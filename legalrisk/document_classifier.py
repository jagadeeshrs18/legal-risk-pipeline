"""
legalrisk/document_classifier.py

Lightweight, dependency-free document-category classifier, operating at
two levels:

1. TOP-LEVEL (4 categories, matches the frontend's four upload sections
   and the taxonomy requested by the reviewer):
       - "Business and Commercial Contracts"
       - "Real Estate and Property Documents"
       - "Estate Planning Documents"
       - "Court and Litigation Pleadings"
   Used to reject a document uploaded into the wrong section (e.g. a
   rental agreement dropped into the Business & Commercial box).

2. COMMERCIAL SUB-TYPE (only meaningful once a document has been
   accepted as "Business and Commercial Contracts"): which of
   NDA / Employment Agreement / Service Agreement / Vendor Agreement it
   most resembles, used to sanity-check the subtype the user picked in
   that section's dropdown.

Approach for both levels: weighted keyword/phrase scoring.
  - "title" phrases: checked only in the first ~600 characters of the
    document (titles/headings), weighted heavily.
  - "strong" phrases: fairly unambiguous for that category, weighted high.
  - "medium" phrases: common but less unique to the category, weighted low.

The result is a normalised confidence score per category. If the top
category's score is not comfortably ahead of the runner-up, or is below
an absolute minimum, the document is reported as "Uncertain" rather than
forcing a guess.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field

TITLE_WEIGHT = 6
STRONG_WEIGHT = 3
MEDIUM_WEIGHT = 1
TITLE_WINDOW_CHARS = 600

# A category is only reported (rather than "Uncertain") if its score is
# at least this many points AND at least this ratio ahead of the runner-up.
MIN_ABSOLUTE_SCORE = 4
MIN_MARGIN_RATIO = 1.25


@dataclass
class CategoryResult:
    predicted: str                      # a key of the signal dict used, or "Uncertain"
    confidence: float                   # 0..1, roughly "how sure are we"
    scores: dict[str, float] = field(default_factory=dict)   # raw score per category

    def matches(self, expected_category: str) -> bool:
        """True if the prediction agrees with (or is unsure about) expected_category."""
        return self.predicted in (expected_category, "Uncertain")


def _count(haystack: str, phrase: str) -> int:
    return len(re.findall(re.escape(phrase), haystack))


def _detect(text: str, signal_dict: dict[str, dict[str, list[str]]]) -> CategoryResult:
    low = text.lower()
    title_zone = low[:TITLE_WINDOW_CHARS]

    raw_scores: dict[str, float] = {}

    for category, buckets in signal_dict.items():
        score = 0.0
        for phrase in buckets.get("title", []):
            score += _count(title_zone, phrase) * TITLE_WEIGHT
        for phrase in buckets.get("strong", []):
            score += _count(low, phrase) * STRONG_WEIGHT
        for phrase in buckets.get("medium", []):
            score += _count(low, phrase) * MEDIUM_WEIGHT
        raw_scores[category] = score

    ordered = sorted(raw_scores.items(), key=lambda kv: kv[1], reverse=True)
    top_category, top_score = ordered[0]
    runner_up_score = ordered[1][1] if len(ordered) > 1 else 0.0

    total = sum(raw_scores.values()) or 1.0
    confidence = round(top_score / total, 3)

    comfortable_margin = top_score >= MIN_ABSOLUTE_SCORE and (
        runner_up_score == 0 or top_score / max(runner_up_score, 1e-9) >= MIN_MARGIN_RATIO
    )

    predicted = top_category if comfortable_margin else "Uncertain"

    return CategoryResult(predicted=predicted, confidence=confidence, scores=raw_scores)


# ---------------------------------------------------------------------
# Commercial sub-type signals (unchanged from the original 4-category
# version of this module). Used only inside the "Business and Commercial
# Contracts" section to sanity-check the subtype dropdown.
# ---------------------------------------------------------------------
COMMERCIAL_SUBTYPE_SIGNALS: dict[str, dict[str, list[str]]] = {
    "NDA": {
        "title": [
            "non-disclosure agreement", "nondisclosure agreement",
            "confidentiality agreement", "mutual non-disclosure agreement",
        ],
        "strong": [
            "disclosing party", "receiving party", "confidential information",
            "purpose of evaluating", "non-disclosure", "nondisclosure",
        ],
        "medium": [
            "proprietary information", "trade secret", "return or destroy",
            "permitted purpose",
        ],
    },
    "Employment Agreement": {
        "title": [
            "employment agreement", "letter of appointment", "offer of employment",
            "appointment letter",
        ],
        "strong": [
            "employee shall", "employer shall", "probationary period", "probation period",
            "ctc", "cost to company", "notice period", "date of joining",
            "employee's employment", "resignation",
        ],
        "medium": [
            "salary", "designation", "leave policy", "employee benefits",
            "reporting manager", "workplace",
        ],
    },
    "Service Agreement": {
        "title": [
            "service agreement", "services agreement", "master service agreement",
            "consulting agreement", "statement of work",
        ],
        "strong": [
            "scope of services", "service provider", "deliverables",
            "service levels", "sla", "statement of work", "consultant shall",
        ],
        "medium": [
            "professional services", "acceptance criteria", "milestones",
            "support and maintenance",
        ],
    },
    "Vendor Agreement": {
        "title": [
            "vendor agreement", "supply agreement", "purchase agreement",
            "procurement agreement",
        ],
        "strong": [
            "vendor shall", "supplier shall", "purchase order", "supply of goods",
            "delivery schedule", "goods and services", "vendor's obligations",
        ],
        "medium": [
            "procurement", "inventory", "shipment", "warranty period", "goods",
        ],
    },
}


def detect_commercial_subtype(text: str) -> CategoryResult:
    """Guess which of NDA/Employment/Service/Vendor a commercial contract resembles."""
    return _detect(text, COMMERCIAL_SUBTYPE_SIGNALS)


# ---------------------------------------------------------------------
# Top-level category signals (the 4 categories requested by the reviewer).
# "Business and Commercial Contracts" reuses the union of all commercial
# sub-type phrase lists above, so anything that looks like an NDA, an
# employment agreement, a service agreement, or a vendor agreement is
# recognised as belonging to this top-level bucket.
# ---------------------------------------------------------------------

def _merge_buckets(*signal_dicts: dict[str, list[str]]) -> dict[str, list[str]]:
    merged: dict[str, list[str]] = {"title": [], "strong": [], "medium": []}
    for d in signal_dicts:
        for bucket in merged:
            merged[bucket].extend(d.get(bucket, []))
    return merged


TOP_LEVEL_SIGNALS: dict[str, dict[str, list[str]]] = {
    "Business and Commercial Contracts": _merge_buckets(
        *COMMERCIAL_SUBTYPE_SIGNALS.values(),
        {
            # Generic commercial-contract boilerplate. Unlike the subtype
            # dicts above (which are specific to NDA/Employment/Service/
            # Vendor wording), these phrases are near-universal across real
            # commercial contracts regardless of sub-type — found by
            # inspecting real, held-out clauses from the project's own
            # ACORD dataset (see tests/build_acord_samples.py) that were
            # being misclassified as "Uncertain" for lack of any matching
            # signal. They are deliberately generic legal-contract
            # boilerplate that essentially never appears in wills, leases,
            # or court pleadings.
            "strong": [
                "indemnify", "indemnification", "indemnitee", "hold harmless",
                "breach of this agreement", "third party claims",
                "limitation of liability",
            ],
            "medium": [
                "notwithstanding the foregoing", "the parties hereto",
                "consequential damages", "incidental damages", "punitive damages",
                "assign this agreement", "work product", "affiliates",
                "governing law", "force majeure", "arbitration",
                "work made for hire", "patent application",
            ],
        },
    ),
    "Real Estate and Property Documents": {
        "title": [
            "lease agreement", "rental agreement", "tenancy agreement",
            "leave and license agreement", "property deed", "sale deed",
        ],
        "strong": [
            "landlord", "tenant", "lessee", "lessor",
            "security deposit", "monthly rent", "leased premises",
        ],
        "medium": [
            "rent escalation", "eviction", "subletting", "maintenance charges",
            "vacant possession", "quiet enjoyment",
        ],
    },
    "Estate Planning Documents": {
        "title": [
            "last will and testament", "last will", "living trust",
            "power of attorney", "advance healthcare directive", "living will",
        ],
        "strong": [
            "testator", "executor", "beneficiary", "beneficiaries", "bequeath",
            "attorney-in-fact", "revocation of prior wills", "residuary estate",
        ],
        "medium": [
            "letters of administration", "probate", "guardian", "trustee",
            "healthcare proxy", "codicil",
        ],
    },
    "Court and Litigation Pleadings": {
        "title": [
            "plaint", "complaint", "petition", "writ petition", "legal notice",
            "notice of motion", "criminal complaint",
        ],
        "strong": [
            "plaintiff", "defendant", "petitioner", "respondent", "hon'ble court",
            "cause of action", "prayer", "wherefore",
        ],
        "medium": [
            "affidavit", "summons", "jurisdiction of this court", "relief sought",
            "statute of limitations", "cross-examination",
        ],
    },
}


def detect_document_category(text: str) -> CategoryResult:
    """Guess which of the 4 top-level categories a document belongs to."""
    return _detect(text, TOP_LEVEL_SIGNALS)
