# canon_triage_engine.py

import os
import json
import requests
import google.generativeai as genai
from datetime import datetime, timedelta
from dateutil.parser import parse as parse_date
from typing import List, Dict, Any

# --- Configuration ---
# Search keywords for the Google Books API
KEYWORDS: List[str] = [
    'cybersecurity',
    'AI security',
    'threat intelligence',
    'network security',
    'cloud security',
    'incident response'
]

# Timeframe in months to filter for newly published books
PUBLICATION_TIMEFRAME_MONTHS: int = 12

# --- FIX: Set default LLM provider to LOCAL to avoid Gemini key error ---
LLM_PROVIDER: str = 'LOCAL' 

# --- Local LLM (Ollama) Configuration ---
LOCAL_LLM_ENDPOINT: str = 'http://localhost:11434/v1/chat/completions'
LOCAL_LLM_MODEL: str = 'llama3'

# --- Security: Load API keys from environment variables ---
try:
    GOOGLE_BOOKS_API_KEY: str = os.environ['GOOGLE_BOOKS_API_KEY']
except KeyError:
    print(f"🛑 Error: Environment variable 'GOOGLE_BOOKS_API_KEY' not set. Please set your API key.")
    exit(1)

# Conditionally load the Gemini key only if the provider is 'GEMINI'
GEMINI_API_KEY: str = ""
if LLM_PROVIDER == 'GEMINI':
    try:
        GEMINI_API_KEY = os.environ['GEMINI_API_KEY']
    except KeyError:
        print(f"🛑 Error: LLM_PROVIDER is 'GEMINI' but 'GEMINI_API_KEY' is not set.")
        exit(1)

# --- LLM Triage Prompt Template ---
TRIAGE_PROMPT_TEMPLATE: str = """
You are a senior cybersecurity professional serving on the CyberCanon book review committee. Your task is to assign a Priority Score to the following book to determine if it's worth the committee's immediate attention.

Provide a "Priority Score" from 1 (low) to 10 (high) and a single sentence "Reasoning".

Base your score on these criteria:
- Author Credibility: Is the author a known practitioner, researcher, or leader in the field?
- Topic Timeliness: Is the subject cutting-edge and highly relevant right now (e.g., Securing GenAI, Cloud Security Posture)?
- Practicality: Does the description suggest a hands-on, practical guide for professionals?

Respond ONLY in a valid JSON format with the keys "priority_score" (as an integer) and "reasoning" (as a string).

[Book Data]
Title: {book_title}
Author(s): {book_authors}
Description: {book_description}
"""

# MODIFICATION: Changed function signature to accept timeframe_months
def discover_books(api_key: str, keywords: List[str], max_results: int, timeframe_months: int) -> List[Dict[str, Any]]:
    """
    Discovers newly published books from the Google Books API based on keywords.

    Args:
        api_key: The API key for the Google Books API.
        keywords: A list of search terms.
        max_results: The maximum number of results to fetch per keyword.
        timeframe_months: How many months back to search for new books.

    Returns:
        A de-duplicated list of book data dictionaries.
    """
    print(f"🔎 Discovering books using {len(keywords)} keywords (up to {max_results} results per keyword)...")
    unique_books = {}
    
    # MODIFICATION: Use timeframe_months to calculate the cutoff date
    cutoff_date = datetime.now() - timedelta(days=timeframe_months * 30)
    
    for keyword in keywords:
        try:
            params = {
                'q': keyword,
                'orderBy': 'newest',
                'maxResults': max_results,
                'key': api_key
            }
            response = requests.get("https://www.googleapis.com/books/v1/volumes", params=params)
            response.raise_for_status()
            data = response.json()

            if 'items' not in data:
                continue

            for item in data['items']:
                book_id = item.get('id')
                volume_info = item.get('volumeInfo', {})
                published_str = volume_info.get('publishedDate')

                if not book_id or not published_str:
                    continue

                try:
                    publication_date = parse_date(published_str).replace(tzinfo=None)
                    if publication_date >= cutoff_date:
                        if book_id not in unique_books:
                            unique_books[book_id] = {
                                'id': book_id,
                                'title': volume_info.get('title', 'N/A'),
                                'authors': ", ".join(volume_info.get('authors', ['N/A'])),
                                'published_date': published_str,
                                'description': volume_info.get('description', 'No description available.')
                            }
                except (ValueError, TypeError):
                    continue
        except requests.exceptions.RequestException as e:
            print(f"⚠️  Could not fetch books for keyword '{keyword}': {e}")

    print(f"✅ Found {len(unique_books)} unique books published in the last {timeframe_months} months.")
    return list(unique_books.values())


def triage_books_with_ai(books: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Analyzes and scores a list of books using the configured LLM provider.

    Args:
        books: A list of book data dictionaries.

    Returns:
        The same list, enriched with 'priority_score' and 'reasoning'.
    """
    print(f"🧠 Triaging {len(books)} books with LLM provider: {LLM_PROVIDER}...")
    scored_books = []

    if LLM_PROVIDER == 'GEMINI':
        genai.configure(api_key=GEMINI_API_KEY)
        model = genai.GenerativeModel('gemini-pro')

    for i, book in enumerate(books):
        print(f"   - Processing book {i+1}/{len(books)}: {book['title'][:50]}...")
        prompt = TRIAGE_PROMPT_TEMPLATE.format(
            book_title=book['title'],
            book_authors=book['authors'],
            book_description=book.get('description', 'N/A')
        )
        
        try:
            if LLM_PROVIDER == 'GEMINI':
                response = model.generate_content(
                    prompt,
                    generation_config={"response_mime_type": "application/json"}
                )
                analysis = json.loads(response.text)
            
            elif LLM_PROVIDER == 'LOCAL':
                payload = {
                    "model": LOCAL_LLM_MODEL,
                    "messages": [{"role": "user", "content": prompt}],
                    "response_format": {"type": "json_object"}
                }
                headers = {"Content-Type": "application/json"}
                response = requests.post(LOCAL_LLM_ENDPOINT, json=payload, headers=headers)
                response.raise_for_status()
                response_content = response.json()['choices'][0]['message']['content']
                analysis = json.loads(response_content)

            else:
                raise ValueError(f"Unknown LLM_PROVIDER: {LLM_PROVIDER}")

            book['priority_score'] = int(analysis.get('priority_score', 0))
            book['reasoning'] = analysis.get('reasoning', 'Error in analysis.')
            scored_books.append(book)

        except (requests.exceptions.RequestException, json.JSONDecodeError, ValueError, IndexError, KeyError) as e:
            print(f"   - ⚠️  Failed to triage book '{book['title']}': {e}")
            book['priority_score'] = 0
            book['reasoning'] = f"AI Triage Failed: {str(e)}"
            scored_books.append(book)
            
    print("✅ Triage complete.")
    return scored_books


def generate_report(scored_books: List[Dict[str, Any]]):
    """
    Generates a Markdown report from the scored list of books.

    Args:
        scored_books: A list of book dictionaries with triage scores.
    """
    print("✍️ Generating Markdown report...")
    scored_books.sort(key=lambda x: x.get('priority_score', 0), reverse=True)

    markdown_content = ["# 📚 CyberCanon Triage Report\n\n"]
    markdown_content.append(f"Report generated on: **{datetime.now().strftime('%Y-%m-%d')}**\n\n")
    
    markdown_content.append("| Priority | Title | Author(s) | Reasoning |\n")
    markdown_content.append("|---:|---|---|---|\n")

    for book in scored_books:
        title = book.get('title', 'N/A').replace('|', r'\|')
        authors = book.get('authors', 'N/A').replace('|', r'\|')
        reasoning = book.get('reasoning', 'N/A').replace('|', r'\|')
        score = book.get('priority_score', 0)
        
        markdown_content.append(f"| **{score}** | {title} | {authors} | {reasoning} |\n")

    try:
        with open("triage_report.md", "w", encoding="utf-8") as f:
            f.writelines(markdown_content)
        print("✅ Report successfully generated: triage_report.md")
    except IOError as e:
        print(f"🛑 Error writing report to file: {e}")


def save_books_to_json(books: List[Dict[str, Any]], filename: str):
    """Saves a list of book dictionaries to a JSON file."""
    print(f"💾 Saving {len(books)} discovered books to {filename}...")
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(books, f, indent=4, ensure_ascii=False)
        print(f"✅ Successfully saved books to {filename}")
    except IOError as e:
        print(f"🛑 Error saving books to file: {e}")


def main():
    """
    Main function to orchestrate the book discovery, triage, and reporting process.
    """
    print("--- Canon Triage Engine Initializing ---")
    
    # --- NEW FEATURE: Get user input for publication timeframe ---
    timeframe_months = PUBLICATION_TIMEFRAME_MONTHS
    while True:
        try:
            user_input = input(f"Enter publication timeframe in months [default: {timeframe_months}]: ")
            if not user_input:
                break # Keep the default
            
            num_input = int(user_input)
            if num_input > 0:
                timeframe_months = num_input
                break
            else:
                print("🛑 Please enter a positive number.")
        except ValueError:
            print("🛑 Invalid input. Please enter a whole number.")

    # Get user input for max results
    max_results = 20
    while True:
        try:
            user_input = input(f"Enter number of results per keyword to fetch [default: {max_results}]: ")
            if not user_input:
                break # Keep the default
            
            num_input = int(user_input)
            if num_input > 0 and num_input <= 40: # Google Books API max is 40
                max_results = num_input
                break
            else:
                print("🛑 Please enter a number between 1 and 40.")
        except ValueError:
            print("🛑 Invalid input. Please enter a whole number.")

    # Step 1: Discover books, passing the user-defined limits
    # MODIFICATION: Pass timeframe_months to the function call
    discovered_books = discover_books(GOOGLE_BOOKS_API_KEY, KEYWORDS, max_results, timeframe_months)
    
    if not discovered_books:
        print("No new books found. Exiting.")
        return

    # NEW STEP: Save the discovered books to a file
    save_books_to_json(discovered_books, "discovered_books.json")

    # Step 2: Triage with AI
    scored_books = triage_books_with_ai(discovered_books)
    
    # Step 3: Generate report
    generate_report(scored_books)
    
    print("--- Canon Triage Engine Finished ---")


if __name__ == "__main__":
    main()
