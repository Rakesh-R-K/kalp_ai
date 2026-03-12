"""
CTF/Security Dataset Scraper — FULL VERSION
=============================================
All sources in one script:
  1.  GitHub CTF Writeup Repos
  2.  HackTheBox Writeups
  3.  TryHackMe Writeups
  4.  HackTricks GitBook
  5.  PayloadsAllTheThings
  6.  SecLists Docs
  7.  PortSwigger Web Security Academy
  8.  Linux Tool Docs (tldr + man pages)
  9.  PwnTools Documentation
  10. OWASP CheatSheet Series
  11. Exploit-DB Papers
  12. HuggingFace Security Datasets

Usage:
    pip install requests beautifulsoup4 trafilatura tqdm datasets
    python 1_scrape_dataset.py
"""

import os
import json
import time
import re
import requests
import subprocess
from tqdm import tqdm

# ┌─────────────────────────────────────────────────────────────────┐
# │  !! PASTE YOUR GITHUB TOKEN HERE !!                             │
# │  github.com → Settings → Developer Settings →                  │
# │  Personal Access Tokens → Tokens (classic) → Generate          │
# │  Scopes needed: tick only "public_repo"                         │
# └─────────────────────────────────────────────────────────────────┘
GITHUB_TOKEN = ""   # e.g. "ghp_xxxxxxxxxxxxxxxxxxxx"


# ── Config ────────────────────────────────────────────────────────────────────
OUTPUT_DIR    = "raw_data"
REQUEST_DELAY = 1.2   # Seconds between requests
os.makedirs(OUTPUT_DIR, exist_ok=True)

HEADERS = {"User-Agent": "Mozilla/5.0 (CTF-Dataset-Builder/1.0)"}
if GITHUB_TOKEN:
    HEADERS["Authorization"] = f"token {GITHUB_TOKEN}"
    print("✅ GitHub token loaded — rate limit: 5,000 req/hr")
else:
    print("⚠️  No GitHub token — rate limit: 60 req/hr (will likely fail)")
    print("   Add your token to GITHUB_TOKEN at the top of this script!\n")


# ── Helpers ───────────────────────────────────────────────────────────────────
def save_jsonl(data: list, filename: str):
    path = os.path.join(OUTPUT_DIR, filename)
    with open(path, "w", encoding="utf-8") as f:
        for item in data:
            f.write(json.dumps(item, ensure_ascii=False) + "\n")
    print(f"  ✓ Saved {len(data):>5} docs → {path}")
    return path


def fetch_url_text(url: str) -> str | None:
    """Fetch and extract clean text from a URL using trafilatura."""
    try:
        import trafilatura
        downloaded = trafilatura.fetch_url(url)
        text = trafilatura.extract(
            downloaded,
            include_comments=False,
            include_tables=True,
            no_fallback=False,
        )
        return text if text and len(text) > 200 else None
    except Exception:
        return None


def github_search_repos(query: str, max_results: int = 30) -> list:
    """Search GitHub for repos matching a query."""
    url = "https://api.github.com/search/repositories"
    params = {
        "q": query,
        "sort": "stars",
        "order": "desc",
        "per_page": min(max_results, 30),
    }
    try:
        r = requests.get(url, headers=HEADERS, params=params, timeout=10)
        r.raise_for_status()
        return [repo["full_name"] for repo in r.json().get("items", [])]
    except Exception as e:
        print(f"    ⚠ GitHub search error for '{query}': {e}")
        return []


def get_markdown_files(repo: str, max_files: int = 20) -> tuple:
    """Get markdown files from a repo. Tries HEAD, master, main."""
    for branch in ["HEAD", "master", "main"]:
        url = f"https://api.github.com/repos/{repo}/git/trees/{branch}?recursive=1"
        try:
            r = requests.get(url, headers=HEADERS, timeout=12)
            if r.status_code == 200:
                tree = r.json().get("tree", [])
                files = [
                    f["path"] for f in tree
                    if f["path"].lower().endswith(".md")
                    and 200 < f.get("size", 0) < 200_000
                ][:max_files]
                if files:
                    return files, branch
        except Exception:
            pass
        time.sleep(0.5)
    return [], "master"


def fetch_raw(repo: str, branch: str, filepath: str) -> str | None:
    """Fetch raw file content from GitHub."""
    url = f"https://raw.githubusercontent.com/{repo}/{branch}/{filepath}"
    try:
        r = requests.get(url, timeout=10)
        if r.status_code == 200 and len(r.text) > 200:
            return r.text
    except Exception:
        pass
    return None


def scrape_repo_markdowns(repo: str, max_files: int = 20,
                           source_prefix: str = "github",
                           category: str = "ctf_writeup") -> list:
    """Generic: scrape all markdown files from a repo."""
    files, branch = get_markdown_files(repo, max_files)
    results = []
    for filepath in files:
        content = fetch_raw(repo, branch, filepath)
        if content and len(content) > 300:
            results.append({
                "source": f"{source_prefix}:{repo}/{filepath}",
                "text": content,
                "category": category,
            })
        time.sleep(0.3)
    return results


# ── 1. GitHub CTF Writeups ────────────────────────────────────────────────────
def scrape_github_ctf_writeups(max_repos: int = 150):
    print("\n[1/12] GitHub CTF Writeup Repos...")

    queries = [
        "CTF writeup walkthrough solution",
        "capture the flag writeup",
        "ctf-writeups collection",
        "hackthebox writeup walkthrough",
        "tryhackme writeup solution",
        "picoctf writeup solution",
        "pwnable writeup",
        "overthewire writeup",
        "CTF pwn binary exploitation writeup",
        "CTF web exploitation writeup",
        "CTF cryptography writeup solution",
        "CTF forensics writeup solution",
        "CTF reverse engineering writeup",
        "CTF steganography writeup",
        "DEF CON CTF writeup",
        "Google CTF writeup",
        "CSAW CTF writeup",
        "CTF OSINT writeup",
        "ctftime writeup",
        "plaidCTF writeup",
    ]

    all_repos = set()
    for query in tqdm(queries, desc="  Searching GitHub"):
        repos = github_search_repos(query, max_results=20)
        all_repos.update(repos)
        time.sleep(REQUEST_DELAY)

    print(f"  Found {len(all_repos)} unique repos")

    results = []
    for repo in tqdm(list(all_repos)[:max_repos], desc="  Fetching files"):
        results.extend(scrape_repo_markdowns(repo, max_files=20,
                                              source_prefix="github_ctf",
                                              category="ctf_writeup"))
        time.sleep(0.8)

    save_jsonl(results, "github_ctf_writeups.jsonl")
    return results


# ── 2. HackTheBox Writeups ────────────────────────────────────────────────────
def scrape_htb_writeups(max_repos: int = 80):
    print("\n[2/12] HackTheBox Writeups...")

    queries = [
        "hackthebox machine writeup retired",
        "htb writeup walkthrough",
        "hackthebox penetration test writeup",
        "htb machine pwned writeup",
        "hackthebox write-up solution",
    ]

    all_repos = set()
    for query in tqdm(queries, desc="  Searching"):
        repos = github_search_repos(query, max_results=25)
        all_repos.update(repos)
        time.sleep(REQUEST_DELAY)

    print(f"  Found {len(all_repos)} repos")

    results = []
    for repo in tqdm(list(all_repos)[:max_repos], desc="  Fetching HTB writeups"):
        results.extend(scrape_repo_markdowns(repo, max_files=15,
                                              source_prefix="htb_writeup",
                                              category="htb_writeup"))
        time.sleep(0.8)

    save_jsonl(results, "htb_writeups.jsonl")
    return results


# ── 3. TryHackMe Writeups ─────────────────────────────────────────────────────
def scrape_thm_writeups(max_repos: int = 60):
    print("\n[3/12] TryHackMe Writeups...")

    queries = [
        "tryhackme room writeup walkthrough",
        "thm writeup solution",
        "tryhackme learning path writeup",
        "tryhackme write-up flags",
    ]

    all_repos = set()
    for query in tqdm(queries, desc="  Searching"):
        repos = github_search_repos(query, max_results=20)
        all_repos.update(repos)
        time.sleep(REQUEST_DELAY)

    print(f"  Found {len(all_repos)} repos")

    results = []
    for repo in tqdm(list(all_repos)[:max_repos], desc="  Fetching THM writeups"):
        results.extend(scrape_repo_markdowns(repo, max_files=15,
                                              source_prefix="thm_writeup",
                                              category="thm_writeup"))
        time.sleep(0.8)

    save_jsonl(results, "thm_writeups.jsonl")
    return results


# ── 4. HackTricks ─────────────────────────────────────────────────────────────
def scrape_hacktricks():
    print("\n[4/12] HackTricks GitBook...")

    urls = [
        # Web exploitation
        "https://book.hacktricks.xyz/pentesting-web/sql-injection",
        "https://book.hacktricks.xyz/pentesting-web/xss-cross-site-scripting",
        "https://book.hacktricks.xyz/pentesting-web/command-injection",
        "https://book.hacktricks.xyz/pentesting-web/file-inclusion",
        "https://book.hacktricks.xyz/pentesting-web/ssrf-server-side-request-forgery",
        "https://book.hacktricks.xyz/pentesting-web/csrf-cross-site-request-forgery",
        "https://book.hacktricks.xyz/pentesting-web/deserialization",
        "https://book.hacktricks.xyz/pentesting-web/xxe-xee-xml-external-entity",
        "https://book.hacktricks.xyz/pentesting-web/web-cache-poisoning",
        "https://book.hacktricks.xyz/pentesting-web/jwt-vulnerabilities",
        "https://book.hacktricks.xyz/pentesting-web/oauth-to-account-takeover",
        "https://book.hacktricks.xyz/pentesting-web/nosql-injection",
        "https://book.hacktricks.xyz/pentesting-web/graphql",
        "https://book.hacktricks.xyz/pentesting-web/http-request-smuggling",
        "https://book.hacktricks.xyz/pentesting-web/race-condition",
        "https://book.hacktricks.xyz/pentesting-web/cors-bypass",
        "https://book.hacktricks.xyz/pentesting-web/clickjacking",
        "https://book.hacktricks.xyz/pentesting-web/open-redirect",
        "https://book.hacktricks.xyz/pentesting-web/server-side-template-injection",
        # Linux
        "https://book.hacktricks.xyz/linux-hardening/privilege-escalation",
        "https://book.hacktricks.xyz/linux-hardening/privilege-escalation/interesting-groups-linux-pe",
        "https://book.hacktricks.xyz/linux-hardening/privilege-escalation/docker-security",
        "https://book.hacktricks.xyz/linux-hardening/useful-linux-commands",
        "https://book.hacktricks.xyz/linux-hardening/bypass-bash-restrictions",
        # Windows / AD
        "https://book.hacktricks.xyz/windows-hardening/windows-local-privilege-escalation",
        "https://book.hacktricks.xyz/windows-hardening/active-directory-methodology",
        "https://book.hacktricks.xyz/windows-hardening/active-directory-methodology/kerberoasting",
        "https://book.hacktricks.xyz/windows-hardening/active-directory-methodology/pass-the-hash",
        "https://book.hacktricks.xyz/windows-hardening/active-directory-methodology/silver-ticket",
        "https://book.hacktricks.xyz/windows-hardening/active-directory-methodology/golden-ticket",
        # Network services
        "https://book.hacktricks.xyz/network-services-pentesting/pentesting-ssh",
        "https://book.hacktricks.xyz/network-services-pentesting/pentesting-ftp",
        "https://book.hacktricks.xyz/network-services-pentesting/pentesting-smb",
        "https://book.hacktricks.xyz/network-services-pentesting/pentesting-rdp",
        "https://book.hacktricks.xyz/network-services-pentesting/pentesting-dns",
        "https://book.hacktricks.xyz/network-services-pentesting/pentesting-smtp",
        "https://book.hacktricks.xyz/network-services-pentesting/pentesting-mysql",
        "https://book.hacktricks.xyz/network-services-pentesting/pentesting-redis",
        "https://book.hacktricks.xyz/network-services-pentesting/pentesting-mongodb",
        # Crypto / Forensics
        "https://book.hacktricks.xyz/cryptography/certificates",
        "https://book.hacktricks.xyz/cryptography/hash-cracking",
        "https://book.hacktricks.xyz/forensics/basic-forensic-methodology",
        "https://book.hacktricks.xyz/forensics/basic-forensic-methodology/memory-dump-analysis",
        "https://book.hacktricks.xyz/forensics/basic-forensic-methodology/pcap-inspection",
        # Reverse / Binary
        "https://book.hacktricks.xyz/reversing/reversing-tools-basic-methods",
        "https://book.hacktricks.xyz/exploiting/linux-exploiting-basic-esp",
        "https://book.hacktricks.xyz/exploiting/linux-exploiting-basic-esp/rop-leaking-libc-address",
        "https://book.hacktricks.xyz/exploiting/tools/pwntools",
        # Generic
        "https://book.hacktricks.xyz/generic-methodologies-and-resources/reverse-shells/linux",
        "https://book.hacktricks.xyz/generic-methodologies-and-resources/shells/linux",
        "https://book.hacktricks.xyz/generic-methodologies-and-resources/exfiltration",
        "https://book.hacktricks.xyz/generic-methodologies-and-resources/tunneling-and-port-forwarding",
        "https://book.hacktricks.xyz/generic-methodologies-and-resources/pentesting-methodology",
    ]

    results = []
    for url in tqdm(urls, desc="  HackTricks pages"):
        text = fetch_url_text(url)
        if text:
            results.append({
                "source": f"hacktricks:{url}",
                "text": text,
                "category": "exploit_technique",
            })
        time.sleep(REQUEST_DELAY)

    save_jsonl(results, "hacktricks.jsonl")
    return results


# ── 5. PayloadsAllTheThings ───────────────────────────────────────────────────
def scrape_payloads_all_things():
    print("\n[5/12] PayloadsAllTheThings...")
    repo = "swisskyrepo/PayloadsAllTheThings"
    files, branch = get_markdown_files(repo, max_files=120)
    print(f"  Branch: {branch}, found {len(files)} markdown files")

    results = []
    for filepath in tqdm(files, desc="  PayloadsAllTheThings"):
        content = fetch_raw(repo, branch, filepath)
        if content and len(content) > 200:
            results.append({
                "source": f"payloads_all_things:{filepath}",
                "text": content,
                "category": "payloads_reference",
            })
        time.sleep(0.3)

    save_jsonl(results, "payloads_all_things.jsonl")
    return results


# ── 6. SecLists Docs ──────────────────────────────────────────────────────────
def scrape_seclists_docs():
    print("\n[6/12] SecLists Documentation...")
    repo = "danielmiessler/SecLists"
    files, branch = get_markdown_files(repo, max_files=50)
    readme_files = [f for f in files if "readme" in f.lower()]
    print(f"  Branch: {branch}, readme files: {len(readme_files)}")

    results = []
    for filepath in tqdm(readme_files[:30], desc="  SecLists docs"):
        content = fetch_raw(repo, branch, filepath)
        if content and len(content) > 200:
            results.append({
                "source": f"seclists:{filepath}",
                "text": content,
                "category": "security_reference",
            })
        time.sleep(0.3)

    save_jsonl(results, "seclists_docs.jsonl")
    return results


# ── 7. PortSwigger Web Security Academy ──────────────────────────────────────
def scrape_portswigger():
    print("\n[7/12] PortSwigger Web Security Academy...")

    topics = [
        "sql-injection", "xss", "csrf", "xxe", "ssrf",
        "os-command-injection", "path-traversal", "access-control",
        "authentication", "websockets", "web-cache-poisoning",
        "insecure-deserialization", "http-request-smuggling",
        "business-logic-vulnerabilities", "clickjacking", "cors",
        "jwt", "oauth", "file-upload-vulnerabilities", "race-conditions",
        "nosql-injection", "api-testing", "prototype-pollution",
        "graphql-api-vulnerabilities", "server-side-template-injection",
        "dom-based", "web-llm-attacks",
    ]

    results = []
    for topic in tqdm(topics, desc="  PortSwigger topics"):
        url = f"https://portswigger.net/web-security/{topic}"
        text = fetch_url_text(url)
        if text:
            results.append({
                "source": f"portswigger:{topic}",
                "text": text,
                "category": "web_security",
            })
        time.sleep(REQUEST_DELAY)

    save_jsonl(results, "portswigger.jsonl")
    return results


# ── 8. Linux Tool Docs ────────────────────────────────────────────────────────
def scrape_linux_tool_docs():
    print("\n[8/12] Linux Tool Documentation...")

    tools = [
        # Recon & scanning
        "nmap", "masscan", "nikto", "gobuster", "dirb", "dirsearch",
        "whatweb", "subfinder", "amass", "ffuf",
        # Exploitation
        "sqlmap", "hydra", "medusa", "msfvenom", "searchsploit",
        # Web
        "curl", "wget",
        # Password cracking
        "hashcat", "john",
        # Binary analysis
        "gdb", "objdump", "nm", "strings", "ltrace", "strace",
        "file", "readelf",
        # Forensics
        "binwalk", "foremost", "exiftool", "steghide",
        "dd", "tcpdump", "tshark",
        # Crypto / encoding
        "openssl", "gpg", "xxd", "base64",
        # Networking
        "netcat", "nc", "socat", "ssh", "ncat", "proxychains",
        # Privilege escalation
        "sudo", "find", "chmod", "crontab", "ps", "ss", "lsof",
        # General utils
        "awk", "sed", "grep", "cut", "hexdump",
    ]

    results = []

    # tldr pages — concise, example-focused tool summaries
    base_url = "https://raw.githubusercontent.com/tldr-pages/tldr/main/pages"
    for tool in tqdm(tools, desc="  tldr pages"):
        for cat in ["common", "linux"]:
            url = f"{base_url}/{cat}/{tool}.md"
            try:
                r = requests.get(url, timeout=8)
                if r.status_code == 200 and len(r.text) > 100:
                    results.append({
                        "source": f"tldr:{tool}",
                        "text": r.text,
                        "category": "tool_documentation",
                        "tool": tool,
                    })
                    break
            except Exception:
                pass
            time.sleep(0.2)

    # PayloadsAllTheThings cheatsheets (methodology files)
    cheatsheets = [
        ("swisskyrepo/PayloadsAllTheThings",
         "Methodology and Resources/Network Discovery.md"),
        ("swisskyrepo/PayloadsAllTheThings",
         "Methodology and Resources/Linux - Privilege Escalation.md"),
        ("swisskyrepo/PayloadsAllTheThings",
         "Methodology and Resources/Windows - Privilege Escalation.md"),
        ("swisskyrepo/PayloadsAllTheThings",
         "Methodology and Resources/Reverse Shell Cheatsheet.md"),
        ("swisskyrepo/PayloadsAllTheThings",
         "Methodology and Resources/Powershell - Cheatsheet.md"),
    ]
    for repo, filepath in tqdm(cheatsheets, desc="  Cheatsheets"):
        for branch in ["master", "main"]:
            content = fetch_raw(repo, branch, filepath)
            if content:
                results.append({
                    "source": f"cheatsheet:{filepath}",
                    "text": content,
                    "category": "tool_cheatsheet",
                })
                break
        time.sleep(0.4)

    # Local man pages (works on Linux/Mac, skipped silently on Windows)
    local_tools = [
        "nmap", "gdb", "netcat", "curl", "wget", "ssh", "find",
        "grep", "awk", "sed", "xxd", "strings", "objdump", "readelf",
        "strace", "ltrace", "file",
    ]
    print("  Extracting local man pages...")
    for tool in local_tools:
        try:
            result = subprocess.run(
                ["man", tool], capture_output=True, text=True, timeout=5
            )
            if result.returncode == 0 and len(result.stdout) > 200:
                text = re.sub(r'.\x08', '', result.stdout)
                text = re.sub(r'\x1b\[[0-9;]*m', '', text)
                results.append({
                    "source": f"manpage:{tool}",
                    "text": text,
                    "category": "man_page",
                    "tool": tool,
                })
        except Exception:
            pass

    save_jsonl(results, "linux_tool_docs.jsonl")
    return results


# ── 9. PwnTools Documentation ─────────────────────────────────────────────────
def scrape_pwntools_docs():
    print("\n[9/12] PwnTools Documentation...")

    urls = [
        "https://docs.pwntools.com/en/stable/",
        "https://docs.pwntools.com/en/stable/tubes.html",
        "https://docs.pwntools.com/en/stable/elf/elf.html",
        "https://docs.pwntools.com/en/stable/rop/rop.html",
        "https://docs.pwntools.com/en/stable/fmtstr.html",
        "https://docs.pwntools.com/en/stable/shellcraft.html",
        "https://docs.pwntools.com/en/stable/util/cyclic.html",
        "https://docs.pwntools.com/en/stable/gdb.html",
        "https://docs.pwntools.com/en/stable/libcdb.html",
    ]

    results = []
    for url in tqdm(urls, desc="  PwnTools docs"):
        text = fetch_url_text(url)
        if text:
            results.append({
                "source": f"pwntools_docs:{url}",
                "text": text,
                "category": "tool_documentation",
            })
        time.sleep(REQUEST_DELAY)

    # PwnTools tutorial repo
    tutorial_files = scrape_repo_markdowns(
        "Gallopsled/pwntools-tutorial",
        max_files=20,
        source_prefix="pwntools_tutorial",
        category="tool_tutorial",
    )
    results.extend(tutorial_files)

    save_jsonl(results, "pwntools_docs.jsonl")
    return results


# ── 10. OWASP CheatSheet Series ───────────────────────────────────────────────
def scrape_owasp():
    print("\n[10/12] OWASP CheatSheet Series...")
    repo = "OWASP/CheatSheetSeries"
    files, branch = get_markdown_files(repo, max_files=100)
    cheatsheet_files = [f for f in files if "cheatsheets" in f.lower()]
    print(f"  Branch: {branch}, cheatsheet files: {len(cheatsheet_files)}")

    results = []
    for filepath in tqdm(cheatsheet_files, desc="  OWASP cheatsheets"):
        content = fetch_raw(repo, branch, filepath)
        if content and len(content) > 300:
            results.append({
                "source": f"owasp_cheatsheet:{filepath}",
                "text": content,
                "category": "security_reference",
            })
        time.sleep(0.3)

    save_jsonl(results, "owasp.jsonl")
    return results


# ── 11. Exploit-DB Papers ─────────────────────────────────────────────────────
def scrape_exploitdb_papers():
    print("\n[11/12] Exploit-DB Papers...")
    repo = "offensive-security/exploitdb"
    paper_files = []

    for branch in ["main", "master"]:
        url = f"https://api.github.com/repos/{repo}/git/trees/{branch}?recursive=1"
        try:
            r = requests.get(url, headers=HEADERS, timeout=15)
            if r.status_code == 200:
                tree = r.json().get("tree", [])
                paper_files = [
                    (f["path"], branch) for f in tree
                    if "papers/" in f["path"]
                    and f["path"].endswith(".txt")
                    and f.get("size", 0) > 500
                ][:120]
                if paper_files:
                    print(f"  Branch: {branch}, papers: {len(paper_files)}")
                    break
        except Exception as e:
            print(f"  ⚠ {e}")

    results = []
    for filepath, branch in tqdm(paper_files, desc="  Exploit-DB papers"):
        content = fetch_raw(repo, branch, filepath)
        if content and len(content) > 400:
            results.append({
                "source": f"exploitdb:{filepath}",
                "text": content,
                "category": "exploit_paper",
            })
        time.sleep(0.3)

    save_jsonl(results, "exploitdb_papers.jsonl")
    return results


# ── 12. HuggingFace Datasets ──────────────────────────────────────────────────
def load_huggingface_datasets():
    print("\n[12/12] HuggingFace Security Datasets...")
    from datasets import load_dataset

    results = []

    # Dataset 1: SecQA — security multiple choice Q&A
    try:
        print("  Loading zefang-liu/secqa...")
        ds = load_dataset("zefang-liu/secqa", split="train")
        count = 0
        for item in ds:
            q = item.get("question", "")
            a = item.get("answer", "") or item.get("correct_answer", "")
            if q and a:
                results.append({
                    "source": "hf:zefang-liu/secqa",
                    "text": f"### Instruction:\n{q}\n\n### Response:\n{a}",
                    "category": "security_qa",
                })
                count += 1
        print(f"    ✓ {count} examples from secqa")
    except Exception as e:
        print(f"    ⚠ secqa: {e}")

    # Dataset 2: Filter security content from Alpaca
    count_before = len(results)
    try:
        print("  Filtering security content from tatsu-lab/alpaca...")
        ds = load_dataset("tatsu-lab/alpaca", split="train")
        security_keywords = [
            "exploit", "vulnerability", "penetration", "ctf", "hack",
            "sql injection", "xss", "buffer overflow", "reverse shell",
            "privilege escalation", "cryptography", "forensics", "malware",
            "payload", "shellcode", "rop chain", "nmap", "metasploit",
            "burp suite", "wireshark", "binwalk", "pwntools",
        ]
        for item in ds:
            combined = (item.get("instruction", "") + " " + item.get("output", "")).lower()
            if any(kw in combined for kw in security_keywords):
                instr = item.get("instruction", "")
                inp   = item.get("input", "")
                out   = item.get("output", "")
                text  = f"### Instruction:\n{instr}"
                if inp:
                    text += f"\n\n### Input:\n{inp}"
                text += f"\n\n### Response:\n{out}"
                results.append({
                    "source": "hf:alpaca_security_filtered",
                    "text": text,
                    "category": "security_instruction",
                })
        print(f"    ✓ {len(results) - count_before} security entries filtered from alpaca")
    except Exception as e:
        print(f"    ⚠ alpaca: {e}")

    # Dataset 3: CyberNative security dataset
    count_before = len(results)
    try:
        print("  Loading CyberNative/AI_Security_Dataset...")
        ds = load_dataset("CyberNative/AI_Security_Dataset", split="train")
        for item in ds:
            q = item.get("prompt") or item.get("instruction") or item.get("question", "")
            a = item.get("response") or item.get("output") or item.get("answer", "")
            if q and a and len(q) + len(a) > 100:
                results.append({
                    "source": "hf:CyberNative/AI_Security_Dataset",
                    "text": f"### Instruction:\n{q}\n\n### Response:\n{a}",
                    "category": "security_qa",
                })
        print(f"    ✓ {len(results) - count_before} examples from CyberNative")
    except Exception as e:
        print(f"    ⚠ CyberNative: {e}")

    save_jsonl(results, "huggingface_datasets.jsonl")
    return results


# ── Summary ───────────────────────────────────────────────────────────────────
def print_summary(all_results: dict):
    print(f"\n{'='*65}")
    print(f"  🎉 SCRAPING COMPLETE")
    print(f"{'='*65}")
    total = 0
    for source, data in all_results.items():
        count = len(data)
        total += count
        status = "✓" if count > 0 else "✗"
        print(f"  {status} {source:<35} {count:>6} docs")
    print(f"{'─'*65}")
    print(f"  {'TOTAL':<37} {total:>6} docs")
    print(f"{'='*65}")
    print(f"\n  📁 Saved to: ./{OUTPUT_DIR}/")
    print(f"  👉 Next: python 2_prepare_dataset.py")
    print(f"{'='*65}\n")


# ── Main ──────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("=" * 65)
    print("  CTF/Security Dataset Scraper — FULL VERSION")
    print("=" * 65)
    print(f"  ⏱  Estimated time: 45–90 minutes")
    print(f"  ☕  Grab a coffee!\n")

    all_results = {}
    all_results["GitHub CTF Writeups"]     = scrape_github_ctf_writeups(max_repos=150)
    all_results["HackTheBox Writeups"]     = scrape_htb_writeups(max_repos=80)
    all_results["TryHackMe Writeups"]      = scrape_thm_writeups(max_repos=60)
    all_results["HackTricks"]              = scrape_hacktricks()
    all_results["PayloadsAllTheThings"]    = scrape_payloads_all_things()
    all_results["SecLists Docs"]           = scrape_seclists_docs()
    all_results["PortSwigger"]             = scrape_portswigger()
    all_results["Linux Tool Docs"]         = scrape_linux_tool_docs()
    all_results["PwnTools Docs"]           = scrape_pwntools_docs()
    all_results["OWASP"]                   = scrape_owasp()
    all_results["Exploit-DB Papers"]       = scrape_exploitdb_papers()
    all_results["HuggingFace Datasets"]    = load_huggingface_datasets()

    print_summary(all_results)
