# Simulating Voices and Fabricating Realities

Term paper for *Advanced Topics in Computational Text and Media Sciences #2* (M.Sc. NLP, Universität Trier, 2026).
Author: Sowrabha Somashekar · Supervisor: Christoph Hau

## Overview
The paper is a structured comparative review of how large language models are used to simulate human respondents and to generate and detect disinformation. It compares four empirical studies (Aher et al. 2023; Santurkar et al. 2023; Vykopal et al. 2024; Gaeta et al. 2025) along a common set of dimensions, and it adds a small experiment: a replication of the wisdom-of-crowds Turing Experiment with Qwen2.5-0.5B (base vs. instruct). In this setting, instruction tuning alone did not produce the hyper-accuracy distortion. Exact answers were 4.0 % for the base model and 1.4 % / 1.0 % for the instruct model.

## Structure
| Path | Content |
|---|---|
| `Adavanced2_PG4_Somashekar_Sowrabha.pdf` | final paper |
| `main.tex` | main document |
| `sections/` | one file per section |
| `tables/`, `figures/` | comparison table, framework figure, plots and plotting script |
| `appendix/` | contribution summary and AI-use statement |
| `references.bib` | bibliography |
| `declaration_prefilled.*` | declaration of authorship |
| `check_paper.py` | formal checks (page count, references, citations) |

## Build
```bash
pdflatex main && bibtex main && pdflatex main && pdflatex main
python check_paper.py
```
Requires a LaTeX distribution (TeX Live / MiKTeX) and Python with `pypdf`.
