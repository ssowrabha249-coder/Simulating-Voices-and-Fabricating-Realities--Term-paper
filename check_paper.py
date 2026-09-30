#!/usr/bin/env python3
"""Pre-submission validation checker for the term paper LaTeX project."""

import os
import re
import sys
import glob
import pypdf

def main():
    paper_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(paper_dir)

    print("=" * 80)
    print(" TERM PAPER PRE-SUBMISSION VALIDATION REPORT")
    print(" Author: Sowrabha Somashekar (Matr. 1837734)")
    print("=" * 80)

    reasons = []

    # 1. TODO Check
    print("\n[1] TODO Check:")
    tex_files = sorted(glob.glob("*.tex") + glob.glob("sections/*.tex") + glob.glob("appendix/*.tex") + glob.glob("tables/*.tex"))
    todo_list = []
    for tf in tex_files:
        if os.path.exists(tf):
            with open(tf, "r", encoding="utf-8") as f:
                for line_idx, line in enumerate(f, start=1):
                    if r"\todo{" in line or "[TODO:" in line or ("URL MISSING" in line and not line.lstrip().startswith("%")):
                        todo_list.append((tf, line_idx, line.strip()))

    if todo_list:
        print(f"  FAILED: Found {len(todo_list)} TODO occurrences:")
        for tf, l_no, text in todo_list:
            print(f"    - {tf}:{l_no} -> {text}")
        reasons.append(f"Found {len(todo_list)} TODO occurrences")
    else:
        print("  PASS: 0 TODO occurrences found.")

    # 2. Body Page Count Check
    print("\n[2] Body Page Count Check:")
    pdf_path = "main.pdf"
    if not os.path.exists(pdf_path):
        print("  ERROR: main.pdf does not exist. Run compilation first.")
        reasons.append("main.pdf not found")
    else:
        reader = pypdf.PdfReader(pdf_path)
        total_pages = len(reader.pages)
        print(f"  Total PDF pages: {total_pages}")
        
        intro_page = None
        ref_page = None
        for idx, page in enumerate(reader.pages, start=1):
            text = page.extract_text() or ""
            # skip the table of contents, which also lists "1 Introduction"
            if intro_page is None and "Contents" not in text and re.search(r'^\s*1\s+Introduction', text, re.MULTILINE):
                intro_page = idx
            if ref_page is None and re.search(r'^\s*References\s*$', text, re.MULTILINE):
                ref_page = idx

        if intro_page and ref_page:
            body_pages = ref_page - intro_page
            print(f"  Introduction starts on page: {intro_page}")
            print(f"  References start on page: {ref_page}")
            print(f"  Computed body page count: {body_pages}")
            if 8 <= body_pages <= 10:
                print(f"  PASS: Body page count ({body_pages}) is within the required 8-10 range.")
            else:
                print(f"  WARN: Body page count ({body_pages}) is outside 8-10 range.")
                reasons.append(f"Body pages ({body_pages}) outside 8-10 range")
        else:
            print("  WARN: Could not strictly determine intro/ref page boundaries.")
            reasons.append("Could not determine body page count")

    # 3. Reference Count in references.bib
    print("\n[3] Reference Count Check:")
    bib_path = "references.bib"
    bib_entries = []
    bib_keys = set()
    bib_entry_data = {}
    if os.path.exists(bib_path):
        with open(bib_path, "r", encoding="utf-8") as f:
            bib_content = f.read()

        pattern = re.compile(r'@(\w+)\s*\{\s*([^,]+),([^@]*)(?=\n@|\Z)', re.DOTALL)
        for match in pattern.finditer(bib_content):
            entry_type = match.group(1).lower()
            key = match.group(2).strip()
            body = match.group(3)
            bib_entries.append(key)
            bib_keys.add(key)
            bib_entry_data[key] = (entry_type, body)

        n_refs = len(bib_entries)
        print(f"  Number of bib entries: {n_refs}")
        if 10 <= n_refs <= 15:
            print(f"  PASS: Reference count ({n_refs}) is within the 10-15 range.")
        else:
            print(f"  WARN: Reference count ({n_refs}) outside 10-15 range.")
            reasons.append(f"Reference count ({n_refs}) outside 10-15 range")
    else:
        print("  ERROR: references.bib does not exist.")
        reasons.append("references.bib not found")

    # 4. Bidirectional Citation Check
    print("\n[4] Citation Key Consistency Check:")
    cited_keys = set()
    cite_pattern = re.compile(r'\\cite(?:\[[^\]]*\])?\{([^}]+)\}')
    for tf in tex_files:
        if os.path.exists(tf):
            with open(tf, "r", encoding="utf-8") as f:
                content = f.read()
            for match in cite_pattern.finditer(content):
                keys = [k.strip() for k in match.group(1).split(",") if k.strip()]
                cited_keys.update(keys)

    missing_keys = cited_keys - bib_keys
    unused_keys = bib_keys - cited_keys
    print(f"  Total unique cited keys in .tex: {len(cited_keys)}")
    if missing_keys:
        print(f"  FAILED: Missing keys (cited but not in .bib): {sorted(missing_keys)}")
        reasons.append(f"Missing keys: {sorted(missing_keys)}")
    else:
        print("  PASS: All cited keys exist in references.bib.")

    if unused_keys:
        print(f"  FAILED: Unused keys in bib: {sorted(unused_keys)}")
        reasons.append(f"Unused keys: {sorted(unused_keys)}")
    else:
        print("  PASS: All keys in references.bib are cited in the text.")

    # 5. Undefined References in Log
    print("\n[5] Undefined References Check in main.log:")
    log_path = "main.log"
    undefined_warnings = []
    if os.path.exists(log_path):
        with open(log_path, "r", encoding="utf-8", errors="replace") as f:
            for line in f:
                if re.search(r'undefined', line, re.IGNORECASE):
                    if any(w in line.lower() for w in ["reference", "citation", "label"]):
                        undefined_warnings.append(line.strip())
        if undefined_warnings:
            print(f"  FAILED: Found {len(undefined_warnings)} undefined warnings:")
            for uw in undefined_warnings:
                print(f"    - {uw}")
            reasons.append(f"Undefined warnings in log: {len(undefined_warnings)}")
        else:
            print("  PASS: 0 undefined reference/citation warnings in main.log.")
    else:
        print("  WARN: main.log not found.")

    # 6. Persistent Identifiers
    print("\n[6] Persistent Identifier Check (doi / url / eprint):")
    missing_id_keys = []
    for key, (etype, body) in bib_entry_data.items():
        has_doi = bool(re.search(r'\bdoi\s*=', body, re.IGNORECASE))
        has_url = bool(re.search(r'\burl\s*=', body, re.IGNORECASE))
        has_eprint = bool(re.search(r'\beprint\s*=', body, re.IGNORECASE))
        if not (has_doi or has_url or has_eprint):
            missing_id_keys.append(key)

    if missing_id_keys:
        print(f"  FAILED: Bib entries missing doi/url/eprint: {missing_id_keys}")
        reasons.append(f"Missing identifiers: {missing_id_keys}")
    else:
        print("  PASS: Every bib entry contains a valid DOI, URL, or eprint.")

    # Summary
    print("\n" + "=" * 80)
    if not reasons:
        print(" TERM PAPER STATUS: READY FOR SUBMISSION (ALL CHECKS PASSED)")
        print("=" * 80)
        sys.exit(0)
    else:
        print(" TERM PAPER STATUS: NOT READY (REASONS BELOW)")
        for idx, r in enumerate(reasons, start=1):
            print(f"  {idx}. {r}")
        print("=" * 80)
        sys.exit(1)

if __name__ == "__main__":
    main()
