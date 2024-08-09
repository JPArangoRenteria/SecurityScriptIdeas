#!/usr/bin/env python3

import sys
import requests
from bs4 import BeautifulSoup
import networkx as nx
import matplotlib.pyplot as plt
from urllib.parse import urljoin
from concurrent.futures import ThreadPoolExecutor, as_completed
import time

def extract_links(url):
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        links = [urljoin(url, link['href']) for link in soup.find_all('a', href=True)]
        return links
    except requests.RequestException as e:
        print(f"Request failed for {url}: {e}")
        return []

def fetch_url(url):
    try:
        time.sleep(1)  # Sleep for 1 second between requests
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return url, response.text
    except requests.RequestException as e:
        print(f"Error fetching {url}: {e}")
        return url, None

def build_website_graph_dfs(start_url, visited, graph, depth, max_depth, link_limit, current_links_count, executor, max_workers):
    if start_url in visited or depth > max_depth or current_links_count >= link_limit:
        return
    visited.add(start_url)
    links = extract_links(start_url)
    current_links_count += len(links)
    futures = {executor.submit(fetch_url, link): link for link in links if link not in visited}
    
    for future in as_completed(futures):
        link = futures[future]
        _, content = future.result()
        if content is not None:
            graph.add_edge(start_url, link)
            build_website_graph_dfs(link, visited, graph, depth + 1, max_depth, link_limit, current_links_count, executor, max_workers)

def build_website_graph(start_url, max_depth=2, link_limit=100, max_workers=5):
    graph = nx.Graph()
    visited = set()
    try:
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            build_website_graph_dfs(start_url, visited, graph, 0, max_depth, link_limit, 0, executor, max_workers)
    except KeyboardInterrupt:
        print("Process interrupted by user.")
        return graph, visited
    return graph, visited

def classify_graph(G):
    is_directed = nx.is_directed(G)
    is_connected = nx.is_connected(G)
    is_bipartite = nx.is_bipartite(G)
    is_tree = nx.is_tree(G)
    is_cyclic = len(nx.cycle_basis(G)) > 0
    
    if is_directed:
        if nx.is_strongly_connected(G):
            return "Strongly Connected Directed Graph"
        elif nx.is_weakly_connected(G):
            return "Weakly Connected Directed Graph"
        else:
            return "Disconnected Directed Graph"
    elif is_connected:
        if is_bipartite:
            return "Bipartite Connected Graph"
        elif is_tree:
            return "Tree"
        else:
            return "Connected Forest Graph"
    elif is_cyclic:
        return "Cyclic Graph"
    else:
        return "Acyclical Graph"
def topology_classification(G):
    classifiers = []
    num_nodes = len(G.nodes())
    num_edges = len(G.edges())
    switch = False
    for node,degree in G.degree():
        if degree == num_nodes-1:
            classifiers.append('star')
    for node,degree in G.degree():
        if degree == 2:
            switch = True
        else:
            switch = False
    if switch and (num_edges == num_nodes):
        classifiers.append('ring')
    if num_edges == ((num_nodes)*(num_nodes-1)*0.5):
        classifiers.append('full mesh')
    if num_edges == num_nodes-1:
        classifiers.append('full-tree')


    return
def graph_stats(G):
    classification = classify_graph(G)
    metrics_table = [("Metric", "Value")]
    metrics_table.append(("Number of Nodes", len(G.nodes)))
    metrics_table.append(("Number of Edges", len(G.edges)))
    metrics_table.append(("Average Degree", sum(dict(G.degree()).values()) / len(G.nodes)))
    return classification, metrics_table

def visualize_graph(G, output_file="website_graph.png"):
    plt.figure(figsize=(10, 10))
    pos = nx.spring_layout(G)
    nx.draw(G, pos, with_labels=False, node_color='skyblue', node_size=1500, edge_color='black', linewidths=1, font_size=10)
    plt.title("Website Graph")
    plt.savefig(output_file)
    print(f"Graph saved as {output_file}")


def analyze_website(url):
    website_graph, visited = build_website_graph(url)
    visualize_graph(website_graph)
    classification, metrics_table = graph_stats(website_graph)
    print("Graph Classification:", classification)
    print("Graph Metrics:")
    for metric, value in metrics_table:
        print(f"{metric}: {value}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: website_graph_analyzer.py <url>")
        sys.exit(1)
    start_url = sys.argv[1]
    analyze_website(start_url)
