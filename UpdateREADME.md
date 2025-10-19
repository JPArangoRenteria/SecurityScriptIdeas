# Website Graph Analyzer

A small tool that crawls a website and builds a link graph, classifies it, and visualizes it interactively.

Live demo: (deploy the `app.py` to Streamlit Community Cloud and paste the link here)

## Features
- Polite crawling with user agent and optional robots.txt respect
- Domain-restricted crawling
- Configurable max pages and depth
- Graph metrics and classification
- Interactive visualization using pyvis (exported to an HTML widget)
- Streamlit app for easy demos

## Quickstart (local)
1. Clone the repo and install dependencies:
   pip install -r requirements.txt

2. Run the Streamlit demo:
   streamlit run app.py

3. Or use the analyzer as a script:
   python -m website_graph.analyzer https://example.com --max-pages 100 --max-depth 2 --same-domain
