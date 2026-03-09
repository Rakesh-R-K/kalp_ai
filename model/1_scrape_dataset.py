"""
STEP 1: CTF/Security Dataset Scraper
=====================================
Scrapes CTF writeups and security content from:
- GitHub CTF writeup repositories
- HackTricks GitBook
- PortSwigger Web Academy

Run this LOCALLY or on Colab before training.

Usage:
    pip install requests beautifulsoup4 trafilatura tqdm
    python 1_scrape_dataset.py
"""

import os
import json
import time
import requests
from bs4 import BeautifulSoup
import trafilatura
from tqdm import tqdm

# ── Config ────────────────────────────────────────────────────────────────────
OUTPUT_DIR = "raw_data"
os.makedirs(OUTPUT_DIR, exist_ok=True)

GITHUB_TOKEN = ""   # Optional: add your token for higher rate limits
                    # Get one free at github.com/settings/tokens

HEADERS = {
    "User-Agent": "Mozilla/5.0 (CTF-Dataset-Builder/1.0)",
    "Accept": "application/json",
}
if GITHUB_TOKEN:
    HEADERS["Authorization"] = f"token {GITHUB_TOKEN}"


# ── 1. GitHub CTF Writeup Scraper ────────────────────────────────────────────
def scrape_github_ctf_writeups(max_repos=50):
    """
    Searches GitHub for popular CTF writeup repositories and
    downloads their README / markdown writeup files.
    """
    print("\n[1/3] Scraping GitHub CTF writeup repos...")

    search_queries = [
        "CTF writeup walkthrough",
        "CTF writeup pwn web crypto",
        "capture the flag writeup solution",
        "hackthebox writeup",
        "tryhackme writeup walkthrough",
    ]

    repo_names = set()
    for query in search_queries:
        url = "https://api.github.com/search/repositories"
        params = {
            "q": query,
            "sort": "stars",
            "order": "desc",
            "per_page": 20,
        }
        try:
            r = requests.get(url, headers=HEADERS, params=params, timeout=10)
            r.raise_for_status()
            for repo in r.json().get("items", []):
                repo_names.add(repo["full_name"])
        except Exception as e:
            print(f"  ⚠ GitHub search error: {e}")
        time.sleep(1.5)  # Respect rate limits

    print(f"  Found {len(repo_names)} unique repos. Fetching markdown files...")

    all_writeups = []
    for repo in tqdm(list(repo_names)[:max_repos], desc="  Repos"):
        # Get file tree
        url = f"https://api.github.com/repos/{repo}/git/trees/HEAD?recursive=1"
        try:
            r = requests.get(url, headers=HEADERS, timeout=10)
            r.raise_for_status()
            tree = r.json().get("tree", [])

            # Find markdown files (writeups are usually .md or README)
            md_files = [
                f["path"] for f in tree
                if f["path"].endswith(".md")
                and f.get("size", 0) > 500       # Skip tiny files
                and f.get("size", 0) < 100_000   # Skip huge files
            ][:10]  # Max 10 files per repo

            for filepath in md_files:
                raw_url = f"https://raw.githubusercontent.com/{repo}/HEAD/{filepath}"
                try:
                    content = requests.get(raw_url, timeout=8).text
                    if len(content) > 200:
                        all_writeups.append({
                            "source": f"github:{repo}/{filepath}",
                            "text": content,
                        })
                except Exception:
                    pass
                time.sleep(0.3)

        except Exception as e:
            pass
        time.sleep(1)

    # Save
    out_path = os.path.join(OUTPUT_DIR, "github_writeups.jsonl")
    with open(out_path, "w") as f:
        for item in all_writeups:
            f.write(json.dumps(item) + "\n")

    print(f"  ✓ Saved {len(all_writeups)} writeups → {out_path}")
    return all_writeups


# ── 2. HackTricks Scraper ─────────────────────────────────────────────────────
def scrape_hacktricks(max_pages=100):
    """
    Scrapes HackTricks GitBook — one of the best free pentesting references.
    Covers: web hacking, privilege escalation, AD attacks, and more.
    """
    print("\n[2/3] Scraping HackTricks...")

    # HackTricks sitemap or known section URLs
    base_urls = [
        "https://book.hacktricks.xyz/pentesting-web/sql-injection",
        "https://book.hacktricks.xyz/pentesting-web/xss-cross-site-scripting",
        "https://book.hacktricks.xyz/pentesting-web/command-injection",
        "https://book.hacktricks.xyz/pentesting-web/file-inclusion",
        "https://book.hacktricks.xyz/pentesting-web/ssrf-server-side-request-forgery",
        "https://book.hacktricks.xyz/pentesting-web/csrf-cross-site-request-forgery",
        "https://book.hacktricks.xyz/pentesting-web/deserialization",
        "https://book.hacktricks.xyz/pentesting-web/xxe-xee-xml-external-entity",
        "https://book.hacktricks.xyz/linux-hardening/privilege-escalation",
        "https://book.hacktricks.xyz/windows-hardening/windows-local-privilege-escalation",
        "https://book.hacktricks.xyz/generic-methodologies-and-resources/reverse-shells/linux",
        "https://book.hacktricks.xyz/generic-methodologies-and-resources/shells/linux",
        "https://book.hacktricks.xyz/network-services-pentesting/pentesting-web",
        "https://book.hacktricks.xyz/network-services-pentesting/pentesting-ssh",
        "https://book.hacktricks.xyz/network-services-pentesting/pentesting-ftp",
        "https://book.hacktricks.xyz/network-services-pentesting/pentesting-smb",
        "https://book.hacktricks.xyz/cryptography/certificates",
        "https://book.hacktricks.xyz/cryptography/hash-cracking",
        "https://book.hacktricks.xyz/forensics/basic-forensic-methodology",
        "https://book.hacktricks.xyz/reversing/reversing-tools-basic-methods",
        "https://book.hacktricks.xyz/exploiting/linux-exploiting-basic-esp",
        "https://book.hacktricks.xyz/exploiting/tools/pwntools",
    ]

    results = []
    for url in tqdm(base_urls, desc="  HackTricks pages"):
        try:
            downloaded = trafilatura.fetch_url(url)
            text = trafilatura.extract(downloaded, include_comments=False,
                                       include_tables=True, no_fallback=False)
            if text and len(text) > 300:
                results.append({
                    "source": f"hacktricks:{url}",
                    "text": text,
                })
        except Exception as e:
            pass
        time.sleep(1.2)

    out_path = os.path.join(OUTPUT_DIR, "hacktricks.jsonl")
    with open(out_path, "w") as f:
        for item in results:
            f.write(json.dumps(item) + "\n")

    print(f"  ✓ Saved {len(results)} pages → {out_path}")
    return results


# ── 3. PortSwigger Web Security Academy ──────────────────────────────────────
def scrape_portswigger(max_pages=40):
    """
    Scrapes PortSwigger Web Security Academy — excellent structured
    explanations of web vulnerabilities with examples.
    """
    print("\n[3/3] Scraping PortSwigger Web Security Academy...")

    topics = [
        "sql-injection", "xss", "csrf", "xxe", "ssrf",
        "os-command-injection", "path-traversal", "access-control",
        "authentication", "websockets", "web-cache-poisoning",
        "insecure-deserialization", "http-request-smuggling",
        "business-logic-vulnerabilities", "clickjacking",
        "cors", "jwt", "oauth", "file-upload-vulnerabilities",
        "race-conditions", "nosql-injection", "api-testing",
        "prototype-pollution", "graphql-api-vulnerabilities",
    ]

    results = []
    base = "https://portswigger.net/web-security"

    for topic in tqdm(topics, desc="  PortSwigger topics"):
        url = f"{base}/{topic}"
        try:
            downloaded = trafilatura.fetch_url(url)
            text = trafilatura.extract(downloaded, include_comments=False,
                                       include_tables=True)
            if text and len(text) > 300:
                results.append({
                    "source": f"portswigger:{topic}",
                    "text": text,
                })
        except Exception:
            pass
        time.sleep(1.5)

    out_path = os.path.join(OUTPUT_DIR, "portswigger.jsonl")
    with open(out_path, "w") as f:
        for item in results:
            f.write(json.dumps(item) + "\n")

    print(f"  ✓ Saved {len(results)} pages → {out_path}")
    return results


# ── Main ──────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("=" * 60)
    print("  CTF/Security Dataset Scraper")
    print("=" * 60)

    github_data   = scrape_github_ctf_writeups(max_repos=50)
    hacktricks    = scrape_hacktricks()
    portswigger   = scrape_portswigger()

    total = len(github_data) + len(hacktricks) + len(portswigger)
    print(f"\n{'='*60}")
    print(f"  ✅ Done! Total documents collected: {total}")
    print(f"  📁 All saved to: ./{OUTPUT_DIR}/")
    print(f"  👉 Next: Run 2_prepare_dataset.py")
    print(f"{'='*60}")
