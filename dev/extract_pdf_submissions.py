#!/usr/bin/env python3
"""
Extract names and numbers from Fantasy Football Draft Order Game.pdf
"""
import pdfplumber
import re

PDF_PATH = "dev/Fantasy Football Draft Order Game.pdf"

submissions = []

with pdfplumber.open(PDF_PATH) as pdf:
    for i, page in enumerate(pdf.pages):
        text = page.extract_text()
        print(f"--- Page {i+1} ---\n{text}\n")
        # Extraction logic will be refined after inspecting output

print(f"Extracted {len(submissions)} submissions:")
for name, number in submissions:
    print(f"{name}: {number}")
