#!/usr/bin/env python3
"""
Deep Research Tool - Automated expert-level research on any topic
Usage: python research_topic.py "your topic here"
"""

import sys
import os
import re
import hashlib
from datetime import datetime

# Auto-install dependencies
try:
    from ddgs import DDGS
except ImportError:
    os.system("pip install -q ddgs")
    from ddgs import DDGS

try:
    import requests
    from bs4 import BeautifulSoup
except ImportError:
    os.system("pip install -q requests beautifulsoup4")
    import requests
    from bs4 import BeautifulSoup

import warnings
warnings.filterwarnings("ignore")


def generate_search_queries(topic: str) -> list:
    """Generate varied search queries to cover different angles of the topic."""
    base_queries = [
        f"{topic}",
        f"{topic} explained",
        f"{topic} overview fundamentals",
        f"{topic} how it works",
        f"{topic} key concepts principles",
        f"{topic} latest developments",
        f"{topic} applications use cases",
        f"{topic} advantages benefits",
        f"{topic} challenges limitations",
        f"{topic} expert guide",
    ]
    return base_queries[:10]


def search_web(query: str, max_results: int = 5) -> list:
    """Perform web search and return results."""
    try:
        ddgs = DDGS()
        results = list(ddgs.text(query, max_results=max_results))
        return results
    except Exception as e:
        print(f"  ⚠️ Search error for '{query[:30]}...': {e}")
        return []


def extract_content(url: str, timeout: int = 10) -> str:
    """Extract main text content from a URL."""
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
        response = requests.get(url, headers=headers, timeout=timeout)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")

        # Remove script, style, nav, footer elements
        for tag in soup(["script", "style", "nav", "footer", "header", "aside", "form", "noscript"]):
            tag.decompose()

        # Try to find main content areas
        main_content = soup.find("main") or soup.find("article") or soup.find("div", class_=re.compile(r"content|main|article|post", re.I))

        if main_content:
            text = main_content.get_text(separator=" ", strip=True)
        else:
            text = soup.get_text(separator=" ", strip=True)

        # Clean up whitespace
        text = re.sub(r"\s+", " ", text)
        return text[:6000]  # Limit content length

    except Exception as e:
        return ""


def synthesize_research(topic: str, sources: list) -> str:
    """Synthesize collected information into expert-level content."""

    # Collect all content
    all_content = []
    for source in sources:
        if source.get("content"):
            all_content.append({
                "title": source.get("title", ""),
                "url": source.get("url", ""),
                "snippet": source.get("snippet", ""),
                "content": source.get("content", "")
            })

    # Build comprehensive report
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")

    report = f"""# Deep Research Report: {topic}

**Generated:** {timestamp}  
**Sources Analyzed:** {len(all_content)}

---

## Executive Summary

This report provides expert-level analysis of **{topic}** based on comprehensive research across {len(all_content)} authoritative sources.

---

## Key Information & Findings

"""

    # Extract and organize key information from sources
    seen_info = set()
    key_points = []

    for source in all_content[:15]:
        content = source.get("content", "")
        snippet = source.get("snippet", "")

        combined = f"{snippet} {content[:2000]}"

        # Extract informative sentences
        sentences = re.split(r"(?<=[.!?])\s+", combined)
        for sent in sentences:
            sent = sent.strip()
            if len(sent) > 60 and len(sent) < 350:
                topic_words = topic.lower().split()
                if any(word in sent.lower() for word in topic_words if len(word) > 3):
                    sent_hash = hashlib.md5(sent[:60].encode()).hexdigest()
                    if sent_hash not in seen_info:
                        seen_info.add(sent_hash)
                        key_points.append(sent)

    # Add key points as bullet list
    for point in key_points[:25]:
        clean_point = point.strip()
        if not clean_point.endswith('.'):
            clean_point += '.'
        report += f"- {clean_point}\n"

    report += "\n---\n\n## Detailed Source Analysis\n\n"

    # Add detailed sections from top sources
    for i, source in enumerate(all_content[:10], 1):
        title = source.get("title", "Source")
        content = source.get("content", "")[:1000]
        url = source.get("url", "")

        if content:
            report += f"### {i}. {title}\n\n"
            report += f"{content}...\n\n"
            report += f"*Source: {url}*\n\n"

    # Add source references
    report += "---\n\n## All Source References\n\n"
    for i, source in enumerate(all_content, 1):
        title = source.get("title", "Unknown")
        url = source.get("url", "")
        report += f"{i}. [{title}]({url})\n"

    return report


def deep_research(topic: str) -> str:
    """Main research function."""
    print(f"\n🔬 Starting Deep Research on: {topic}")
    print("=" * 60)

    # Generate search queries
    queries = generate_search_queries(topic)
    print(f"\n📋 Generated {len(queries)} search queries")

    # Collect all search results
    all_results = []
    seen_urls = set()

    for i, query in enumerate(queries, 1):
        print(f"\n🔍 Search {i}/{len(queries)}: {query[:50]}...")
        results = search_web(query, max_results=5)

        for r in results:
            url = r.get("href", r.get("link", ""))
            if url and url not in seen_urls:
                seen_urls.add(url)
                all_results.append({
                    "url": url,
                    "title": r.get("title", ""),
                    "snippet": r.get("body", r.get("snippet", "")),
                    "content": ""
                })
        print(f"   Found {len(results)} results ({len(seen_urls)} unique total)")

    print(f"\n📚 Total unique sources found: {len(all_results)}")

    # Extract content from top sources
    print(f"\n📖 Extracting content from sources...")
    sources_with_content = 0
    max_sources = min(20, len(all_results))

    for i, source in enumerate(all_results[:max_sources]):
        url = source["url"]
        print(f"   [{i+1}/{max_sources}] Fetching: {url[:55]}...")
        content = extract_content(url)
        if content:
            source["content"] = content
            sources_with_content += 1

    print(f"\n✅ Successfully extracted content from {sources_with_content} sources")

    # Synthesize research
    print(f"\n📝 Synthesizing research report...")
    report = synthesize_research(topic, all_results)

    # Save report
    safe_topic = re.sub(r"[^a-zA-Z0-9]+", "_", topic)[:50].strip("_")
    report_path = f"/a0/tmp/research_{safe_topic}.md"

    with open(report_path, "w", encoding="utf-8") as f:
        f.write(report)

    print(f"\n💾 Full report saved to: {report_path}")
    print("\n" + "=" * 60)

    return report


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python research_topic.py \"your topic here\"")
        sys.exit(1)

    topic = " ".join(sys.argv[1:])
    report = deep_research(topic)

    # Print summary (first ~80 lines for ~1 page)
    lines = report.split("\n")
    summary_lines = lines[:80]
    print("\n" + "\n".join(summary_lines))

    if len(lines) > 80:
        print(f"\n... [Full report saved to file - see path above]")
