# AI-Powered Canon Triage Engine

This project is a volunteer initiative to support the [CyberCanon project](https://www.cybercanon.org/), a nonprofit dedicated to identifying and curating a definitive library of essential cybersecurity books.

This tool automates the discovery and initial analysis of new books to help the review committee focus on the most impactful literature.

-----

## Project Status

**Version 1.0 - Functional.** The core engine is a Python script that successfully queries for books, analyzes them with a local LLM or Gemini via API, and generates a report.

-----

## Features

  * Queries the Google Books API for new books based on a configurable list of keywords.
  * Filters results to a user-defined timeframe (e.g., books published in the last 12 months).
  * Uses either a local Ollama LLM instance or Gemini API to analyze each book and assign a review priority score and a qualitative reason for the ranking.
  * Generates a clean, sorted Markdown report (`triage_report.md`) ready for review.

-----

## Technology Stack

  * **Core Logic:** Python 3
  * **Libraries:** `requests`, `python-dotenv`
  * **Data Source:** Google Books API
  * **Intelligence:** Ollama (via OpenAI-compatible API) / Gemini
  * **Hosting:** GitHub

-----

## Setup & Installation

**1. Clone the Repository**

```bash
git clone https://github.com/your-username/Canon-Triage-Engine.git
cd Canon-Triage-Engine
```

**2. Install Dependencies**

```bash
pip install -r requirements.txt
```

**3. Set Up Environment Variables**
Create a file named `.env` in the root of the project folder and add your API key:

```
GOOGLE_BOOKS_API_KEY='your_google_books_api_key_here'
```

**4. Ensure Ollama is Running**
By default this script requires a local or network-accessible Ollama instance. Ensure it is running and you have a model pulled (e.g., `ollama pull llama3`). You can modify the `LOCAL_LLM_ENDPOINT` and `LOCAL_LLM_MODEL` variables in the script to match your setup. If you'd like to use Gemini instead, you can add a Gemini API key to your environment variables and change the LLM in the config to Gemini.

-----

## Usage

1.  Open the main Python script (`main.py` or similar).
2.  Modify the `keywords` list and the `PUBLICATION_TIMEFRAME_MONTHS` variable to fit your needs.
3.  Run the script from your terminal:
    ```bash
    python main.py
    ```
4.  Once the script is finished, a `triage_report.md` file will be created in the project directory with the results.

-----

## Example Output

| Priority | Title | Author(s) | Reasoning |
|---:|---|---|---:|
| **9** | Navigating the Intersection of Artificial Intelligence, Security, and Ethical Governance | Reza Montasari, et al. | This book possesses high timeliness due to its focus on the critical intersection of AI, security, and ethical governance...warranting immediate committee attention. |
| **8** | AI Security | Kai Turing, AI | This book addresses a timely and critical topic – AI’s role in security, particularly within online assessments...justifying a high priority for review. |

-----

## Roadmap

  * Add support for more data sources (e.g., publisher websites).
  * Develop a simple web UI for easier interaction.
  * Allow for more complex, user-defined ranking criteria.
