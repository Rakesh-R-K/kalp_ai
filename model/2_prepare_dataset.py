"""
STEP 2: Prepare Instruction-Tuning Dataset
===========================================
Converts raw scraped text into instruction/response pairs
suitable for fine-tuning TinyLlama with SFTTrainer.

Output format (Alpaca-style):
    {
        "instruction": "Explain how SQL injection works",
        "input": "",
        "output": "SQL injection is a..."
    }

Usage:
    pip install datasets tqdm
    python 2_prepare_dataset.py
"""

import os
import re
import json
import random
from tqdm import tqdm
from datasets import Dataset
import hashlib

# ── Config ────────────────────────────────────────────────────────────────────
RAW_DIR      = "raw_data"
OUTPUT_DIR   = "prepared_data"
OUTPUT_FILE  = "ctf_dataset.jsonl"
MIN_LENGTH   = 100    # Minimum chars for a valid response
MAX_LENGTH   = 2048   # Max chars per response (keeps context window sane)
TRAIN_SPLIT  = 0.95

os.makedirs(OUTPUT_DIR, exist_ok=True)
random.seed(42)


# ── CTF-style instruction templates ───────────────────────────────────────────
# These wrap raw security content into question-answer format
INSTRUCTION_TEMPLATES = [
    # Explanation style
    "Explain the concept of {topic} in cybersecurity.",
    "What is {topic} and how does it work?",
    "Describe the {topic} attack technique.",
    "How does {topic} vulnerability work?",

    # CTF / practical style
    "How would you exploit a {topic} vulnerability in a CTF challenge?",
    "What tools and techniques are used for {topic} in penetration testing?",
    "Walk me through the steps to identify and exploit {topic}.",
    "What are common {topic} payloads used in CTF competitions?",

    # Defense / detection
    "How can {topic} attacks be detected and prevented?",
    "What are the indicators of a {topic} attack?",

    # Code / script style
    "Write a Python script to demonstrate {topic}.",
    "Give an example of a {topic} payload.",
    "Show me how to test for {topic} vulnerabilities.",
]

# Topic keywords to detect from content
TOPIC_KEYWORDS = {
    "sql injection": ["sql injection", "sqli", "union select", "sqlmap", "boolean-based", "time-based"],
    "XSS": ["xss", "cross-site scripting", "javascript injection", "<script>", "document.cookie"],
    "CSRF": ["csrf", "cross-site request forgery", "anti-csrf token"],
    "buffer overflow": ["buffer overflow", "stack overflow", "bof", "ret2libc", "shellcode", "pwntools"],
    "command injection": ["command injection", "os command", "rce", "remote code execution", ";ls", "|id"],
    "path traversal": ["path traversal", "directory traversal", "../", "lfi", "local file inclusion"],
    "SSRF": ["ssrf", "server-side request forgery", "internal network"],
    "XXE": ["xxe", "xml external entity", "xml injection"],
    "privilege escalation": ["privilege escalation", "privesc", "sudo", "suid", "capabilities"],
    "reverse shell": ["reverse shell", "netcat", "nc -e", "bash -i", "msfvenom"],
    "cryptography": ["rsa", "aes", "encryption", "decryption", "hash", "cipher", "padding oracle"],
    "steganography": ["steganography", "stego", "hidden data", "lsb", "binwalk"],
    "forensics": ["forensics", "memory dump", "volatility", "pcap", "wireshark", "strings"],
    "web exploitation": ["web exploit", "burp suite", "http request", "cookie", "session"],
    "binary exploitation": ["binary exploit", "pwn", "gdb", "radare2", "ghidra", "rop chain"],
    "network scanning": ["nmap", "port scan", "service enumeration", "network recon"],
    "OWASP": ["owasp", "top 10", "web application security"],
}


def detect_topic(text: str) -> str:
    """Detect the primary security topic from text content."""
    text_lower = text.lower()
    topic_scores = {}
    for topic, keywords in TOPIC_KEYWORDS.items():
        score = sum(1 for kw in keywords if kw in text_lower)
        if score > 0:
            topic_scores[topic] = score
    if topic_scores:
        return max(topic_scores, key=topic_scores.get)
    return "cybersecurity"


def clean_text(text: str) -> str:
    """Clean raw scraped text."""
    # Remove excessive whitespace
    text = re.sub(r'\n{3,}', '\n\n', text)
    text = re.sub(r' {2,}', ' ', text)
    # Remove URLs (they become stale)
    text = re.sub(r'http[s]?://\S+', '[URL]', text)
    # Remove markdown image syntax
    text = re.sub(r'!\[.*?\]\(.*?\)', '', text)
    # Remove HTML tags if any slipped through
    text = re.sub(r'<[^>]+>', '', text)
    # Strip leading/trailing whitespace
    text = text.strip()
    return text


def chunk_text(text: str, max_chars: int = MAX_LENGTH) -> list[str]:
    """Split long documents into chunks at paragraph boundaries."""
    paragraphs = text.split('\n\n')
    chunks = []
    current_chunk = []
    current_len = 0

    for para in paragraphs:
        para = para.strip()
        if not para:
            continue
        if current_len + len(para) > max_chars and current_chunk:
            chunks.append('\n\n'.join(current_chunk))
            current_chunk = [para]
            current_len = len(para)
        else:
            current_chunk.append(para)
            current_len += len(para)

    if current_chunk:
        chunks.append('\n\n'.join(current_chunk))

    return [c for c in chunks if len(c) >= MIN_LENGTH]


def text_to_instruction_pairs(text: str, source: str) -> list[dict]:
    """Convert a text chunk into instruction-response pairs."""
    text = clean_text(text)
    chunks = chunk_text(text)
    pairs = []

    for chunk in chunks:
        topic = detect_topic(chunk)
        template = random.choice(INSTRUCTION_TEMPLATES)
        instruction = template.format(topic=topic)

        pairs.append({
            "instruction": instruction,
            "input": "",
            "output": chunk,
            "source": source,
        })

    return pairs


def load_jsonl(filepath: str) -> list[dict]:
    """Load a JSONL file."""
    items = []
    if not os.path.exists(filepath):
        return items
    with open(filepath) as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    items.append(json.loads(line))
                except json.JSONDecodeError:
                    pass
    return items


def deduplicate(pairs: list[dict]) -> list[dict]:
    """Remove near-duplicate entries using content hashing."""
    seen = set()
    unique = []
    for pair in pairs:
        # Hash first 500 chars of output to detect duplicates
        h = hashlib.md5(pair["output"][:500].encode()).hexdigest()
        if h not in seen:
            seen.add(h)
            unique.append(pair)
    return unique


def format_as_prompt(pair: dict) -> str:
    """
    Format into the TinyLlama chat template used during fine-tuning.
    This must match exactly what you use in the training script.
    """
    instruction = pair["instruction"]
    response = pair["output"]
    inp = pair.get("input", "")

    if inp:
        prompt = f"### Instruction:\n{instruction}\n\n### Input:\n{inp}\n\n### Response:\n{response}"
    else:
        prompt = f"### Instruction:\n{instruction}\n\n### Response:\n{response}"

    return prompt


# ── Main ──────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("=" * 60)
    print("  CTF Dataset Preparation")
    print("=" * 60)

    # Load all raw data
    all_raw = []
    for filename in ["github_writeups.jsonl", "hacktricks.jsonl", "portswigger.jsonl"]:
        path = os.path.join(RAW_DIR, filename)
        items = load_jsonl(path)
        all_raw.extend(items)
        print(f"  Loaded {len(items):>5} docs from {filename}")

    if not all_raw:
        print("\n⚠ No raw data found! Run 1_scrape_dataset.py first.")
        print("  Or place .jsonl files in ./raw_data/")
        exit(1)

    print(f"\n  Total raw documents: {len(all_raw)}")

    # Convert to instruction pairs
    print("\n  Converting to instruction pairs...")
    all_pairs = []
    for doc in tqdm(all_raw):
        pairs = text_to_instruction_pairs(doc["text"], doc.get("source", "unknown"))
        all_pairs.extend(pairs)

    print(f"  Raw pairs generated: {len(all_pairs)}")

    # Deduplicate
    all_pairs = deduplicate(all_pairs)
    print(f"  After deduplication: {len(all_pairs)}")

    # Shuffle
    random.shuffle(all_pairs)

    # Train / Val split
    split_idx = int(len(all_pairs) * TRAIN_SPLIT)
    train_pairs = all_pairs[:split_idx]
    val_pairs   = all_pairs[split_idx:]

    print(f"\n  Train: {len(train_pairs)} | Val: {len(val_pairs)}")

    # Save as JSONL (instruction format)
    train_path = os.path.join(OUTPUT_DIR, "train.jsonl")
    val_path   = os.path.join(OUTPUT_DIR, "val.jsonl")

    with open(train_path, "w") as f:
        for pair in train_pairs:
            f.write(json.dumps(pair) + "\n")

    with open(val_path, "w") as f:
        for pair in val_pairs:
            f.write(json.dumps(pair) + "\n")

    # Also save formatted prompts for SFTTrainer
    formatted_path = os.path.join(OUTPUT_DIR, "train_formatted.jsonl")
    with open(formatted_path, "w") as f:
        for pair in train_pairs:
            formatted = {"text": format_as_prompt(pair)}
            f.write(json.dumps(formatted) + "\n")

    print(f"\n{'='*60}")
    print(f"  ✅ Dataset ready!")
    print(f"  📄 train.jsonl     → {len(train_pairs)} examples")
    print(f"  📄 val.jsonl       → {len(val_pairs)} examples")
    print(f"  📄 train_formatted.jsonl → ready for SFTTrainer")
    print(f"\n  👉 Next: Upload prepared_data/ to Google Drive")
    print(f"     Then run the Colab notebook: 3_finetune_colab.ipynb")
    print(f"{'='*60}")

    # Preview a sample
    print("\n  📋 Sample pair:")
    sample = random.choice(train_pairs)
    print(f"  Instruction: {sample['instruction']}")
    print(f"  Output preview: {sample['output'][:200]}...")
