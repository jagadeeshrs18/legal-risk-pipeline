"""
Synthetic sample-contract text bank used to build the test PDF corpus.

These are NOT copied from any real agreement — they are written from
scratch to exercise the pipeline's clause detection, risk rules, and
document-category classifier across realistic variations in wording,
party names, numbers, and structure. 12-15 variants per category.

NOTE: this covers the "in-house dataset" leg of accuracy testing
required by the assignment. For the second leg (real-world PDFs found
on the internet), see tests/README.md — those files are supplied by
you and dropped into test_samples/from_internet/<Category>/, since we
cannot redistribute third-party contract PDFs here.
"""

NDA_SAMPLES = [
    """MUTUAL NON-DISCLOSURE AGREEMENT

This Non-Disclosure Agreement ("Agreement") is entered into between {party_a}
("Disclosing Party") and {party_b} ("Receiving Party") for the purpose of
evaluating a potential business relationship.

1. CONFIDENTIAL INFORMATION
"Confidential Information" means all non-public information disclosed by the
Disclosing Party, whether oral or written, that is designated as confidential
or that a reasonable person would understand to be confidential.

2. OBLIGATIONS OF RECEIVING PARTY
The Receiving Party shall use the Confidential Information solely for the
Permitted Purpose and shall not disclose it to any third party without the
prior written consent of the Disclosing Party.

3. EXCLUSIONS
This Agreement does not apply to information that is already known to the
Receiving Party, becomes publicly available through no fault of the
Receiving Party, or is independently developed without use of the
Confidential Information.

4. TERM
The obligations of confidentiality under this Agreement shall survive for a
period of {years} years from the date of disclosure.

5. GOVERNING LAW
This Agreement shall be governed by the laws of India, and the courts at
{city}, India shall have exclusive jurisdiction.

6. TERMINATION
Either party may terminate this Agreement upon thirty (30) days written
notice to the other party.
""",
    """NON-DISCLOSURE AGREEMENT

This Non-Disclosure Agreement is made between {party_a} (Disclosing Party)
and {party_b} (Receiving Party).

1. Definition of Confidential Information
All information marked confidential or reasonably understood to be
confidential, including business plans, source code, pricing, and customer
lists, shall be treated as Confidential Information.

2. Restrictions
The Receiving Party shall not use or disclose any Confidential Information
except as required to evaluate the proposed transaction between the parties.

3. Perpetual Confidentiality
The confidentiality obligations under this Agreement shall continue in
perpetuity and shall survive termination indefinitely.

4. Remedies
The Disclosing Party shall be entitled to injunctive relief in addition to
any other remedies available at law or in equity.

5. Jurisdiction
This Agreement is governed by the laws of India and subject to the
exclusive jurisdiction of the courts at {city}.
""",
    """CONFIDENTIALITY AGREEMENT

Entered into by and between {party_a} and {party_b} as of {date}.

1. Purpose
The parties wish to explore a potential collaboration and, in connection
therewith, may disclose certain confidential and proprietary information to
each other.

2. Confidential Information
Confidential Information includes any technical, financial, or business
information disclosed by either party, whether marked confidential or not.

3. Obligations
Each Receiving Party shall protect the disclosing party's Confidential
Information using at least the same degree of care it uses for its own
confidential information, and in no event less than reasonable care.

4. Exceptions
Confidential Information does not include information that was already
known, is publicly available, or is required to be disclosed by applicable
law, provided prompt notice is given to the Disclosing Party.

5. Term and Survival
This Agreement remains in effect for two (2) years from signature, and the
confidentiality obligations survive for three (3) years thereafter.

6. Governing Law
This Agreement shall be construed under the laws of India.
""",
]

EMPLOYMENT_SAMPLES = [
    """EMPLOYMENT AGREEMENT

This Employment Agreement is entered into between {party_a} ("Company") and
{employee_name} ("Employee") effective from {date}.

1. APPOINTMENT AND DESIGNATION
The Employee is appointed as {designation} and shall report to the
reporting manager designated by the Company.

2. PROBATIONARY PERIOD
The probationary period will be of six (6) months, during which the Company
may terminate the working relationship without cause or notice at any time.

3. COMPENSATION
The Employee's annual Cost to Company (CTC) shall be Rs. {salary}, payable
monthly, subject to applicable statutory deductions.

4. CONFIDENTIALITY
The Employee shall not, during or after employment, disclose any
confidential information of the Company to any third party without consent.

5. INTELLECTUAL PROPERTY
All intellectual property, inventions, and work product created by the
Employee during the course of employment shall be the exclusive property of
the Company.

6. TERMINATION
Either party may terminate this Agreement by giving thirty (30) days written
notice. The Company may terminate immediately for misconduct.

7. GOVERNING LAW
This Agreement shall be governed by the laws of India, and the courts at
{city} shall have jurisdiction.
""",
    """LETTER OF APPOINTMENT

Dear {employee_name},

We are pleased to offer you employment with {party_a} as {designation},
effective {date}. This letter, together with the attached terms, constitutes
your Employment Agreement.

1. Probation
Your employment will be subject to a probation period of {probation_months}
months, extendable at the Company's sole discretion.

2. Salary
Your annual CTC will be Rs. {salary}, as detailed in Annexure A.

3. Notice Period
During probation, either party may terminate the employment by giving seven
(7) days notice. Post-confirmation, the notice period shall be sixty (60)
days from the Employee, or immediate termination with pay in lieu from the
Employer.

4. Confidential Information
You agree to keep confidential all information relating to the Company's
business, clients, and operations, both during and after employment,
without exception.

5. Intellectual Property
Any work product created during your employment, including software,
designs, and documents, shall vest exclusively in the Company.

6. Governing Law
This offer and your employment are governed by the laws of India, with
courts at {city} having exclusive jurisdiction.

Please sign and return a copy of this letter to confirm your acceptance.
""",
    """EMPLOYMENT AGREEMENT

Made between {party_a} (the "Employer") and {employee_name} (the
"Employee") on {date}.

1. Position
The Employee is engaged as {designation} and shall devote full working time
to the Employer's business.

2. Probation and Confirmation
The Employee shall serve a probationary period of {probation_months}
months. This period involves closer performance evaluation than that given
to regular employees, and does not guarantee confirmation.

3. Remuneration
The Employee shall be paid a monthly salary as set out in Schedule 1,
amounting to an annual CTC of Rs. {salary}.

4. Resignation and Termination
The Employee may lawfully terminate this Employment Agreement by giving the
Employer not less than sixty (60) days' notice in writing. The Employer may
terminate the Employee at any time with immediate effect without giving any
notice period, in case of misconduct or breach of policy.

5. Confidentiality
The Employee shall not, directly or indirectly, disclose any trade secrets,
client information, or confidential business information of the Employer,
either during employment or thereafter, without exception.

6. Intellectual Property
All intellectual property created by the Employee during employment,
including any software, source code, or inventions, shall be the exclusive
property of the Employer, and the Employee waives all rights therein.

7. Governing Law
This Agreement is governed by the laws of India. The courts at {city} shall
have exclusive jurisdiction over any dispute.
""",
]

SERVICE_SAMPLES = [
    """SERVICE AGREEMENT

This Service Agreement ("Agreement") is entered into between {party_a}
("Customer") and {party_b} ("Service Provider") effective {date}.

1. SCOPE OF SERVICES
The Service Provider shall perform the services described in the attached
Statement of Work, including {scope_desc}.

2. SERVICE LEVELS
The Service Provider shall use commercially reasonable efforts to meet the
service levels described in Schedule 1, including response and resolution
times for support requests.

3. FEES AND PAYMENT
The Customer shall pay the fees set out in Schedule 2 within thirty (30)
days of a valid invoice. Fees paid are non-refundable.

4. TERM AND TERMINATION
This Agreement shall continue for an initial term of twelve (12) months and
shall automatically renew for successive twelve (12) month terms unless
either party gives ninety (90) days notice of non-renewal.

5. LIMITATION OF LIABILITY
The Service Provider's aggregate liability under this Agreement shall not
exceed the fees paid in the one (1) month preceding the claim. Neither
party shall be liable for indirect or consequential loss of any kind.

6. INDEMNIFICATION
The Customer shall defend and indemnify the Service Provider against any
third-party claims arising from the Customer's use of the deliverables.

7. GOVERNING LAW
This Agreement is governed by the laws of India, with courts at {city}
having exclusive jurisdiction.
""",
    """CONSULTING SERVICES AGREEMENT

This Agreement is made between {party_a} ("Client") and {party_b}
("Consultant") on {date}.

1. Services
The Consultant shall provide {scope_desc} in accordance with the Statement
of Work attached as Exhibit A.

2. Deliverables and Acceptance
Deliverables shall be reviewed by the Client, who shall provide acceptance
or feedback within ten (10) business days of delivery.

3. Fees
The Client shall pay the Consultant the fees set out in Exhibit B. Late
payments shall accrue interest at 3% per month, compounded monthly.

4. Warranty
The services are provided on an "as is" basis, and the Consultant disclaims
all warranties, whether express or implied, including fitness for purpose.

5. Confidentiality
Each party shall keep the other's confidential information confidential and
shall not disclose it to any third party without written consent.

6. Termination
The Client may terminate only for the Consultant's material breach that
remains uncured after a ninety (90) day cure period.

7. Governing Law
This Agreement shall be governed by the laws of India.
""",
    """MASTER SERVICE AGREEMENT

Between {party_a} ("Customer") and {party_b} ("Provider"), effective
{date}.

1. Scope of Services
The Provider shall deliver {scope_desc} as further described in one or more
Statements of Work executed under this Agreement.

2. Service Levels
The Provider shall provide no uptime guarantee for the hosted service, and
service credits shall be the Customer's sole remedy for any outage.

3. Fees and Payment
Fees shall be invoiced monthly and are due within thirty (30) days. The
Provider may unilaterally revise fees upon thirty (30) days' notice.

4. Data Protection
The Provider may share the Customer's personal data with its affiliates and
sub-processors as it deems necessary, without further consent from the
Customer.

5. Termination
The Provider may suspend or terminate the services immediately for
suspected misuse or delayed payment.

6. Limitation of Liability
The Provider shall not be liable for any data loss or security incident
arising from the hosted service, howsoever caused.

7. Governing Law
This Agreement shall be governed by the laws of the State of Delaware,
United States, and the parties submit to the exclusive jurisdiction of the
courts of Delaware.
""",
]

VENDOR_SAMPLES = [
    """VENDOR AGREEMENT

This Vendor Agreement is entered into between {party_a} ("Buyer") and
{party_b} ("Vendor") effective {date}.

1. SUPPLY OF GOODS
The Vendor shall supply {goods_desc} in accordance with the specifications
set out in Purchase Order Schedule A, and in accordance with the delivery
schedule agreed by the parties.

2. DELIVERY
The Vendor shall deliver the goods to the Buyer's designated facility on the
dates specified in each Purchase Order. Time is of the essence.

3. PRICE AND PAYMENT
The Buyer shall pay the Vendor the prices set out in Schedule B within
forty-five (45) days of receipt of a valid invoice matched to a Purchase
Order and delivery note.

4. WARRANTY
The Vendor warrants that the goods supplied shall conform to the agreed
specifications, be free from material defects, and be fit for the intended
purpose for a period of twelve (12) months from delivery.

5. LIMITATION OF LIABILITY
The Vendor's aggregate liability arising out of this Agreement shall not
exceed the value of the relevant Purchase Order, subject to a carve-out for
gross negligence or wilful misconduct.

6. TERMINATION
Either party may terminate this Agreement for the other party's material
breach that remains uncured for thirty (30) days after written notice.

7. GOVERNING LAW
This Agreement shall be governed by the laws of India, and the courts at
{city} shall have exclusive jurisdiction.
""",
    """SUPPLY AGREEMENT

Between {party_a} ("Purchaser") and {party_b} ("Supplier"), dated {date}.

1. Goods and Services
The Supplier shall supply {goods_desc} pursuant to purchase orders issued
under this Agreement from time to time.

2. Delivery Schedule
The Supplier shall deliver goods strictly in accordance with the delivery
schedule set out in each purchase order; late delivery may result in
liquidated damages as specified in Schedule C.

3. Payment Terms
Payment shall be made within sixty (60) days of the Purchaser's receipt of a
compliant invoice, provided the goods have passed acceptance inspection.

4. Quality and Inspection
The Purchaser reserves the right to inspect and reject any goods that do
not meet agreed quality standards, at the Supplier's cost.

5. Indemnification
The Supplier shall indemnify the Purchaser against all claims, losses,
damages, penalties, and expenses arising from defective goods, regardless
of fault.

6. Governing Law
This Agreement shall be governed by the laws of India.
""",
    """VENDOR AGREEMENT (PROCUREMENT OF GOODS)

This Vendor Agreement is made between {party_a} ("Company") and {party_b}
("Vendor") on {date}.

1. Vendor's Obligations
The Vendor shall supply {goods_desc} to the Company as per purchase orders
raised from time to time, in accordance with the agreed inventory and
shipment plan.

2. Price
Prices for the goods are fixed for the initial term of this Agreement, and
may not be unilaterally revised by the Vendor without the Company's prior
written consent.

3. Warranty
The Vendor warrants that all goods supplied will be free of defects in
material and workmanship for a period of twelve (12) months from the date
of delivery, and will conform to the agreed specifications.

4. Payment
The Company shall pay the Vendor within forty-five (45) days of receipt of
a valid invoice and matching delivery note.

5. Termination
This Agreement may be terminated by either party on ninety (90) days
written notice, or immediately for a material and uncured breach.

6. Governing Law
This Agreement shall be governed by the laws of India, with courts at
{city} having exclusive jurisdiction.
""",
]

REAL_ESTATE_SAMPLES = [
    """LEASE AGREEMENT

This Lease Agreement is entered into between {landlord} ("Landlord") and
{tenant} ("Tenant") for the premises located at {premises}, effective
{date}.

1. TERM
The lease shall run for a period of eleven (11) months from the date of
this Agreement, renewable by mutual written consent of both parties.

2. RENT AND SECURITY DEPOSIT
The Tenant shall pay monthly rent of Rs. {rent} on or before the 5th of
each month. The Tenant shall pay a refundable security deposit of Rs.
{deposit}, to be refunded within thirty (30) days of vacating the
premises, less any documented deductions for damage beyond reasonable
wear and tear.

3. MAINTENANCE AND REPAIRS
The Landlord shall be responsible for structural repairs and major
maintenance. The Tenant shall be responsible for day-to-day upkeep and
any damage caused by the Tenant or the Tenant's guests.

4. USE OF PREMISES AND SUBLETTING
The Tenant shall use the premises solely for residential purposes and
shall not sublet the premises without the Landlord's prior written
consent, which shall not be unreasonably withheld.

5. TERMINATION AND EVICTION
Either party may terminate this Agreement by giving sixty (60) days
written notice. The Landlord shall not evict the Tenant except through
due process of law.

6. GOVERNING LAW
This Agreement shall be governed by the laws of India, and the courts at
{city} shall have jurisdiction.
""",
    """RENTAL AGREEMENT

This Rental Agreement is made between {landlord} (Owner) and {tenant}
(Tenant) in respect of the property at {premises}.

1. Rent and Deposit
Monthly rent shall be Rs. {rent}, payable in advance. The Tenant has paid
an interest-free security deposit of Rs. {deposit}, which is
non-refundable and shall not be returned under any circumstances upon
vacating the premises.

2. Rent Escalation
The Owner may increase the rent at its sole discretion at any time during
the tenancy, without prior notice to the Tenant.

3. Termination
The Owner may terminate this tenancy and re-enter the premises
immediately, without notice, if the Owner believes the Tenant has
breached any term of this Agreement.

4. Maintenance
The Tenant shall be solely responsible for all repairs and maintenance of
the premises, including structural repairs, for the duration of the
tenancy.

5. Governing Law
This Agreement shall be governed by the laws of India.
""",
    """LEAVE AND LICENSE AGREEMENT

This Leave and License Agreement is entered into between {landlord}
("Licensor") and {tenant} ("Licensee") for the premises at {premises},
effective {date}.

1. Licence Fee and Deposit
The Licensee shall pay a monthly licence fee of Rs. {rent} and an
interest-free refundable deposit of Rs. {deposit}, refundable within
thirty (30) days of handover of vacant possession, subject to itemised
deductions for damage.

2. Lock-in Period
The Licensee shall not terminate this Agreement before the completion of
a lock-in period of twenty-four (24) months, and early termination shall
result in complete forfeiture of the deposit.

3. Renewal
This Agreement shall automatically renew on the same terms for a further
period of eleven (11) months unless either party objects in writing.

4. Subletting
The Licensee shall have no right to sublet or share possession of the
premises under any circumstances.

5. Governing Law
This Agreement shall be governed by the laws of India, with courts at
{city} having jurisdiction.
""",
]

ESTATE_SAMPLES = [
    """LAST WILL AND TESTAMENT

I, {testator}, residing at {city}, being of sound mind, hereby declare
this to be my Last Will and Testament, and I revoke all prior wills and
codicils made by me.

1. APPOINTMENT OF EXECUTOR
I appoint {executor} as the Executor of this Will. The Executor shall
provide a periodic accounting of the estate to all named beneficiaries
and shall administer the estate under the supervision of the competent
court.

2. BENEFICIARIES AND BEQUESTS
I bequeath my residuary estate to {beneficiary}. If {beneficiary} does not
survive me, I bequeath my residuary estate to {contingent_beneficiary} as
a contingent beneficiary.

3. WITNESS AND EXECUTION
This Will has been signed by me in the presence of two witnesses, who
have also signed below, and has been notarised in accordance with
applicable law.

Witness 1: ______________
Witness 2: ______________
""",
    """LAST WILL AND TESTAMENT

I, {testator}, of {city}, declare this to be my Last Will and Testament.

1. Executor
I appoint {executor} as sole Executor, who may distribute or sell any
asset of my estate at their sole discretion and without the requirement
to post any bond or provide any accounting to beneficiaries.

2. Bequests
I leave my entire estate to {beneficiary}. No contingent beneficiary is
named should {beneficiary} predecease me.

3. Execution
Signed by me on {date}, witnessed by one witness whose signature appears
below.

Witness: ______________
""",
    """POWER OF ATTORNEY

I, {testator}, of {city}, hereby appoint {executor} as my
attorney-in-fact ("Agent") under this Power of Attorney.

1. Scope of Authority
The Agent shall have unlimited authority to act on my behalf in all
financial and property matters, without any requirement for periodic
accounting or oversight by any third party.

2. Durability
This Power of Attorney shall remain in effect and be durable
notwithstanding my subsequent incapacity, and shall continue in effect
without any independent oversight mechanism.

3. Revocation
This Power of Attorney revokes all prior powers of attorney granted by
me.

4. Execution
Signed and notarised on {date} at {city}.
""",
]

LITIGATION_SAMPLES = [
    """BEFORE THE HON'BLE COURT AT {city}

{plaintiff} ... PLAINTIFF
VERSUS
{defendant} ... DEFENDANT

CIVIL SUIT FOR RECOVERY OF MONEY

1. PARTIES AND JURISDICTION
The Plaintiff, {plaintiff}, is a company having its registered address at
{city}. The Defendant, {defendant}, carries on business within the
jurisdiction of this Hon'ble Court, which accordingly has jurisdiction to
try and decide this suit.

2. CAUSE OF ACTION
The cause of action arose on {date}, when the Defendant failed to make
payment of the outstanding invoice amount despite repeated demands.

3. LIMITATION
This suit is filed within the limitation period prescribed under the
Limitation Act, as the cause of action arose on {date}, well within three
years of the filing of this suit.

4. RELIEF SOUGHT
WHEREFORE, the Plaintiff prays that this Hon'ble Court be pleased to
direct the Defendant to pay a sum of Rs. {amount} along with interest and
costs of this suit, and pass such other relief as this Hon'ble Court deems
fit.

5. SERVICE OF PROCESS
An affidavit of service shall be filed confirming that summons has been
duly served upon the Defendant at its registered address.
""",
    """LEGAL NOTICE

To,
{defendant}

Under instructions from my client, {plaintiff}, I hereby serve upon you
this Legal Notice as follows:

1. My client's cause of action arose on {date} on account of your failure
to honour the terms of the agreement between the parties.

2. You are hereby called upon to make payment of Rs. {amount} within
fifteen (15) days of receipt of this notice, failing which my client
shall be constrained to initiate appropriate legal proceedings against
you at your risk, cost, and consequences, before a court of competent
jurisdiction.

3. This notice is issued without prejudice to any other right or remedy
available to my client under law.
""",
    """BEFORE THE HON'BLE COURT AT {city}

{plaintiff} ... PETITIONER
VERSUS
{defendant} ... RESPONDENT

WRIT PETITION

1. The Petitioner, {plaintiff}, is unable to ascertain the current
registered address of the Respondent, {defendant}, which has made service
of process difficult in this matter.

2. The petitioner submits that the impugned action is arbitrary and filed
this petition on {date}.

3. No specific relief is claimed in this petition beyond a general prayer
that this Hon'ble Court may pass such orders as it deems fit in the
interest of justice.
""",
]


_REAL_ESTATE_DEFAULTS = dict(
    landlord="Ramesh Kulkarni", tenant="Sneha Iyer", premises="Flat 4B, Green Meadows, Andheri",
    date="1 April 2026", rent="35,000", deposit="1,00,000", city="Mumbai",
)
_ESTATE_DEFAULTS = dict(
    testator="Vijay Kumar Malhotra", executor="Anita Malhotra", beneficiary="Rahul Malhotra",
    contingent_beneficiary="Rahul Malhotra's children", city="Delhi", date="10 February 2026",
)
_LITIGATION_DEFAULTS = dict(
    plaintiff="Sunrise Enterprises Pvt Ltd", defendant="Horizon Traders",
    city="Bengaluru", date="15 January 2026", amount="4,50,000",
)

_REAL_ESTATE_OVERRIDES = [
    {},
    {"landlord": "Meena Associates", "tenant": "Vikram Singh", "premises": "Shop No 12, MG Road",
     "city": "Pune", "rent": "22,000", "deposit": "66,000"},
    {"landlord": "Coastal Properties LLP", "tenant": "Farah Sheikh", "premises": "Villa 7, Palm Estates",
     "city": "Kochi", "rent": "48,000", "deposit": "1,44,000"},
    {"landlord": "Deccan Realty", "tenant": "Arjun Rao", "premises": "Flat 202, Silver Oaks",
     "city": "Hyderabad", "rent": "18,500", "deposit": "55,500"},
    {"landlord": "Northgate Estates", "tenant": "Priya Chawla", "premises": "House No 9, Sector 21",
     "city": "Chandigarh", "rent": "27,000", "deposit": "81,000"},
]
_ESTATE_OVERRIDES = [
    {},
    {"testator": "Geeta Devi Sharma", "executor": "Suresh Sharma", "beneficiary": "Kavita Sharma",
     "contingent_beneficiary": "Kavita Sharma's descendants", "city": "Jaipur"},
    {"testator": "Thomas Mathew", "executor": "Anna Mathew", "beneficiary": "Little Flower Trust",
     "contingent_beneficiary": "Diocese of Kochi", "city": "Kochi"},
    {"testator": "Harpreet Singh Sodhi", "executor": "Jasmeet Kaur", "beneficiary": "Simran Kaur",
     "contingent_beneficiary": "Simran Kaur's children", "city": "Chandigarh"},
    {"testator": "Lakshmi Narayanan", "executor": "Ganesh Narayanan", "beneficiary": "Ganesh Narayanan",
     "contingent_beneficiary": "Ganesh Narayanan's spouse", "city": "Chennai"},
]
_LITIGATION_OVERRIDES = [
    {},
    {"plaintiff": "Bluepeak Logistics Ltd", "defendant": "Rapid Cargo Movers", "city": "Ahmedabad", "amount": "9,20,000"},
    {"plaintiff": "Anjali Deshmukh", "defendant": "Metro Builders Pvt Ltd", "city": "Pune", "amount": "3,10,000"},
    {"plaintiff": "Vantage Software Solutions", "defendant": "Clearview Retail Chain", "city": "Bengaluru", "amount": "6,75,000"},
    {"plaintiff": "Kiran Textiles", "defendant": "Global Apparel Exports", "city": "Surat", "amount": "5,40,000"},
]


def _fill(samples, defaults, overrides_list):
    out = []
    for template in samples:
        for overrides in overrides_list:
            fields = {**defaults, **overrides}
            out.append(template.format(**fields))
    return out


_FILL_DEFAULTS = dict(
    party_a="Alpha Technologies Private Limited",
    party_b="Beta Consulting Services LLP",
    employee_name="Rohan Sharma",
    designation="Senior Software Engineer",
    date="1 April 2026",
    years="3",
    city="Mumbai",
    salary="9,60,000",
    probation_months="6",
    scope_desc="software development and technical support services",
    goods_desc="industrial packaging materials",
)


def _variants(samples: list[str], overrides_list: list[dict]) -> list[str]:
    """Fill each template with each override dict (cycled) to create variety."""
    out = []
    for i, template in enumerate(samples):
        for j, overrides in enumerate(overrides_list):
            fields = {**_FILL_DEFAULTS, **overrides}
            out.append(template.format(**fields))
    return out


# A handful of party-name / number variations so filled documents differ
# beyond just their template structure (12-15 docs per category).
_OVERRIDE_SETS = [
    {},
    {"party_a": "Nimbus Software Pvt Ltd", "party_b": "Orion Data Systems Inc",
     "city": "Bengaluru", "date": "12 January 2026"},
    {"party_a": "Meridian Textiles Ltd", "party_b": "Falcon Traders",
     "city": "Ahmedabad", "date": "5 June 2026", "employee_name": "Ananya Verma",
     "designation": "Marketing Executive", "salary": "6,50,000",
     "goods_desc": "raw cotton and textile inputs",
     "scope_desc": "digital marketing and brand consulting services"},
    {"party_a": "Skyline Constructions", "party_b": "Vertex Engineering Co",
     "city": "Pune", "date": "20 August 2026", "employee_name": "Karan Mehta",
     "designation": "Site Supervisor", "salary": "5,40,000",
     "goods_desc": "steel reinforcement bars",
     "scope_desc": "structural design and consulting services"},
    {"party_a": "Bluewave Analytics", "party_b": "Redstone Capital Advisors",
     "city": "Hyderabad", "date": "3 March 2026", "employee_name": "Priya Nair",
     "designation": "Data Analyst", "salary": "7,20,000",
     "goods_desc": "networking hardware and cabling",
     "scope_desc": "data analytics and dashboarding services"},
]


def get_all_samples() -> dict[str, list[str]]:
    commercial = (
        _variants(NDA_SAMPLES, _OVERRIDE_SETS)
        + _variants(EMPLOYMENT_SAMPLES, _OVERRIDE_SETS)
        + _variants(SERVICE_SAMPLES, _OVERRIDE_SETS)
        + _variants(VENDOR_SAMPLES, _OVERRIDE_SETS)
    )
    return {
        "Business and Commercial Contracts": commercial,
        "Real Estate and Property Documents": _fill(REAL_ESTATE_SAMPLES, _REAL_ESTATE_DEFAULTS, _REAL_ESTATE_OVERRIDES),
        "Estate Planning Documents": _fill(ESTATE_SAMPLES, _ESTATE_DEFAULTS, _ESTATE_OVERRIDES),
        "Court and Litigation Pleadings": _fill(LITIGATION_SAMPLES, _LITIGATION_DEFAULTS, _LITIGATION_OVERRIDES),
    }


def get_commercial_subtype_samples() -> dict[str, list[str]]:
    """Used only for optionally testing the commercial sub-type detector."""
    return {
        "NDA": _variants(NDA_SAMPLES, _OVERRIDE_SETS),
        "Employment Agreement": _variants(EMPLOYMENT_SAMPLES, _OVERRIDE_SETS),
        "Service Agreement": _variants(SERVICE_SAMPLES, _OVERRIDE_SETS),
        "Vendor Agreement": _variants(VENDOR_SAMPLES, _OVERRIDE_SETS),
    }
