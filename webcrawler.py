#!/usr/bin/env python

import sys
import requests
from bs4 import BeautifulSoup
import networkx as nx
import matplotlib.pyplot as plt

# Function to extract links from a webpage
def extract_links(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    links = []
    for link in soup.find_all('a', href=True):
        links.append(link['href'])
    return links

def build_website_graph_dfs(start_url, visited, graph):
    if start_url in visited:
        return
    visited.add(start_url)
    links = extract_links(start_url)
    for link in links:
        graph.add_edge(start_url, link)
        build_website_graph_dfs(link, visited, graph)

# Function to build the website graph
def build_website_graph(start_url):
    graph = nx.Graph()
    visited = set()
    build_website_graph_dfs(start_url, visited, graph)
    return graph

def classify_graph(G):
    is_directed = nx.is_directed(G)
    is_connected = nx.is_connected(G)
    is_bipartite = nx.is_bipartite(G)
    is_tree = nx.is_tree(G)
    is_cyclic = len(nx.cycle_basis(G)) > 0
    
    # Define classification rules
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
        return "Acylical Graph"

def graph_stats(G):
    classification = classify_graph(G)
    metrics_table = [("Metric", "Value")]
    metrics_table.append(("Number of Nodes", len(G.nodes)))
    metrics_table.append(("Number of Edges", len(G.edges)))
    metrics_table.append(("Average Degree", sum(dict(G.degree()).values()) / len(G.nodes)))
    return classification, metrics_table

def visualize_graph(G):
    plt.figure(figsize=(10, 10))
    pos = nx.spring_layout(G)
    nx.draw(G, pos, with_labels=True, node_color='skyblue', node_size=1500, edge_color='black', linewidths=1, font_size=10)
    plt.title("Website Graph")
    plt.show()

def analyze_website(url):
    website_graph = build_website_graph(url)
    visualize_graph(website_graph)
    classification, metrics_table = graph_stats(website_graph)
    print("Graph Classification:", classification)
    print("Graph Metrics:")
    for metric, value in metrics_table:
        print(metric + ":", value)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: website_graph_analyzer.py <url>")
        sys.exit(1)
    start_url = sys.argv[1]
    analyze_website(start_url)

