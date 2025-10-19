#!/usr/bin/env python3
"""
website_graph.analyzer
Refactored website crawler + graph builder with politeness, domain limiting, depth limit,
and export to pyvis Network for interactive visualization.
"""
from urllib.parse import urljoin, urlparse
import time
import requests
from bs4 import BeautifulSoup
from collections import deque
import networkx as nx
from pyvis.network import Network
import logging
import urllib.robotparser

logging.basicConfig(level=logging.INFO)
USER_AGENT = "website-graph-analyzer/1.0 (+https://github.com/yourname)"

def is_valid_scheme(url):
    return urlparse(url).scheme in ("http", "https")

def normalize_url(base, link):
    # Resolve relative URLs and strip fragments
    joined = urljoin(base, link.split('#')[0])
    return joined.rstrip('/')

def extract_links(url, timeout=5):
    try:
        headers = {"User-Agent": USER_AGENT}
        resp = requests.get(url, headers=headers, timeout=timeout)
        resp.raise_for_status()
    except Exception as e:
        logging.debug("Failed to fetch %s: %s", url, e)
        return []
    soup = BeautifulSoup(resp.text, "html.parser")
    links = []
    for a in soup.find_all('a', href=True):
        href = a['href'].strip()
        # skip javascript:, mailto:, tel:, fragments
        if href.startswith(('mailto:', 'javascript:', 'tel:')):
            continue
        links.append(normalize_url(url, href))
    return links

def allowed_by_robots(url):
    try:
        parsed = urlparse(url)
        robots_url = f"{parsed.scheme}://{parsed.netloc}/robots.txt"
        rp = urllib.robotparser.RobotFileParser()
        rp.set_url(robots_url)
        rp.read()
        return rp.can_fetch(USER_AGENT, url)
    except Exception:
        # if robots can't be fetched, be conservative and allow
        return True

def build_website_graph(start_url, max_pages=200, max_depth=2, same_domain=True, delay=0.5):
    """
    Build a directed graph by BFS up to max_pages and max_depth.
    - same_domain restricts crawling to the start_url domain.
    - Returns a networkx.DiGraph
    """
    start_url = normalize_url(start_url, "")
    parsed_start = urlparse(start_url)
    domain = parsed_start.netloc

    G = nx.DiGraph()
    seen = set([start_url])
    q = deque([(start_url, 0)])
    pages_crawled = 0

    while q and pages_crawled < max_pages:
        url, depth = q.popleft()
        if depth > max_depth:
            continue
        if not allowed_by_robots(url):
            logging.info("Blocked by robots.txt: %s", url)
            continue
        try:
            links = extract_links(url)
        except Exception as e:
            logging.debug("Error extracting links from %s: %s", url, e)
            links = []
        pages_crawled += 1
        G.add_node(url)
        for link in links:
            if not is_valid_scheme(link):
                continue
            if same_domain and urlparse(link).netloc != domain:
                continue
            G.add_edge(url, link)
            if link not in seen and depth + 1 <= max_depth and pages_crawled < max_pages:
                seen.add(link)
                q.append((link, depth + 1))
        time.sleep(delay)
    return G

def classify_graph(G):
    if G.is_directed():
        # For DiGraph, use weak/strong connectivity checks on underlying graphs when sensible
        try:
            if nx.is_strongly_connected(G):
                return "Strongly Connected Directed Graph"
            elif nx.is_weakly_connected(G):
                return "Weakly Connected Directed Graph"
            else:
                return "Disconnected Directed Graph"
        except nx.NetworkXError:
            return "Directed Graph (connectivity not determined)"
    else:
        if len(G) == 0:
            return "Empty Graph"
        if nx.is_connected(G.to_undirected()):
            if nx.is_tree(G.to_undirected()):
                return "Tree"
            elif nx.is_bipartite(G.to_undirected()):
                return "Bipartite Connected Graph"
            else:
                return "Connected Graph"
        else:
            if nx.cycle_basis(G.to_undirected()):
                return "Cyclic Graph"
            else:
                return "Acyclic Graph"

def graph_stats(G):
    n = G.number_of_nodes()
    m = G.number_of_edges()
    avg_deg = sum(dict(G.degree()).values()) / n if n else 0
    classification = classify_graph(G)
    return {
        "classification": classification,
        "nodes": n,
        "edges": m,
        "average_degree": avg_deg
    }

def to_pyvis(G, notebook=False, height="750px", width="100%"):
    """
    Convert networkx graph to a pyvis Network and return it (not saved).
    """
    net = Network(height=height, width=width, directed=G.is_directed())
    # transfer nodes and edges
    for n in G.nodes():
        # shorten label for readability
        label = n if len(n) <= 60 else n[:57] + "..."
        net.add_node(n, label=label, title=n)
    for u, v in G.edges():
        net.add_edge(u, v)
    net.toggle_physics(True)
    return net

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Build a website graph.")
    parser.add_argument("url")
    parser.add_argument("--max-pages", type=int, default=200)
    parser.add_argument("--max-depth", type=int, default=2)
    parser.add_argument("--same-domain", action="store_true", help="Restrict crawling to start domain")
    args = parser.parse_args()
    G = build_website_graph(args.url, max_pages=args.max_pages, max_depth=args.max_depth, same_domain=args.same_domain)
    stats = graph_stats(G)
    print("Graph stats:", stats)
    # optional: save pyvis html
    net = to_pyvis(G)
    net.show("graph.html")
