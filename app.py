#!/usr/bin/env python3
"""
Streamlit app to demo the website graph analyzer.
Run with: streamlit run app.py
"""
import streamlit as st
from website_graph.analyzer import build_website_graph, graph_stats, to_pyvis
import tempfile
import os
import streamlit.components.v1 as components

st.set_page_config(page_title="Website Graph Analyzer", layout="wide")

st.title("Website Graph Analyzer")
st.write("Enter a starting URL and visualize the site's link graph. Use depth and limits to keep crawling safe.")

with st.form("crawl_form"):
    start_url = st.text_input("Start URL", value="https://example.com")
    max_pages = st.slider("Max pages", 10, 1000, 200, step=10)
    max_depth = st.slider("Max depth", 1, 4, 2)
    same_domain = st.checkbox("Restrict to same domain", value=True)
    delay = st.slider("Delay between requests (seconds)", 0.0, 2.0, 0.5, step=0.1)
    submit = st.form_submit_button("Analyze")

if submit:
    with st.spinner("Crawling and building graph… (be patient)"):
        G = build_website_graph(start_url, max_pages=max_pages, max_depth=max_depth, same_domain=same_domain, delay=delay)
        stats = graph_stats(G)
    st.subheader("Graph Metrics")
    st.json(stats)

    if G.number_of_nodes() == 0:
        st.warning("No nodes found — check the URL or increase max pages/depth.")
    else:
        st.subheader("Interactive Graph (pyvis)")
        net = to_pyvis(G, height="700px")
        # save to a temporary HTML file and embed
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".html")
        tmp_path = tmp.name
        tmp.close()
        net.show(tmp_path)
        html = open(tmp_path, "r", encoding="utf-8").read()
        components.html(html, height=700, scrolling=True)
        try:
            os.remove(tmp_path)
        except Exception:
            pass

    st.info("Tip: try small sites first (low depth). To showcase on GitHub, deploy this app to Streamlit Community Cloud and link from your README.")
