"""
legalrisk/domain_rules.py

Clause heading aliases + risk rules for the three non-commercial document
categories: Real Estate & Property Documents, Estate Planning Documents,
and Court & Litigation Pleadings.

Structure mirrors legalrisk/flask_analyzer.py's HEADING_ALIASES/CLAUSE_RULES
exactly, so the same classify_rule()/analyse() engine can drive all four
categories:

    HEADING_ALIASES[clause_type] -> list[str] heading phrases
    CLAUSE_RULES[clause_type] -> {
        "required": bool,
        "risk": [(regex_pattern, explanation, points), ...],
        "protective": [regex_pattern, ...],
        "missing_points": int,
    }
"""
from __future__ import annotations

# ============================================================
# Real Estate and Property Documents (rental / lease agreements)
# ============================================================

REAL_ESTATE_HEADING_ALIASES = {
    "Rent and Security Deposit": [
        "rent and security deposit", "security deposit", "monthly rent", "advance rent",
    ],
    "Maintenance and Repairs": [
        "maintenance and repairs", "repairs and maintenance", "upkeep of premises",
    ],
    "Termination and Eviction": [
        "termination and eviction", "termination of tenancy", "eviction", "lock-in period",
    ],
    "Renewal and Rent Escalation": [
        "renewal", "rent escalation", "rent increase", "renewal of lease",
    ],
    "Use of Premises and Subletting": [
        "use of premises", "permitted use", "subletting", "sub-letting",
    ],
    "Governing Law": [
        "governing law", "jurisdiction", "applicable law",
    ],
}

REAL_ESTATE_CLAUSE_RULES = {
    "Rent and Security Deposit": {
        "required": True,
        "risk": [
            (r"security deposit.{0,80}non-?refundable",
             "The security deposit is described as non-refundable regardless of the condition of the property.", 26),
            (r"deposit.{0,80}(?:forfeit|forfeited)",
             "The security deposit may be forfeited without a clear justification.", 22),
            (r"advance rent.{0,60}non-?refundable",
             "Advance rent payments may not be refunded if the tenancy ends early.", 18),
            (r"deposit.{0,80}(?:sole discretion|as (?:the )?landlord (?:deems|sees) fit)",
             "Deductions from the deposit may be made at the landlord's sole discretion.", 20),
        ],
        "protective": [
            r"refund.{0,80}deposit.{0,60}(?:days|weeks)",
            r"deduction[s]?.{0,60}itemi[sz]ed",
            r"reasonable wear and tear",
        ],
        "missing_points": 22,
    },
    "Maintenance and Repairs": {
        "required": False,
        "risk": [
            (r"tenant.{0,100}(?:sole responsibility|solely responsible).{0,60}(?:repairs|maintenance)",
             "The tenant may bear sole responsibility for all repairs, including structural issues.", 24),
            (r"landlord.{0,60}no obligation.{0,60}repair",
             "The landlord disclaims any obligation to carry out repairs.", 22),
            (r"tenant shall bear.{0,80}(?:all|any).{0,40}(?:repair|maintenance) costs",
             "The tenant may be required to bear all repair and maintenance costs, including major/structural repairs.", 18),
        ],
        "protective": [
            r"landlord shall.{0,80}(?:repair|maintain)",
            r"structural repairs.{0,60}landlord",
            r"reasonable wear and tear",
        ],
        "missing_points": 14,
    },
    "Termination and Eviction": {
        "required": True,
        "risk": [
            (r"landlord may.{0,80}(?:evict|terminate).{0,60}(?:without notice|immediately)",
             "The landlord may terminate the tenancy or evict the tenant without adequate notice.", 28),
            (r"lock-?in period.{0,60}(?:12|18|24|36)\s*months?",
             "A lengthy lock-in period restricts the tenant's ability to exit the lease early.", 20),
            (r"forfeit.{0,80}deposit.{0,60}early termination",
             "Early termination results in forfeiture of the full security deposit.", 22),
            (r"eviction.{0,80}without.{0,40}(?:court order|due process)",
             "The clause suggests eviction may proceed without a court order or due process.", 30),
        ],
        "protective": [
            r"(?:30|60|90)\s*days?.{0,40}notice",
            r"either party.{0,60}terminate",
            r"court order",
        ],
        "missing_points": 24,
    },
    "Renewal and Rent Escalation": {
        "required": False,
        "risk": [
            (r"rent.{0,80}increase.{0,60}(?:sole discretion|unilaterally)",
             "Rent may be increased unilaterally at the landlord's sole discretion.", 22),
            (r"automatic(?:ally)? renew.{0,100}(?:same terms|without (?:tenant's )?consent)",
             "The lease automatically renews without requiring the tenant's consent.", 16),
        ],
        "protective": [
            r"mutual(?:ly)? agree.{0,60}renew",
            r"notice.{0,60}rent increase",
            r"(?:\d{1,2})\s*%.{0,40}(?:annual|per annum)",
        ],
        "missing_points": 10,
    },
    "Use of Premises and Subletting": {
        "required": False,
        "risk": [
            (r"tenant.{0,80}liable.{0,60}(?:any|all).{0,40}damage.{0,40}(?:guests|visitors)",
             "The tenant may be held liable for damage caused by any guest or visitor, without qualification.", 14),
            (r"no right to sublet.{0,60}under any circumstances",
             "Subletting is prohibited under all circumstances, which may limit the tenant's flexibility.", 10),
        ],
        "protective": [
            r"prior written consent.{0,60}sublet",
            r"landlord's consent.{0,40}not.{0,20}unreasonably withheld",
        ],
        "missing_points": 8,
    },
    "Governing Law": {
        "required": True,
        "risk": [
            (r"courts (?:of|at|in) (?:the )?(?:united states|singapore|united kingdom|dubai)",
             "The agreement requires disputes to be handled in a foreign jurisdiction.", 18),
        ],
        "protective": [
            r"laws of india",
            r"courts (?:of|at|in).{0,30}india",
        ],
        "missing_points": 12,
    },
}

# ============================================================
# Estate Planning Documents (wills, trusts, power of attorney)
# ============================================================

ESTATE_HEADING_ALIASES = {
    "Executor and Administration": [
        "executor", "appointment of executor", "administration of estate", "letters of administration",
    ],
    "Beneficiaries and Bequests": [
        "beneficiaries", "bequest", "legacy", "residuary estate", "distribution of assets",
    ],
    "Revocation": [
        "revocation", "revocation of prior wills",
    ],
    "Power of Attorney Scope": [
        "power of attorney", "attorney-in-fact", "agent's authority", "scope of authority",
    ],
    "Witness and Execution": [
        "witness", "attestation", "execution", "notarization", "notarisation",
    ],
}

ESTATE_CLAUSE_RULES = {
    "Executor and Administration": {
        "required": True,
        "risk": [
            (r"executor.{0,100}sole discretion.{0,60}(?:distribute|sell|dispose)",
             "The executor may have unchecked discretion over how assets are distributed or sold.", 20),
            (r"no bond (?:shall be )?required",
             "The executor is not required to post a bond, removing a safeguard against mismanagement.", 14),
            (r"executor.{0,80}without.{0,40}(?:accounting|oversight)",
             "The executor may act without providing an accounting to beneficiaries.", 18),
        ],
        "protective": [
            r"accounting.{0,60}beneficiaries",
            r"court supervision",
            r"co-executor",
        ],
        "missing_points": 22,
    },
    "Beneficiaries and Bequests": {
        "required": True,
        "risk": [
            (r"residuary estate.{0,100}(?:sole discretion|as (?:the )?executor deems)",
             "Distribution of the residuary estate may be left to unchecked executor discretion.", 18),
            (r"no contingent beneficiar",
             "No contingent beneficiary is named if the primary beneficiary predeceases the testator.", 16),
        ],
        "protective": [
            r"contingent beneficiar",
            r"per stirpes",
            r"specific bequest",
        ],
        "missing_points": 18,
    },
    "Revocation": {
        "required": True,
        "risk": [
            (r"does not revoke.{0,60}(?:prior|earlier) will",
             "The document does not revoke prior wills, which may create conflicting instructions.", 15),
        ],
        "protective": [
            r"revoke[sd]?.{0,40}all (?:prior|earlier) wills",
        ],
        "missing_points": 12,
    },
    "Power of Attorney Scope": {
        "required": False,
        "risk": [
            (r"unlimited authority.{0,60}(?:agent|attorney-in-fact)",
             "The agent is granted unlimited authority without meaningful restriction.", 24),
            (r"durable power of attorney.{0,100}without.{0,40}(?:oversight|accounting)",
             "The durable power of attorney lacks an oversight or accountability mechanism.", 18),
        ],
        "protective": [
            r"agent shall act.{0,60}best interest",
            r"periodic accounting",
            r"springing power",
        ],
        "missing_points": 16,
    },
    "Witness and Execution": {
        "required": True,
        "risk": [
            (r"(?:only|one) witness.{0,40}sign|sign(?:ed)?.{0,40}(?:only|one) witness|witnessed by (?:only )?one witness",
             "Only one witness appears to have signed, which may not satisfy statutory execution requirements.", 20),
        ],
        "protective": [
            r"two.{0,20}witnesses",
            r"notari[sz]ed",
            r"self-proving affidavit",
        ],
        "missing_points": 18,
    },
}

# ============================================================
# Court and Litigation Pleadings (complaints, notices, motions)
# ============================================================

LITIGATION_HEADING_ALIASES = {
    "Parties and Jurisdiction": [
        "parties", "jurisdiction", "cause of action", "plaintiff and defendant",
    ],
    "Relief Sought": [
        "relief sought", "prayer", "wherefore", "prayer for relief",
    ],
    "Service of Process": [
        "service of process", "summons", "service of summons",
    ],
    "Limitation Period": [
        "limitation period", "statute of limitations", "period of limitation",
    ],
}

LITIGATION_CLAUSE_RULES = {
    "Parties and Jurisdiction": {
        "required": True,
        "risk": [
            (r"(?:plaintiff|petitioner).{0,100}unable to (?:identify|locate).{0,40}defendant",
             "The defendant's identity or address appears unclear, which may affect proper service of process.", 18),
            (r"jurisdiction.{0,60}(?:unclear|not (?:specified|established))",
             "The basis for the court's jurisdiction over the dispute is not clearly established.", 20),
        ],
        "protective": [
            r"registered address",
            r"principal place of business",
            r"this (?:hon'ble )?court has jurisdiction",
        ],
        "missing_points": 20,
    },
    "Relief Sought": {
        "required": True,
        "risk": [
            (r"unspecified damages",
             "The relief sought does not specify a damages amount, which may weaken enforceability.", 16),
            (r"no specific relief.{0,40}(?:claimed|sought)",
             "No specific relief is claimed, which may render the pleading incomplete.", 18),
        ],
        "protective": [
            r"specific performance",
            r"compensatory damages",
            r"declaratory relief",
            r"wherefore.{0,60}prays",
        ],
        "missing_points": 18,
    },
    "Service of Process": {
        "required": False,
        "risk": [
            (r"service.{0,80}(?:not|unable to).{0,40}(?:effected|completed)",
             "Service of process may not have been properly effected on the defendant.", 20),
        ],
        "protective": [
            r"acknowledgment of service",
            r"affidavit of service",
            r"proof of service",
        ],
        "missing_points": 12,
    },
    "Limitation Period": {
        "required": True,
        "risk": [
            (r"filed.{0,80}(?:after|beyond).{0,40}limitation period",
             "The pleading may have been filed after the applicable limitation period, risking dismissal as time-barred.", 30),
            (r"time-?barred",
             "The claim may be time-barred under the applicable statute of limitations.", 28),
        ],
        "protective": [
            r"within the limitation period",
            r"cause of action arose on",
            r"limitation.{0,40}saved by",
        ],
        "missing_points": 22,
    },
}
