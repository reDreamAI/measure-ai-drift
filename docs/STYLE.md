# Writing Style Guide

Rules for all `.md` files in this project. Referenced from `CLAUDE.md`.

This guide distinguishes between **project docs** (master.md, decision docs, CLAUDE.md) and **thesis-facing docs** (thesis_outline.md, thesis_proposal.md, anything feeding into the final thesis).

## Punctuation (all files)

- No em-dashes (`—`), double-dashes (`--`), or semicolons (`;`)
- Exception: semicolons in citation parentheses `(Author, 2023; Author, 2024)` are fine
- Use `:` for definitions, `,` for clause breaks, `→` for flow/causal relationships, `-` for headings
- Use `\-` for content lines that should render as plain text, not bullet points

## Project Docs (master.md, decision docs, CLAUDE.md)

- Active voice, direct tone
- Contractions are fine ("don't", "isn't")
- Plain words: "uses" not "leverages", "shows" not "demonstrates"
- Cut filler: no "it should be noted", "it is worth noting", "as previously discussed"
- Short paragraphs, max 4-5 sentences

## Thesis-Facing Docs (thesis_outline.md, thesis_proposal.md)

- Formal academic register
- No contractions ("do not" instead of "don't")
- Passive voice where conventional ("the metric is computed" rather than "we compute the metric")
- Precise terminology is expected, but avoid gratuitous jargon
- "This study", "the proposed framework" over "we" where appropriate
- Still avoid genuinely empty filler ("it is important to note that"), but standard academic phrasing is fine

## Structure (all files)

- One idea per bullet point
- Tables over long lists when comparing 3+ items with multiple attributes
- Bold for key terms on first use, then plain text

## Things to Avoid (all files)

- Starting multiple consecutive sentences with "This" or "It"
- Stacking adjectives: "robust, scalable, efficient framework" → pick the one that matters most
- Repeating the same information in different words within the same section
- Adding qualifiers that don't add meaning: "quite", "rather", "somewhat", "fairly"
