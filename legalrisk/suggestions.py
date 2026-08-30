"""
legalrisk/suggestions.py

Given a clause type and a detected risk "issue" (the same explanation
strings already produced by flask_analyzer.CLAUSE_RULES), returns a
concrete, safer redraft of the clause plus a short rationale.

- Suggestions are stored in data/clause_suggestions.json, keyed by clause
  type, so the dataset can be reviewed/edited/extended by hand.
- If an issue is encountered that is not yet in the dataset (e.g. a new
  risk rule was added to CLAUSE_RULES, or an unusual clause triggered a
  free-text issue), a generic, clause-type-appropriate fallback is
  generated automatically AND appended to the JSON file, tagged
  "source": "auto-generated" so it is available immediately next time
  and can be reviewed/refined later.
"""
from __future__ import annotations

import json
import threading
from pathlib import Path

DATA_PATH = Path(__file__).resolve().parent.parent / "data" / "clause_suggestions.json"

_lock = threading.Lock()

# Fallback advice used only when nothing in the dataset matches AND the
# clause type itself has no generic template below. Kept intentionally
# generic and clearly marked as unreviewed.
_DEFAULT_FALLBACK = (
    "Rewrite this clause so the obligation is mutual (applies equally to both parties), "
    "time-bound (has a clear start/end or cap), and subject to reasonable exceptions. "
    "Avoid absolute words such as 'all', 'any', 'sole discretion', 'immediately', and "
    "'in perpetuity' unless a specific, negotiated reason requires them."
)

# One generic template per clause type, used to generate a fallback
# suggestion when a specific issue isn't found in the dataset yet.
_GENERIC_TEMPLATES = {
    "Limitation of Liability": "Introduce an aggregate liability cap (e.g. fees paid in the "
        "preceding 6–12 months) with standard carve-outs for fraud, gross negligence, wilful "
        "misconduct, confidentiality breaches, and IP infringement.",
    "Indemnification": "Make the indemnity mutual and fault-based: each party indemnifies the "
        "other only for losses caused by its own breach, negligence, or wilful misconduct, "
        "subject to prompt notice and a right to participate in the defence.",
    "Termination": "Require written notice and a reasonable cure period (15–30 days) before "
        "termination or suspension, and give both parties a symmetrical right to terminate for "
        "convenience on reasonable notice (e.g. 30–60 days).",
    "Governing Law": "Specify the laws of India and a domestic court or arbitration seat so "
        "disputes can be resolved without the cost of a foreign forum.",
    "Confidentiality": "Make confidentiality mutual, add standard exceptions (already public, "
        "independently developed, required by law), and set a fixed survival period (e.g. 3–5 "
        "years) instead of an indefinite one.",
    "Intellectual Property": "Separate pre-existing/background IP (retained by its owner) from "
        "newly created, paid-for deliverables (assigned to the paying customer), and grant only "
        "the licences actually needed to use the service.",
    "Data Protection": "Require a lawful basis for processing, limit third-party sharing to what "
        "is necessary under an equivalent data-processing agreement, set a defined retention/"
        "deletion period, and keep security-incident liability tied to a reasonable standard of care.",
    "Payment": "Limit fee increases and late-payment interest to reasonable, clearly stated "
        "figures, require notice before any change, and allow a pro-rata refund where termination "
        "results from the other party's failure to perform.",
    "Warranty": "Include a baseline warranty (reasonable skill and care, conformance to "
        "specification, non-infringement) rather than disclaiming all warranties or providing the "
        "service strictly 'as is'.",
    "Data Return and Exit": "Guarantee a minimum data-retrieval window after termination (e.g. 30 "
        "days), export in a common machine-readable format, and fix the timetable/cost of "
        "transition assistance in advance.",
    "Service Levels": "Add measurable commitments (uptime percentage, response/resolution times) "
        "and ensure service credits are not the customer's only remedy for repeated failures.",

    # --- Real Estate and Property Documents ---
    "Rent and Security Deposit": "State a clear, itemised refund process for the security deposit "
        "(e.g. within 30–60 days, less documented deductions for damage beyond normal wear and tear) "
        "rather than treating it as non-refundable or forfeitable at the landlord's discretion.",
    "Maintenance and Repairs": "Split responsibility clearly: the landlord handles structural and "
        "major repairs, the tenant handles day-to-day upkeep and damage it causes, with reasonable "
        "wear and tear excluded from tenant liability.",
    "Termination and Eviction": "Require written notice and a reasonable notice period (e.g. 30–60 "
        "days) before termination, and limit eviction to a lawful process (court order/due process) "
        "rather than allowing immediate, unilateral eviction.",
    "Renewal and Rent Escalation": "Cap rent increases to a stated percentage per renewal term and "
        "require advance written notice, rather than leaving increases to unilateral discretion.",
    "Use of Premises and Subletting": "Allow subletting with the landlord's prior written consent, "
        "which shall not be unreasonably withheld, instead of prohibiting it outright.",

    # --- Estate Planning Documents ---
    "Executor and Administration": "Require the executor to provide a periodic accounting to "
        "beneficiaries and consider naming a co-executor or requiring a bond, rather than granting "
        "unchecked, unaccountable discretion.",
    "Beneficiaries and Bequests": "Name contingent (backup) beneficiaries for each bequest in case a "
        "primary beneficiary predeceases the testator, and specify how the residuary estate should "
        "be divided rather than leaving it to discretion.",
    "Revocation": "Include an express revocation clause stating that all prior wills and codicils "
        "are revoked, to avoid conflicting instructions across multiple documents.",
    "Power of Attorney Scope": "Define the agent's authority with specific, enumerated powers and "
        "require periodic accounting to a named third party, rather than granting unlimited, "
        "unsupervised authority.",
    "Witness and Execution": "Ensure execution follows the applicable jurisdiction's formalities — "
        "typically two independent witnesses and/or notarisation — rather than a single witness.",

    # --- Court and Litigation Pleadings ---
    "Parties and Jurisdiction": "Clearly identify each party's full name, address, and role, and "
        "plead the specific facts establishing why this court has jurisdiction over the matter.",
    "Relief Sought": "State the specific relief sought (e.g. a quantified damages figure, specific "
        "performance, or a named declaration) rather than leaving the prayer vague or unspecified.",
    "Service of Process": "Attach or reference proof of proper service (affidavit/acknowledgment of "
        "service) to avoid later challenges to the court's ability to proceed.",
    "Limitation Period": "Plead the specific date the cause of action arose and confirm the filing "
        "falls within the applicable limitation period, or explain any exception that saves the claim.",
}


def _load() -> dict:
    if DATA_PATH.exists():
        try:
            return json.loads(DATA_PATH.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            return {}
    return {}


def _save(data: dict) -> None:
    DATA_PATH.parent.mkdir(parents=True, exist_ok=True)
    DATA_PATH.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def get_suggestion(clause_type: str, issue: str) -> dict:
    """
    Look up a redraft suggestion for a given clause_type + risk issue.
    Creates and persists a generic fallback the first time an unseen
    issue is encountered, so the dataset grows over time.
    """
    issue_norm = issue.strip().lower()

    with _lock:
        data = _load()
        entries = data.get(clause_type, [])

        for entry in entries:
            if entry.get("issue", "").strip().lower() == issue_norm:
                return entry

        # Not found -> build a fallback, tailored to the clause type if we
        # have a template, otherwise a fully generic one.
        fallback = {
            "issue": issue,
            "suggested_clause": _GENERIC_TEMPLATES.get(clause_type, _DEFAULT_FALLBACK),
            "rationale": "Auto-generated general-purpose guidance based on the clause category; "
                         "recommend legal review before adopting this wording verbatim.",
            "source": "auto-generated",
        }

        entries.append(fallback)
        data[clause_type] = entries
        _save(data)
        return fallback


def get_suggestions_for_hits(clause_type: str, risky_hits: list[str]) -> list[dict]:
    """Convenience wrapper: resolve a suggestion for every risky_hit explanation."""
    return [get_suggestion(clause_type, hit) for hit in risky_hits]
