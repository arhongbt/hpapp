"""Extract HP-prov PDFs to JSONL using Anthropic PDF document input.

Reads PDFs from ../../hp-prov/, sends each to Claude (Sonnet) with structured
extraction prompts, writes a unified data/uppgifter.jsonl that the pipeline can consume.

Usage:
    # Test on en fil:
    python scripts/extract_corpus.py --only provpass-2-verb-utan-elf.pdf

    # Allt:
    python scripts/extract_corpus.py
"""
import argparse
import base64
import json
import os
import re
from pathlib import Path

from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv(override=True)

MODEL = "claude-sonnet-4-6"
SCRIPT_DIR = Path(__file__).resolve().parent
PIPELINE_DIR = SCRIPT_DIR.parent
PROV_DIR = PIPELINE_DIR.parent.parent / "hp-prov"
OUTPUT_PATH = PIPELINE_DIR / "data" / "uppgifter.jsonl"

# Mappning från PDF-filnamn → metadata (datum, prov-typ, pass-nummer).
# 26a = HP 2026-04-18 (vt 2026); 25b = HP 2025-10-19 (ht 2025).
EXAM_META = {
    "hogskoleprovet-facit-26a.pdf":  {"date": "2026-04-18", "year": 2026, "term": "vt", "kind": "facit"},
    "hp-25b.pdf":                    {"date": "2025-10-19", "year": 2025, "term": "ht", "kind": "facit"},
    "provpass-1-kvant.pdf":          {"date": "2025-10-19", "year": 2025, "term": "ht", "kind": "kvant", "pass": 1},
    "provpass-2-verb-utan-elf.pdf":  {"date": "2026-04-18", "year": 2026, "term": "vt", "kind": "verb",  "pass": 2},
    "provpass-3-kvant.pdf":          {"date": "2026-04-18", "year": 2026, "term": "vt", "kind": "kvant", "pass": 3},
    "provpass-3-verb-utan-elf.pdf":  {"date": "2025-10-19", "year": 2025, "term": "ht", "kind": "verb",  "pass": 3},
    "provpass-4-kvant.pdf":          {"date": "2025-10-19", "year": 2025, "term": "ht", "kind": "kvant", "pass": 4},
    "provpass-4-verb-utan-elf.pdf":  {"date": "2026-04-18", "year": 2026, "term": "vt", "kind": "verb",  "pass": 4},
    "provpass-5-kvant.pdf":          {"date": "2026-04-18", "year": 2026, "term": "vt", "kind": "kvant", "pass": 5},
    "provpass-5-verb-utan-elf.pdf":  {"date": "2025-10-19", "year": 2025, "term": "ht", "kind": "verb",  "pass": 5},
}

client = Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])


def encode_pdf(path: Path) -> str:
    return base64.standard_b64encode(path.read_bytes()).decode("utf-8")


def call_with_pdf(pdf_b64: str, user_text: str, max_tokens: int = 8192) -> str:
    response = client.messages.create(
        model=MODEL,
        max_tokens=max_tokens,
        messages=[{
            "role": "user",
            "content": [
                {"type": "document", "source": {"type": "base64", "media_type": "application/pdf", "data": pdf_b64}},
                {"type": "text", "text": user_text},
            ],
        }],
    )
    return "\n".join(b.text for b in response.content if hasattr(b, "text"))


def strip_fences(text: str) -> str:
    text = re.sub(r"^```(?:json)?\s*", "", text.strip())
    text = re.sub(r"```\s*$", "", text.strip())
    return text


FACIT_PROMPT = """Detta är ett facit för Högskoleprovet.

Ett av provpassen är "utprövningspass" och ska EXKLUDERAS — det står tydligt i botten
av facit-sidan ("Provpass X ingår ej!").

För de FYRA övriga provpassen: returnera 40 svar (A-E) i ordning 1-40.

Svara med STRIKT JSON, inget annat. Format:
{
  "passes": [
    {"pass_number": 2, "kind": "verb",  "answers": ["D","E",...,"C"]},
    {"pass_number": 3, "kind": "kvant", "answers": ["C","C",...]},
    ...
  ]
}

kind = "verb" om passet listas som "Verbal del", "kvant" om "Kvantitativ del".
"""


def extract_facit(pdf_path: Path) -> dict[int, list[str]]:
    text = call_with_pdf(encode_pdf(pdf_path), FACIT_PROMPT, max_tokens=4096)
    parsed = json.loads(strip_fences(text))
    return {p["pass_number"]: p["answers"] for p in parsed["passes"]}


def provpass_prompt(meta: dict) -> str:
    if meta["kind"] == "kvant":
        ranges = "XYZ (1-12), KVA (13-22), NOG (23-28), DTK (29-40)"
    else:
        ranges = "ORD (1-10), LÄS (11-20), MEK (21-30); ELF (31-40) finns INTE i denna fil"
    return f"""Detta är ett provhäfte för Högskoleprovet, Provpass {meta['pass']}.
Delprov-ordning: {ranges}.

Extrahera VARJE numrerad uppgift med:
- task_number: heltal 1-40
- delprov: en av XYZ, KVA, NOG, DTK, ORD, LÄS, MEK, ELF
- uppgift_text: hela uppgiftstexten. Skriv matematiska uttryck i läsbar text
  (t.ex. "x + 1/4 = 1/8", "f(x) = 7x² - 7", "(3x + y)(x - y)").
  För LÄS-uppgifter: inkludera den läs-text som hör till frågan, men kort —
  räcker att markera vilken text uppgiften refererar till.
- answer_options: dict med "A", "B", "C", "D" (och "E" för NOG), med svarstexten

För DTK-uppgifter där diagram/tabell/karta är central, beskriv KORT i uppgift_text
vad som visas (t.ex. "Tabell visar antal vårdtillfällen, medelvårdtid och medelålder
per sjukhus i Sverige 2014") så en handledare kan förstå kontexten.

Om en delprov-typ saknas i filen (t.ex. ELF), hoppa helt över dessa uppgiftsnummer.

Svara med STRIKT JSONL — en JSON-uppgift per rad, ingen markdown, ingen prolog.
Exempel:
{{"task_number": 1, "delprov": "XYZ", "uppgift_text": "Lös x + 1/4 = 1/8", "answer_options": {{"A": "-3/8", "B": "-1/8", "C": "1/4", "D": "1/2"}}}}
"""


def extract_provpass(pdf_path: Path, meta: dict) -> list[dict]:
    text = call_with_pdf(encode_pdf(pdf_path), provpass_prompt(meta), max_tokens=16384)
    text = strip_fences(text)
    tasks = []
    for line in text.split("\n"):
        line = line.strip()
        if not line:
            continue
        try:
            tasks.append(json.loads(line))
        except json.JSONDecodeError:
            print(f"    WARN: ej parsbar rad: {line[:100]}")
    return tasks


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--only", help="Processa bara denna PDF (filnamn)")
    args = parser.parse_args()

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

    pdfs_to_process = (
        {args.only: EXAM_META[args.only]} if args.only else EXAM_META
    )

    facits: dict[str, dict[int, list[str]]] = {}
    for name, meta in pdfs_to_process.items():
        if meta["kind"] != "facit":
            continue
        path = PROV_DIR / name
        if not path.exists():
            print(f"SKIP (saknas): {name}")
            continue
        print(f"Facit: {name}")
        facits[meta["date"]] = extract_facit(path)
        print(f"  → {sum(len(v) for v in facits[meta['date']].values())} svar i {len(facits[meta['date']])} pass")

    all_tasks: list[dict] = []
    for name, meta in pdfs_to_process.items():
        if meta["kind"] == "facit":
            continue
        path = PROV_DIR / name
        if not path.exists():
            print(f"SKIP (saknas): {name}")
            continue
        print(f"Provpass: {name}")
        tasks = extract_provpass(path, meta)
        print(f"  → {len(tasks)} uppgifter extraherade")

        facit_for_pass = facits.get(meta["date"], {}).get(meta["pass"], [])
        for t in tasks:
            tn = t.get("task_number")
            if not isinstance(tn, int):
                print(f"    WARN: saknar task_number: {t}")
                continue
            correct = facit_for_pass[tn - 1] if 0 < tn <= len(facit_for_pass) else "?"
            all_tasks.append({
                "id": f"{meta['year']}-{meta['term']}-pass{meta['pass']}-uppg{tn:02d}",
                "delprov": t["delprov"],
                "year": meta["year"],
                "term": meta["term"],
                "pass_number": meta["pass"],
                "task_number": tn,
                "uppgift_text": t["uppgift_text"],
                "answer_options": t["answer_options"],
                "correct_answer": correct,
            })

    if args.only:
        out = OUTPUT_PATH.parent / f"_test_{Path(args.only).stem}.jsonl"
    else:
        out = OUTPUT_PATH

    with open(out, "w", encoding="utf-8") as f:
        for task in all_tasks:
            f.write(json.dumps(task, ensure_ascii=False) + "\n")

    print(f"\nKlart. {len(all_tasks)} uppgifter → {out}")


if __name__ == "__main__":
    main()
