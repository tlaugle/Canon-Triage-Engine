# AI-Powered Canon Triage Engine

This project is a volunteer initiative to support the [CyberCanon project](https://www.cybercanon.org/), a nonprofit dedicated to identifying and curating a definitive library of essential cybersecurity books.

---

## Project Status

**Phase:** 1 - Planning & Initial Development

This project is currently in the planning phase. The core logic and data pipeline are being architected.

---

## 1. Mission Statement

To create an automated pipeline that discovers, analyzes, and ranks new cybersecurity books, enabling the CyberCanon review committee to efficiently focus on the most impactful and relevant literature.

## 2. Key Components

* **Automated Discovery:** A scheduled Python script will use the Google Books API to pull a weekly list of new and upcoming publications based on relevant cybersecurity keywords.
* **AI-Powered Triage & Ranking:** An LLM-based agent will process each discovered book. It will enrich the data (e.g., author credibility) and assign a "Priority Score" (1-10) based on topic timeliness, relevance, and author expertise.
* **Triage Report:** The final output will be a simple, ranked report that presents the scored and sorted list of books with a one-sentence justification for each ranking, ready for committee review.

## 3. Technology Stack

* **Core Logic:** Python
* **Data Source:** Google Books API
* **Intelligence:** LLM APIs (e.g., Gemini, OpenAI)
* **Hosting & Collaboration:** Public GitHub Repository

## 4. Next Steps

The immediate next actions for this project are:
1.  Acquire an API key for the Google Books API.
2.  Develop the initial Python script for the "Automated Discovery" component.
3.  Begin prototyping the LLM prompt for the "Triage & Ranking" component.
