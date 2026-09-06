"""
legalrisk/document_builder.py

Turns a report produced by legalrisk.flask_analyzer.analyse() back into a
full document — but with every risky clause's text replaced by its
suggested, safer rewording, and a new section appended covering any
required clause type that was missing entirely.

This is what powers the "generate a revised agreement" feature: apply the
suggestions, re-run analyse() on the result, and show that the score drops.

Two important limits, stated plainly rather than hidden:
- If a clause has multiple risky_hits, only the FIRST suggestion is used as
  the full replacement text (stacking multiple full redraft suggestions on
  top of each other tends to produce a run-on, less usable paragraph).
- A clause classified as "favors_you" is never replaced — it's not risky
  for the selected perspective, so there's nothing to fix.
"""
from __future__ import annotations


def build_revised_text(report: dict) -> str:
    """
    Reconstructs a full document from report["clauses"] (every original
    clause, in order), replacing risky clause text with its suggested
    rewording, and appending a new section per missing required clause.

    Every clause — replaced, kept as-is, or newly added — is written with
    a fresh "N. HEADING" numbering applied uniformly across the whole
    output. This matters for two reasons: it makes the result read as one
    coherent renumbered document, and it keeps every clause boundary
    detectable if this text is fed back through segment_clauses(), which
    looks specifically for numbered/lettered markers (e.g. "1. ", "A) ") —
    a bare, unnumbered heading is invisible to it and would silently merge
    adjacent clauses together on re-analysis.
    """
    lines: list[str] = []
    counter = 1

    for clause in report.get("clauses", []):
        if clause["type"] == "Other":
            # No recognised clause type (e.g. a title or intro paragraph)
            # — keep exactly as-is, unnumbered.
            lines.append(clause["text"].strip())
            continue

        # Drop the clause's own original heading line (which carried its
        # own, possibly differently-styled numbering) so we can apply one
        # consistent scheme across the whole document instead.
        _, _, body_only = clause["text"].partition("\n")
        body_only = body_only.strip() or clause["text"].strip()

        if clause["risky_hits"] and not clause["favors_you"] and clause["suggestions"]:
            body = clause["suggestions"][0]["suggested_clause"]
        else:
            body = body_only

        lines.append(f"{counter}. {clause['type'].upper()}\n{body}")
        counter += 1

    missing = report.get("missing", [])
    if missing:
        lines.append(f"{counter}. ADDITIONAL CLAUSES (added to address gaps identified in the original review)")
        counter += 1
        for item in missing:
            suggestion = item.get("suggestion")
            body = suggestion["suggested_clause"] if suggestion else (
                f"[No specific {item['type']} provision was present in the original "
                "document; a clause covering this should be added and reviewed by counsel.]"
            )
            lines.append(f"{counter}. {item['type'].upper()} (added)\n{body}")
            counter += 1

    return "\n\n".join(lines)
