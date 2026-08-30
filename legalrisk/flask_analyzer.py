from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

import faiss
import fitz
from sentence_transformers import SentenceTransformer

from .beir import load_beir
from .suggestions import get_suggestions_for_hits
from .domain_rules import (
    REAL_ESTATE_HEADING_ALIASES, REAL_ESTATE_CLAUSE_RULES,
    ESTATE_HEADING_ALIASES, ESTATE_CLAUSE_RULES,
    LITIGATION_HEADING_ALIASES, LITIGATION_CLAUSE_RULES,
)


# ============================================================
# Clause heading aliases
# ============================================================

COMMERCIAL_HEADING_ALIASES = {
    "Limitation of Liability": [
        "limitation of liability",
        "limits of liability",
        "liability limitation",
        "liability cap",
    ],
    "Indemnification": [
        "indemnification",
        "indemnity",
        "indemnities",
    ],
    "Termination": [
        "termination",
        "term and termination",
        "suspension and termination",
    ],
    "Governing Law": [
        "governing law",
        "jurisdiction",
        "applicable law",
        "dispute resolution",
    ],
    "Confidentiality": [
        "confidentiality",
        "confidential information",
        "non-disclosure",
        "nondisclosure",
    ],
    "Intellectual Property": [
        "intellectual property",
        "ownership",
        "licence and ownership",
        "license and ownership",
        "proprietary rights",
    ],
    "Data Protection": [
        "data protection",
        "privacy",
        "personal data",
        "data security",
        "information security",
    ],
    "Payment": [
        "payment",
        "fees and payment",
        "fees",
        "pricing",
        "charges",
    ],
    "Warranty": [
        "warranty",
        "warranties",
        "disclaimer of warranties",
    ],
    "Data Return and Exit": [
        "data return",
        "data return and exit",
        "exit management",
        "transition assistance",
        "data portability",
    ],
    "Service Levels": [
        "service level",
        "service levels",
        "service availability",
        "support and maintenance",
    ],
}


# ============================================================
# Risk rules
#
# Format:
# (regular-expression, explanation, points)
# ============================================================

COMMERCIAL_CLAUSE_RULES = {
    "Limitation of Liability": {
        "required": True,
        "risk": [
            (
                r"unlimited liability",
                "The clause may impose unlimited liability.",
                35,
            ),
            (
                r"liable for all (?:losses|damages|claims)",
                "The clause uses broad liability language covering all losses.",
                28,
            ),
            (
                r"without (?:any )?limitation",
                "The obligation is expressed without an identifiable limitation.",
                30,
            ),
            (
                r"liability.{0,100}(?:one|1)\s+month",
                "The liability cap appears to be limited to only one month of fees.",
                35,
            ),
            (
                r"fees paid.{0,100}(?:one|1)\s+month",
                "The liability cap is linked to only one month of fees.",
                35,
            ),
            (
                r"shall not be liable.{0,150}(?:data loss|security incident|data breach)",
                "Liability for data loss or security incidents appears to be excluded.",
                28,
            ),
            (
                r"shall not be liable.{0,150}(?:regulatory penalties|regulatory fines)",
                "Liability for regulatory penalties appears to be excluded.",
                24,
            ),
            (
                r"exclude[sd]?.{0,100}(?:all|any).{0,40}(?:indirect|consequential)",
                "The exclusion of indirect or consequential loss may be excessively broad.",
                16,
            ),
        ],
        "protective": [
            r"aggregate liability.{0,100}(?:shall not exceed|limited to)",
            r"(?:six|6|twelve|12)\s+months?.{0,50}fees",
            r"fraud",
            r"gross negligence",
            r"wilful misconduct|willful misconduct",
        ],
        "missing_points": 28,
    },

    "Indemnification": {
        "required": True,
        "risk": [
            (
                r"(?:customer|client|buyer).{0,80}(?:defend and indemnify|indemnify)",
                "The customer is required to provide an indemnity.",
                22,
            ),
            (
                r"vendor provides no corresponding indemnity",
                "The indemnity is expressly one-sided in favour of the vendor.",
                38,
            ),
            (
                r"no corresponding indemnity",
                "No reciprocal indemnity is provided by the other party.",
                35,
            ),
            (
                r"indemnif(?:y|ication).{0,150}all "
                r"(?:claims|losses|damages|penalties|expenses)",
                "The indemnity covers an unusually broad range of claims and losses.",
                28,
            ),
            (
                r"regulatory investigation",
                "The indemnity extends to regulatory investigations.",
                20,
            ),
            (
                r"regardless of fault",
                "The indemnity may apply regardless of fault.",
                30,
            ),
            (
                r"sole discretion",
                "A party may control an indemnity-related decision at its sole discretion.",
                16,
            ),
        ],
        "protective": [
            r"mutual(?:ly)? indemn",
            r"each party.{0,100}indemn",
            r"prompt written notice",
            r"control of the defen[cs]e",
            r"reasonable settlement",
        ],
        "missing_points": 22,
    },

    "Termination": {
        "required": True,
        "risk": [
            (
                r"automatically renews?.{0,100}(?:12|24|36)[-\s]?month",
                "The agreement automatically renews for a lengthy additional term.",
                22,
            ),
            (
                r"(?:90|120|180)\s+days?.{0,80}(?:notice|before)",
                "The customer must provide an unusually long non-renewal notice.",
                22,
            ),
            (
                r"vendor may (?:suspend|terminate).{0,70}immediately",
                "The vendor may suspend or terminate immediately.",
                25,
            ),
            (
                r"suspend.{0,100}(?:suspected misuse|delayed payment)",
                "Service may be suspended based on suspected misuse or delayed payment.",
                22,
            ),
            (
                r"customer may terminate only",
                "The customer's termination right is materially restricted.",
                24,
            ),
            (
                r"(?:60|90)\s*[- ]?day cure period",
                "The clause imposes a lengthy cure period before termination.",
                18,
            ),
            (
                r"terminate.{0,60}(?:at any time|without cause|without notice)",
                "A party may terminate without cause or adequate notice.",
                28,
            ),
            (
                r"immediate termination",
                "The clause permits immediate termination.",
                24,
            ),
        ],
        "protective": [
            r"either party.{0,80}terminate",
            r"thirty \(?30\)? days",
            r"30 days",
            r"reasonable cure period",
            r"material breach",
        ],
        "missing_points": 18,
    },

    "Governing Law": {
        "required": True,
        "risk": [
            (
                r"exclusive jurisdiction.{0,100}"
                r"(?:united states|delaware|new york|foreign court)",
                "The agreement requires disputes to be handled in a foreign jurisdiction.",
                24,
            ),
            (
                r"governed by.{0,60}(?:delaware|new york|california)",
                "The selected governing law may create additional cost for an Indian party.",
                18,
            ),
        ],
        "protective": [
            r"laws of india",
            r"courts? (?:at|in).{0,60}india",
            r"arbitration and conciliation act",
        ],
        "missing_points": 14,
    },

    "Confidentiality": {
        "required": True,
        "risk": [
            (
                r"in perpetuity",
                "The confidentiality obligation continues indefinitely.",
                18,
            ),
            (
                r"all information.{0,100}confidential",
                "The definition of confidential information may be excessively broad.",
                16,
            ),
            (
                r"without exception",
                "The confidentiality obligation does not appear to contain exceptions.",
                20,
            ),
            (
                r"confidentiality.{0,100}(?:unilateral|one-sided)",
                "The confidentiality obligation may be one-sided.",
                22,
            ),
        ],
        "protective": [
            r"already (?:known|in possession)",
            r"independently developed",
            r"publicly available|public domain",
            r"lawfully received",
            r"required by law",
        ],
        "missing_points": 18,
    },

    "Intellectual Property": {
        "required": True,
        "risk": [
            (
                r"all intellectual property.{0,120}(?:assign|belong)",
                "The clause may assign all intellectual property to one party.",
                30,
            ),
            (
                r"irrevocabl[ey].{0,100}perpetual",
                "The licence appears irrevocable and perpetual.",
                25,
            ),
            (
                r"(?:customer|client) data.{0,100}(?:owned by|belongs to).{0,40}vendor",
                "Customer data or related rights may be assigned to the vendor.",
                35,
            ),
            (
                r"vendor.{0,100}all rights.{0,100}(?:output|deliverable)",
                "The vendor retains broad rights over project outputs or deliverables.",
                26,
            ),
        ],
        "protective": [
            r"pre-existing intellectual property",
            r"background intellectual property",
            r"customer retains ownership",
            r"limited licen[cs]e",
        ],
        "missing_points": 24,
    },

    "Data Protection": {
        "required": False,
        "risk": [
            (
                r"share personal data.{0,100}(?:any|third part)",
                "Personal data may be shared broadly with third parties.",
                30,
            ),
            (
                r"personal data.{0,80}without consent",
                "Personal data may be processed or shared without consent.",
                32,
            ),
            (
                r"no liability.{0,100}(?:data breach|security incident)",
                "The vendor disclaims liability for data-security incidents.",
                30,
            ),
            (
                r"retain.{0,80}(?:personal data|customer data).{0,80}indefinitely",
                "The clause may permit indefinite retention of personal data.",
                26,
            ),
        ],
        "protective": [
            r"digital personal data protection",
            r"personal data",
            r"security measures",
            r"data breach",
            r"reasonable security",
            r"data processor|data fiduciary",
        ],
        "missing_points": 20,
    },

    "Payment": {
        "required": True,
        "risk": [
            (
                r"non-refundable",
                "Payments are described as non-refundable.",
                20,
            ),
            (
                r"unilateral(?:ly)? (?:change|revise|increase).{0,40}(?:fee|price)",
                "One party may unilaterally revise the fees.",
                24,
            ),
            (
                r"interest.{0,40}(?:2%|3%|4%|5%).{0,30}(?:month|monthly)",
                "The late-payment interest rate is high when calculated monthly.",
                24,
            ),
            (
                r"compounded monthly",
                "Late-payment interest is compounded monthly.",
                16,
            ),
            (
                r"fees paid.{0,100}non-refundable.{0,100}service failure",
                "Fees remain non-refundable even where termination results from service failure.",
                32,
            ),
        ],
        "protective": [
            r"valid invoice",
            r"payment.{0,40}(?:days|business days)",
            r"disputed amount",
            r"refund.{0,100}service failure",
        ],
        "missing_points": 16,
    },

    "Warranty": {
        "required": True,
        "risk": [
            (
                r"[\"']?as is[\"']?",
                "The services are provided on an 'as-is' basis.",
                24,
            ),
            (
                r"[\"']?as available[\"']?",
                "The services are provided only on an 'as-available' basis.",
                18,
            ),
            (
                r"disclaims? all warranties",
                "The vendor disclaims all warranties.",
                32,
            ),
            (
                r"disclaims?.{0,100}(?:accuracy|fitness for purpose|non-infringement)",
                "Important warranties concerning accuracy, fitness or non-infringement are excluded.",
                28,
            ),
            (
                r"customer is solely responsible.{0,100}decisions",
                "The customer assumes sole responsibility for decisions based on system outputs.",
                24,
            ),
        ],
        "protective": [
            r"warrants?.{0,100}professional",
            r"reasonable skill and care",
            r"conform.{0,80}specification",
            r"materially perform",
        ],
        "missing_points": 18,
    },

    "Data Return and Exit": {
        "required": False,
        "risk": [
            (
                r"delete customer data immediately",
                "The vendor may delete customer data immediately after termination.",
                35,
            ),
            (
                r"may delete.{0,80}(?:customer data|personal data).{0,40}immediately",
                "Customer data may be deleted without a reasonable retrieval period.",
                35,
            ),
            (
                r"subject to availability",
                "Data export or transition support is not guaranteed.",
                18,
            ),
            (
                r"then-current rates",
                "Exit support may be charged at unspecified future rates.",
                18,
            ),
            (
                r"no export format.{0,80}guaranteed",
                "The agreement does not guarantee a usable data-export format.",
                26,
            ),
            (
                r"no.{0,40}transition timetable.{0,40}guaranteed",
                "No transition timetable is guaranteed.",
                20,
            ),
        ],
        "protective": [
            r"return customer data",
            r"export.{0,80}machine-readable",
            r"transition assistance",
            r"retain.{0,50}(?:30|60|90)\s+days",
        ],
        "missing_points": 18,
    },

    "Service Levels": {
        "required": False,
        "risk": [
            (
                r"no service level",
                "The agreement provides no measurable service level.",
                24,
            ),
            (
                r"no uptime guarantee",
                "The agreement does not guarantee minimum availability.",
                24,
            ),
            (
                r"sole remedy.{0,80}service credit",
                "Service credits are stated as the customer's sole remedy.",
                20,
            ),
        ],
        "protective": [
            r"uptime",
            r"service credit",
            r"response time",
            r"resolution time",
        ],
        "missing_points": 16,
    },
}


# ============================================================
# PDF extraction and clause segmentation
# ============================================================

def extract_pdf(path: Path) -> tuple[str, int]:
    document = fitz.open(path)

    try:
        pages = [
            page.get_text("text")
            for page in document
        ]
    finally:
        document.close()

    text = "\n".join(pages)

    # Remove repeated sample-page labels and normalize spacing
    text = re.sub(
        r"Sample document for PDF extraction and "
        r"risk-analysis testing\s*Page\s*\d+",
        "",
        text,
        flags=re.I,
    )

    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text).strip()

    if len(text) < 100:
        raise ValueError(
            "Very little selectable text was found. "
            "This may be a scanned PDF; run OCR first."
        )

    return text, len(pages)


def segment_clauses(text: str) -> list[str]:
    text = text.replace("\r", "\n")

    boundary = re.compile(
        r"(?m)(?=^(?:"
        r"\d+(?:\.\d+)*[.)]?"
        r"|[A-Z][.)]"
        r")\s+[A-Z])"
    )

    parts = [
        part.strip()
        for part in boundary.split(text)
        if len(part.strip()) >= 40
    ]

    if len(parts) < 3:
        parts = [
            part.strip()
            for part in re.split(r"\n\s*\n", text)
            if len(part.strip()) >= 40
        ]

    output = []

    for part in parts:
        if len(part) <= 2200:
            output.append(part)
            continue

        sentences = re.split(
            r"(?<=[.;])\s+",
            part
        )

        chunk = ""

        for sentence in sentences:
            if (
                len(chunk) + len(sentence) > 2000
                and chunk
            ):
                output.append(chunk.strip())
                chunk = ""

            chunk += sentence + " "

        if chunk.strip():
            output.append(chunk.strip())

    return output[:300]


# ============================================================
# ACORD vector retrieval
# ============================================================

class AcordRetriever:
    def __init__(
        self,
        data_dir: Path,
        cache_dir: Path,
        model_name: str = "BAAI/bge-base-en-v1.5",
    ):
        self.model_name = model_name

        self.model = SentenceTransformer(
            model_name
        )

        self.cache_dir = cache_dir
        self.cache_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

        self.index_path = (
            cache_dir / "acord_bge.index"
        )

        self.meta_path = (
            cache_dir / "acord_metadata.json"
        )

        if (
            self.index_path.exists()
            and self.meta_path.exists()
        ):
            self.index = faiss.read_index(
                str(self.index_path)
            )

            self.metadata = json.loads(
                self.meta_path.read_text(
                    encoding="utf-8"
                )
            )

        else:
            corpus, _, _ = load_beir(
                data_dir,
                "test",
            )

            ids = list(corpus)
            texts = list(corpus.values())

            vectors = self.model.encode(
                texts,
                batch_size=32,
                normalize_embeddings=True,
                show_progress_bar=True,
                convert_to_numpy=True,
            ).astype("float32")

            self.index = faiss.IndexFlatIP(
                vectors.shape[1]
            )

            self.index.add(vectors)

            self.metadata = [
                {
                    "id": document_id,
                    "text": document_text,
                }
                for document_id, document_text
                in zip(ids, texts)
            ]

            faiss.write_index(
                self.index,
                str(self.index_path),
            )

            self.meta_path.write_text(
                json.dumps(
                    self.metadata,
                    ensure_ascii=False,
                ),
                encoding="utf-8",
            )

    def search(
        self,
        clause: str,
        k: int = 3,
    ):
        return self.search_many(
            [clause],
            k=k,
        )[0]

    def search_many(
        self,
        clauses: list[str],
        k: int = 3,
    ):
        if not clauses:
            return []

        queries = [
            "Represent this sentence for searching "
            "relevant passages: " + clause
            for clause in clauses
        ]

        vectors = self.model.encode(
            queries,
            batch_size=32,
            normalize_embeddings=True,
            show_progress_bar=False,
            convert_to_numpy=True,
        ).astype("float32")

        scores, positions = self.index.search(
            vectors,
            k,
        )

        all_results = []

        for score_row, position_row in zip(
            scores,
            positions,
        ):
            clause_results = []

            for score, position in zip(
                score_row,
                position_row,
            ):
                if position < 0:
                    continue

                clause_results.append({
                    **self.metadata[int(position)],
                    "similarity": round(
                        float(score),
                        4,
                    ),
                })

            all_results.append(
                clause_results
            )

        return all_results


# ============================================================
# Clause classification
# ============================================================

def clean_heading(text: str) -> str:
    first_line = text.strip().splitlines()[0]

    first_line = re.sub(
        r"^\s*(?:"
        r"\d+(?:\.\d+)*[.)]?"
        r"|[A-Z][.)]"
        r")\s*",
        "",
        first_line,
    )

    first_line = re.sub(
        r"[^a-zA-Z ]+",
        " ",
        first_line,
    )

    return re.sub(
        r"\s+",
        " ",
        first_line,
    ).strip().lower()


RULESETS = {
    "commercial": (COMMERCIAL_HEADING_ALIASES, COMMERCIAL_CLAUSE_RULES),
    "real_estate": (REAL_ESTATE_HEADING_ALIASES, REAL_ESTATE_CLAUSE_RULES),
    "estate": (ESTATE_HEADING_ALIASES, ESTATE_CLAUSE_RULES),
    "litigation": (LITIGATION_HEADING_ALIASES, LITIGATION_CLAUSE_RULES),
}

# Maps the value the frontend sends as "contract_type" onto one of the
# rulesets above. The four original commercial sub-types all continue to
# share the single "commercial" ruleset exactly as before; the three new
# top-level categories each get their own dedicated ruleset.
CONTRACT_TYPE_RULESET = {
    "Employment Agreement": "commercial",
    "NDA": "commercial",
    "Service Agreement": "commercial",
    "Vendor Agreement": "commercial",
    "Real Estate and Property Documents": "real_estate",
    "Estate Planning Documents": "estate",
    "Court and Litigation Pleadings": "litigation",
}


def _ruleset_for(contract_type: str):
    key = CONTRACT_TYPE_RULESET.get(contract_type, "commercial")
    return RULESETS[key]


# ============================================================
# Perspective-aware scoring
# ============================================================
#
# Every risk rule above was authored from the point of view of one
# "protected" side of the relationship (e.g. the Customer in a Service
# Agreement, the Employee in an Employment Agreement, the Tenant in a
# lease, the Plaintiff in a pleading) — that is simply whose interests
# a contract-risk checklist conventionally protects. A clause flagged as
# risky for that protected side is, by construction, usually favourable
# to the other ("opposite") side of the same relationship.
#
# PERSPECTIVE_FLIP records that (protected, opposite) pair per
# contract_type. When the user selects the "opposite" side, a clause's
# risk points are excluded from the score and the finding is instead
# labelled as favourable to the selected perspective, rather than
# silently scoring identically regardless of which side is asking.
#
# NDA and Estate Planning Documents are deliberately left out: NDA
# obligations are drafted to be mutual, and estate-planning documents
# don't have a clean two-sided adversarial split the way a contract or
# a pleading does — so both remain neutral (no flip) for now.
PERSPECTIVE_FLIP = {
    "Employment Agreement": {"protected": "Employee", "opposite": "Employer"},
    "Service Agreement": {"protected": "Customer", "opposite": "Vendor"},
    "Vendor Agreement": {"protected": "Customer", "opposite": "Vendor"},
    "Real Estate and Property Documents": {"protected": "Tenant", "opposite": "Landlord"},
    "Court and Litigation Pleadings": {"protected": "Plaintiff", "opposite": "Defendant"},
}


def _perspective_multiplier(contract_type: str, perspective: str) -> float:
    """
    Returns 1.0 if this clause type's risk should count in full for the
    given perspective, or 0.0 if this contract_type's rules are written
    from the opposite side's viewpoint (i.e. the clause is actually
    favourable to the selected perspective, not risky for it).
    """
    flip = PERSPECTIVE_FLIP.get(contract_type)
    if not flip:
        return 1.0
    if perspective == flip["opposite"]:
        return 0.0
    return 1.0


def classify_rule(text: str, contract_type: str = "Service Agreement") -> str:
    heading_aliases, clause_rules = _ruleset_for(contract_type)
    heading = clean_heading(text)

    # Heading classification receives first priority
    for clause_type, aliases in heading_aliases.items():
        for alias in aliases:
            if (
                heading == alias
                or heading.startswith(alias + " ")
                or alias in heading
            ):
                return clause_type

    low = text.lower()
    scored = []

    for clause_type, rule in clause_rules.items():
        score = 0

        for alias in heading_aliases.get(
            clause_type,
            [],
        ):
            if alias in low[:300]:
                score += 5
            elif alias in low:
                score += 2

        for pattern, _, _ in rule["risk"]:
            if re.search(
                pattern,
                low,
                re.I | re.S,
            ):
                score += 3

        for pattern in rule["protective"]:
            if re.search(
                pattern,
                low,
                re.I | re.S,
            ):
                score += 2

        scored.append(
            (score, clause_type)
        )

    score, clause_type = max(scored)

    return (
        clause_type
        if score > 0
        else "Other"
    )


# ============================================================
# Risk analysis
# ============================================================

def analyse(
    text: str,
    pages: int,
    retriever: AcordRetriever,
    perspective: str,
    contract_type: str,
    jurisdiction: str,
):
    clauses = segment_clauses(text)

    heading_aliases, clause_rules = _ruleset_for(contract_type)

    # Embed all clauses in one batch
    all_precedents = retriever.search_many(
        clauses,
        k=3,
    )

    findings = []
    detected = set()

    for number, (clause, precedents) in enumerate(
        zip(clauses, all_precedents),
        1,
    ):
        clause_type = classify_rule(clause, contract_type)

        if clause_type != "Other":
            detected.add(clause_type)

        rule = clause_rules.get(
            clause_type
        )

        risky_hits = []
        protective_hits = []
        points = 0

        if rule:
            for (
                pattern,
                explanation,
                risk_points,
            ) in rule["risk"]:
                if re.search(
                    pattern,
                    clause,
                    re.I | re.S,
                ):
                    risky_hits.append(
                        explanation
                    )

                    points += risk_points

            for pattern in rule["protective"]:
                if re.search(
                    pattern,
                    clause,
                    re.I | re.S,
                ):
                    protective_hits.append(
                        pattern
                    )

            # A limited reduction for meaningful protections
            if protective_hits and points:
                points -= min(
                    8,
                    len(protective_hits) * 2,
                )

        points = max(
            0,
            min(points, 50),
        )

        # Perspective-aware scoring: if this clause type's risk rules are
        # written from the opposite side's viewpoint to the selected
        # perspective, the clause is favourable to the user rather than
        # risky for them, so it should not count against the score.
        multiplier = _perspective_multiplier(contract_type, perspective)
        raw_points = points
        effective_points = round(points * multiplier)
        favors_you = multiplier == 0.0 and raw_points > 0

        confidence = max(
            (
                item["similarity"]
                for item in precedents
            ),
            default=0,
        )

        # Display risky clauses and sufficiently similar precedents.
        # Similarity alone does not increase risk points.
        if raw_points > 0 or confidence >= 0.72:
            suggestions = (
                get_suggestions_for_hits(clause_type, risky_hits)
                if risky_hits and not favors_you else []
            )
            findings.append({
                "number": number,
                "type": clause_type,
                "text": clause,
                "score": effective_points,
                "raw_score": raw_points,
                "favors_you": favors_you,
                "risky_hits": risky_hits,
                "protective_hits": protective_hits,
                "confidence": confidence,
                "precedents": precedents,
                "suggestions": suggestions,
            })

    missing = []

    if contract_type in {
        "Real Estate and Property Documents",
        "Estate Planning Documents",
        "Court and Litigation Pleadings",
    }:
        # New, non-commercial categories: every clause type flagged
        # "required" in that category's own ruleset must be present.
        always_required = {
            clause_type
            for clause_type, rule in clause_rules.items()
            if rule.get("required")
        }
    else:
        always_required = {
            "Limitation of Liability",
            "Indemnification",
            "Termination",
            "Governing Law",
            "Confidentiality",
            "Intellectual Property",
            "Payment",
            "Warranty",
        }

        if contract_type in {
            "Service Agreement",
            "Vendor Agreement",
        }:
            always_required.update({
                "Data Protection",
                "Data Return and Exit",
                "Service Levels",
            })

        if contract_type == "NDA":
            always_required = {
                "Confidentiality",
                "Governing Law",
                "Termination",
            }

        if contract_type == "Employment Agreement":
            always_required = {
                "Confidentiality",
                "Intellectual Property",
                "Termination",
                "Governing Law",
                "Payment",
            }

    for clause_type in always_required:
        if clause_type in detected:
            continue

        rule = clause_rules[clause_type]

        missing.append({
            "type": clause_type,
            "score": rule["missing_points"],
            "reason": (
                f"No identifiable {clause_type} "
                "provision was detected."
            ),
        })

    # Only actual risk findings are used in scoring.
    # Zero-point ACORD similarity findings do not dilute the score.
    active_scores = [
        finding["score"]
        for finding in findings
        if finding["score"] > 0
    ]

    missing_scores = [
        item["score"]
        for item in missing
    ]

    all_risk_scores = (
        active_scores
        + missing_scores
    )

    if not all_risk_scores:
        overall = 0

    else:
        all_risk_scores.sort(
            reverse=True
        )

        highest_risk = (
            all_risk_scores[0]
        )

        additional_risk = (
            sum(all_risk_scores[1:])
            * 0.55
        )

        overall = min(
            100,
            round(
                highest_risk
                + additional_risk
            ),
        )

    if overall >= 80:
        level = "Critical"
    elif overall >= 60:
        level = "High"
    elif overall >= 30:
        level = "Medium"
    else:
        level = "Low"

    return {
        "report_id": hashlib.sha256(
            text[:10000].encode()
        ).hexdigest()[:16],
        "pages": pages,
        "characters": len(text),
        "clause_count": len(clauses),
        "perspective": perspective,
        "contract_type": contract_type,
        "jurisdiction": jurisdiction,
        "overall_score": overall,
        "level": level,
        "findings": sorted(
            findings,
            key=lambda item: (
                item["score"],
                item["confidence"],
            ),
            reverse=True,
        ),
        "missing": sorted(
            missing,
            key=lambda item: item["score"],
            reverse=True,
        ),
    }