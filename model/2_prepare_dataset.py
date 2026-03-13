"""
STEP 2: Prepare Instruction-Tuning Dataset
===========================================
- Auto-detects ALL .jsonl files in raw_data/
- Fixes Windows encoding issues (UTF-8)
- Converts raw text into instruction/response pairs
- Deduplicates and splits into train/val

Usage:
    python 2_prepare_dataset.py
"""

import os
import re
import json
import random
import hashlib
from tqdm import tqdm

# ── Config ────────────────────────────────────────────────────────────────────
RAW_DIR     = "raw_data"
OUTPUT_DIR  = "prepared_data"
MIN_LENGTH  = 150
MAX_LENGTH  = 2048
TRAIN_SPLIT = 0.95
RANDOM_SEED = 42

os.makedirs(OUTPUT_DIR, exist_ok=True)
random.seed(RANDOM_SEED)

# ── Instruction templates ─────────────────────────────────────────────────────
INSTRUCTION_TEMPLATES = [
    "Explain the concept of {topic} in cybersecurity.",
    "What is {topic} and how does it work?",
    "Describe the {topic} attack technique.",
    "How does a {topic} vulnerability work?",
    "How would you exploit a {topic} vulnerability in a CTF challenge?",
    "What tools and techniques are used for {topic} in penetration testing?",
    "Walk me through the steps to identify and exploit {topic}.",
    "What are common {topic} payloads used in CTF competitions?",
    "How do you use {topic} in a penetration test?",
    "Show me an example of using {topic} to find vulnerabilities.",
    "What are the most useful {topic} commands for CTF challenges?",
    "How can {topic} attacks be detected and prevented?",
    "Write a Python script to demonstrate {topic}.",
    "Give an example of a {topic} payload.",
    "Show me how to test for {topic} vulnerabilities.",
]

# ── Topic detection ───────────────────────────────────────────────────────────
TOPIC_KEYWORDS = {
    "SQL injection":        ["sql injection", "sqli", "union select", "sqlmap", "boolean-based"],
    "XSS":                  ["xss", "cross-site scripting", "<script>", "document.cookie"],
    "CSRF":                 ["csrf", "cross-site request forgery", "anti-csrf"],
    "buffer overflow":      ["buffer overflow", "bof", "ret2libc", "shellcode", "pwntools", "cyclic"],
    "command injection":    ["command injection", "rce", "remote code execution", "|id", ";ls"],
    "path traversal":       ["path traversal", "directory traversal", "../", "lfi"],
    "SSRF":                 ["ssrf", "server-side request forgery", "169.254.169.254"],
    "XXE":                  ["xxe", "xml external entity", "doctype"],
    "privilege escalation": ["privilege escalation", "privesc", "sudo -l", "suid", "crontab"],
    "reverse shell":        ["reverse shell", "netcat", "bash -i", "msfvenom"],
    "cryptography":         ["rsa", "aes", "encryption", "hash", "cipher", "padding oracle"],
    "steganography":        ["steganography", "stego", "lsb", "binwalk", "steghide", "zsteg"],
    "forensics":            ["forensics", "memory dump", "volatility", "pcap", "wireshark", "foremost"],
    "binary exploitation":  ["binary exploit", "pwn", "gdb", "rop chain", "format string", "ghidra"],
    "network scanning":     ["nmap", "port scan", "masscan", "service enumeration"],
    "password cracking":    ["hashcat", "john the ripper", "rockyou", "brute force"],
    "Active Directory":     ["active directory", "kerberoasting", "pass the hash", "golden ticket"],
    "web exploitation":     ["web exploit", "burp suite", "http request", "web shell"],
    "CTF methodology":      ["ctf", "capture the flag", "writeup", "walkthrough", "flag", "hackthebox"],
    "nmap":                 ["nmap", "-sV", "-sC", "service detection"],
    "metasploit":           ["metasploit", "msfconsole", "meterpreter", "exploit/"],
    "OWASP":                ["owasp", "top 10", "web application security"],
}


def detect_topic(text: str) -> str:
    text_lower = text.lower()
    scores = {
        topic: sum(1 for kw in keywords if kw in text_lower)
        for topic, keywords in TOPIC_KEYWORDS.items()
    }
    best = max(scores, key=scores.get)
    return best if scores[best] > 0 else "cybersecurity"


def clean_text(text: str) -> str:
    text = re.sub(r'\n{3,}', '\n\n', text)
    text = re.sub(r' {2,}', ' ', text)
    text = re.sub(r'http[s]?://\S+', '[URL]', text)
    text = re.sub(r'!\[.*?\]\(.*?\)', '', text)
    text = re.sub(r'<[^>]+>', '', text)
    text = re.sub(r'^[-=]{3,}$', '', text, flags=re.MULTILINE)
    return text.strip()


def chunk_text(text: str) -> list:
    paragraphs = text.split('\n\n')
    chunks, current_chunk, current_len = [], [], 0
    for para in paragraphs:
        para = para.strip()
        if not para:
            continue
        if current_len + len(para) > MAX_LENGTH and current_chunk:
            chunk = '\n\n'.join(current_chunk)
            if len(chunk) >= MIN_LENGTH:
                chunks.append(chunk)
            current_chunk = [para]
            current_len = len(para)
        else:
            current_chunk.append(para)
            current_len += len(para)
    if current_chunk:
        chunk = '\n\n'.join(current_chunk)
        if len(chunk) >= MIN_LENGTH:
            chunks.append(chunk)
    return chunks


def text_to_pairs(text: str, source: str) -> list:
    text   = clean_text(text)
    chunks = chunk_text(text)
    pairs  = []
    for chunk in chunks:
        topic       = detect_topic(chunk)
        instruction = random.choice(INSTRUCTION_TEMPLATES).format(topic=topic)
        pairs.append({
            "instruction": instruction,
            "input":       "",
            "output":      chunk,
            "source":      source,
        })
    return pairs


def load_jsonl(filepath: str) -> list:
    """Load JSONL with UTF-8 encoding, ignoring bad characters."""
    items = []
    if not os.path.exists(filepath):
        return items
    with open(filepath, encoding="utf-8", errors="ignore") as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    items.append(json.loads(line))
                except json.JSONDecodeError:
                    pass
    return items


def deduplicate(pairs: list) -> list:
    seen, unique = set(), []
    for pair in pairs:
        h = hashlib.md5(pair["output"][:500].encode(errors="ignore")).hexdigest()
        if h not in seen:
            seen.add(h)
            unique.append(pair)
    return unique


def format_prompt(pair: dict) -> str:
    instruction = pair["instruction"]
    response    = pair["output"]
    inp         = pair.get("input", "")
    if inp:
        return f"### Instruction:\n{instruction}\n\n### Input:\n{inp}\n\n### Response:\n{response}"
    return f"### Instruction:\n{instruction}\n\n### Response:\n{response}"


# ── Main ──────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("=" * 60)
    print("  CTF Dataset Preparation")
    print("=" * 60)

    # Auto-detect all .jsonl files
    jsonl_files = sorted([
        f for f in os.listdir(RAW_DIR)
        if f.endswith(".jsonl")
    ])

    if not jsonl_files:
        print(f"\n❌ No .jsonl files found in {RAW_DIR}/")
        print("   Run 1_scrape_dataset.py first!")
        exit(1)

    # Load all raw data
    all_raw = []
    print(f"\n  Loading from {RAW_DIR}/")
    for filename in jsonl_files:
        path  = os.path.join(RAW_DIR, filename)
        items = load_jsonl(path)
        all_raw.extend(items)
        status = "✓" if items else "✗"
        print(f"  {status} {filename:<45} {len(items):>5} docs")

    print(f"\n  Total raw documents: {len(all_raw)}")

    if not all_raw:
        print("❌ No data loaded.")
        exit(1)

    # Separate pre-formatted (HuggingFace) from raw text
    pre_formatted = []
    to_convert    = []

    for doc in all_raw:
        text = doc.get("text", "")
        if text.startswith("### Instruction:") and "### Response:" in text:
            parts  = text.split("### Response:\n", 1)
            output = parts[1].strip() if len(parts) > 1 else ""
            instr  = parts[0].replace("### Instruction:\n", "").replace("### Input:\n", "").strip()
            if output and len(output) >= MIN_LENGTH:
                pre_formatted.append({
                    "instruction": instr,
                    "input":       "",
                    "output":      output,
                    "source":      doc.get("source", "unknown"),
                })
        else:
            to_convert.append(doc)

    print(f"\n  Pre-formatted (HuggingFace): {len(pre_formatted)}")
    print(f"  To convert (raw text):       {len(to_convert)}")

    # Convert raw text docs
    print("\n  Converting raw text → instruction pairs...")
    converted = []
    for doc in tqdm(to_convert):
        pairs = text_to_pairs(doc.get("text", ""), doc.get("source", "unknown"))
        converted.extend(pairs)
    print(f"  Converted pairs: {len(converted)}")

    # Combine, deduplicate, shuffle
    all_pairs = pre_formatted + converted
    print(f"  Total before dedup: {len(all_pairs)}")
    all_pairs = deduplicate(all_pairs)
    print(f"  After deduplication: {len(all_pairs)}")
    random.shuffle(all_pairs)

    # Train / Val split
    split_idx   = int(len(all_pairs) * TRAIN_SPLIT)
    train_pairs = all_pairs[:split_idx]
    val_pairs   = all_pairs[split_idx:]

    # Save files
    with open(os.path.join(OUTPUT_DIR, "train.jsonl"), "w", encoding="utf-8") as f:
        for pair in train_pairs:
            f.write(json.dumps(pair, ensure_ascii=False) + "\n")

    with open(os.path.join(OUTPUT_DIR, "val.jsonl"), "w", encoding="utf-8") as f:
        for pair in val_pairs:
            f.write(json.dumps(pair, ensure_ascii=False) + "\n")

    with open(os.path.join(OUTPUT_DIR, "train_formatted.jsonl"), "w", encoding="utf-8") as f:
        for pair in train_pairs:
            f.write(json.dumps({"text": format_prompt(pair)}, ensure_ascii=False) + "\n")

    avg_len = sum(len(p["output"]) for p in train_pairs) // max(len(train_pairs), 1)

    print(f"\n{'='*60}")
    print(f"  ✅ Dataset ready!")
    print(f"{'='*60}")
    print(f"  📄 train.jsonl           →  {len(train_pairs):>6} examples")
    print(f"  📄 val.jsonl             →  {len(val_pairs):>6} examples")
    print(f"  📄 train_formatted.jsonl →  {len(train_pairs):>6} examples")
    print(f"  📊 Avg response length   →  {avg_len:>6} chars")
    print(f"  📁 Saved to: ./{OUTPUT_DIR}/")
    print(f"\n  👉 Upload prepared_data/train_formatted.jsonl to Google Drive")
    print(f"     Then open 3_finetune_colab.ipynb in Google Colab!")
    print(f"{'='*60}")

    # Random sample preview
    sample = random.choice(train_pairs)
    print(f"\n  📋 Random sample:")
    print(f"  Source:      {sample['source']}")
    print(f"  Instruction: {sample['instruction']}")
    print(f"  Output:      {sample['output'][:250]}...")
