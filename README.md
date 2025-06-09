# Bitcoin L2 Research Assistant

A Streamlit application that helps users research Bitcoin Layer 2 (L2) scaling solutions using RAG (Retrieval Augmented Generation).

## Project Structure

The application has been split into multiple components for better maintainability:

```
├── main.py                # Entry point that runs the application
├── app.py                 # Main BitcoinL2RAG class
├── components/
│   ├── __init__.py        # Makes components a proper package
│   ├── ui.py              # UI components and styling
│   ├── rag.py             # RAG components (vector store, embeddings, etc.)
│   └── web_crawler.py     # Web crawling functionality
├── utils.py               # Utility functions
├── requirements.txt       # Dependencies
└── README.md              # This file
```

## Prerequisites

- Python 3.8+
- OpenRouter API key for the LLM
- Ollama running locally with `nomic-embed-text` model for embeddings

## Installation

1. Clone this repository:

```bash
git clone <repository-url>
cd <repository-directory>
```

2. Install the required dependencies:

```bash
pip install -r requirements.txt
```

3. Create a `.env` file in the root directory with your OpenRouter API key:

```
OPENROUTER_API_KEY=your-openrouter-api-key
YOUR_SITE_URL=localhost  # Optional but recommended
YOUR_SITE_NAME=Bitcoin L2 Research Assistant  # Optional but recommended
USER_AGENT=BitcoinL2ResearchAssistant/1.0  # Recommended to identify your requests
```

4. Ensure Ollama is running locally with the required model:

```bash
ollama pull nomic-embed-text
```

## Running the Application

Run the application using Streamlit:

```bash
streamlit run main.py
```

The application will be available at `http://localhost:8501`.

## Data Requirements

Place a CSV file named `data.csv` in the root directory containing Bitcoin L2 information. The application will automatically extract URLs from the CSV and crawl them for additional information.

## Features

- Interactive Q&A about Bitcoin L2 solutions
- Automatic web crawling from URLs found in CSV data
- Semantic search across both structured CSV data and unstructured web content
- Detailed citations and source tracking
- Sample questions for easy exploration 