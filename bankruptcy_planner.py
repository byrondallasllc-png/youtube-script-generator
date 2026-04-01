#!/usr/bin/env python3
"""
Bankruptcy Preparation Planner
Chapter 7 & Chapter 13 — Based on Federal Guidelines (11 U.S.C.)
Designed for Novices  |  Not Legal Advice — Consult a Bankruptcy Attorney
"""

import os
import sys
import json
from datetime import date

# ─── Terminal Colors ────────────────────────────────────────────────────────
class C:
    RESET   = "\033[0m"
    BOLD    = "\033[1m"
    DIM     = "\033[2m"
    RED     = "\033[91m"
    GREEN   = "\033[92m"
    YELLOW  = "\033[93m"
    BLUE    = "\033[94m"
    MAGENTA = "\033[95m"
    CYAN    = "\033[96m"
    WHITE   = "\033[97m"
    BG_BLUE = "\033[44m"
    BG_RED  = "\033[41m"

def h(text): return f"{C.BOLD}{C.CYAN}{text}{C.RESET}"
def warn(text): return f"{C.YELLOW}{text}{C.RESET}"
def ok(text): return f"{C.GREEN}{text}{C.RESET}"
def err(text): return f"{C.RED}{text}{C.RESET}"
def dim(text): return f"{C.DIM}{text}{C.RESET}"
def bold(text): return f"{C.BOLD}{text}{C.RESET}"
def mag(text): return f"{C.MAGENTA}{text}{C.RESET}"

def box(title, lines, color=C.CYAN):
    width = max(len(title) + 4, max(len(l) for l in lines) + 4, 60)
    top    = f"{color}╔{'═' * (width - 2)}╗{C.RESET}"
    mid    = f"{color}║{C.RESET} {C.BOLD}{title:<{width-4}}{C.RESET} {color}║{C.RESET}"
    sep    = f"{color}╠{'═' * (width - 2)}╣{C.RESET}"
    bot    = f"{color}╚{'═' * (width - 2)}╝{C.RESET}"
    body   = [f"{color}║{C.RESET} {l:<{width-4}} {color}║{C.RESET}" for l in lines]
    print("\n".join([top, mid, sep] + body + [bot]))

def section(title):
    print(f"\n{C.BG_BLUE}{C.WHITE}{C.BOLD}  {title}  {C.RESET}\n")

def pause():
    input(f"\n{dim('Press Enter to continue...')}")

def clear():
    os.system('cls' if os.name == 'nt' else 'clear')

def menu(title, options):
    print(f"\n{h(title)}")
    for i, opt in enumerate(options, 1):
        print(f"  {C.CYAN}{i}{C.RESET}. {opt}")
    print(f"  {C.CYAN}0{C.RESET}. {dim('Go back / Exit')}")
    while True:
        choice = input(f"\n{C.BOLD}Choose: {C.RESET}").strip()
        if choice == "0":
            return 0
        if choice.isdigit() and 1 <= int(choice) <= len(options):
            return int(choice)
        print(warn("  Invalid choice. Try again."))

# ─── Checklist State ────────────────────────────────────────────────────────
STATE_FILE = "bankruptcy_progress.json"

def load_state():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE) as f:
            return json.load(f)
    return {"ch7": {}, "ch13": {}}

def save_state(state):
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2)

# ─── Explainer Library ──────────────────────────────────────────────────────
EXPLAINERS = {
    "automatic_stay": {
        "title": "Automatic Stay  (11 U.S.C. § 362)",
        "body": [
            "The moment you file for bankruptcy, a powerful legal protection kicks in",
            "automatically — it's called the Automatic Stay.",
            "",
            "What it does:",
            "  • Immediately stops most creditor collection actions",
            "  • Halts lawsuits, wage garnishments, and bank levies",
            "  • Stops foreclosure proceedings (temporarily)",
            "  • Stops repossessions",
            "  • Stops harassing phone calls and letters",
            "",
            "What it does NOT stop:",
            "  • Criminal proceedings",
            "  • Child support / alimony collection",
            "  • Certain tax proceedings",
            "  • Actions against co-debtors (in Chapter 7)",
            "",
            "Duration:",
            "  Chapter 7 → lasts until discharge (about 3-6 months)",
            "  Chapter 13 → lasts the entire 3-5 year repayment plan",
            "",
            "INSIGHT: This is one of bankruptcy's most valuable protections.",
            "If you're facing imminent foreclosure or wage garnishment,",
            "filing bankruptcy — even on an emergency basis — can stop it",
            "the same day.",
        ]
    },
    "means_test": {
        "title": "The Means Test  (11 U.S.C. § 707(b)(2))",
        "body": [
            "The Means Test determines if you QUALIFY for Chapter 7.",
            "Congress created it in 2005 to prevent abuse by higher-income",
            "filers who could actually afford to repay their debts.",
            "",
            "Step 1 — Compare to State Median Income:",
            "  • The U.S. Trustee publishes median income by state & family size",
            "  • If your average monthly income over the last 6 months is",
            "    AT OR BELOW your state's median → you automatically pass",
            "  • If you're ABOVE the median → you must complete Step 2",
            "",
            "Step 2 — Calculate Disposable Income:",
            "  • Subtract allowed IRS expense standards (housing, food, etc.)",
            "  • Subtract actual expenses for some categories",
            "  • If remaining 'disposable income' is below threshold → you pass",
            "  • If above threshold → you may be required to file Chapter 13",
            "",
            "INSIGHT: The 6-month income lookback can be strategic.",
            "If you recently lost a job or took a pay cut, your income",
            "calculation may be lower than your current income. Timing matters.",
            "",
            "WHERE TO FIND CURRENT NUMBERS:",
            "  justice.gov/ust/means-testing  (updated regularly by DOJ)",
        ]
    },
    "dischargeable_debts": {
        "title": "What Debts Can Be Erased?  (11 U.S.C. § 523 & § 727)",
        "body": [
            "CAN be discharged (erased) in bankruptcy:",
            "  ✓ Credit card balances",
            "  ✓ Medical bills",
            "  ✓ Personal loans / payday loans",
            "  ✓ Utility arrears (past-due amounts)",
            "  ✓ Lease obligations (in most cases)",
            "  ✓ Business debts (for sole proprietors)",
            "  ✓ Older income tax debt (if it meets the '3-year rule')",
            "  ✓ Deficiency balances after repossession",
            "",
            "CANNOT be discharged (these survive bankruptcy):",
            "  ✗ Student loans (very rare hardship exceptions exist)",
            "  ✗ Child support and alimony",
            "  ✗ Recent federal/state income taxes (< 3 years old)",
            "  ✗ Debts from fraud or intentional wrongdoing",
            "  ✗ Criminal fines and restitution",
            "  ✗ DUI-related injury/death judgments",
            "  ✗ Debts not listed in your bankruptcy petition",
            "",
            "INSIGHT: Chapter 13 can sometimes help with non-dischargeable debts",
            "by letting you catch up on arrears (e.g. back child support) or",
            "pay priority tax debt over 3-5 years interest-free.",
        ]
    },
    "exemptions": {
        "title": "Bankruptcy Exemptions  (11 U.S.C. § 522)",
        "body": [
            "Exemptions protect your property from being taken by the trustee.",
            "You keep exempt property — even after filing bankruptcy.",
            "",
            "Federal Exemptions (2025 — adjusted every 3 years):",
            "  🏠 Homestead:         up to $27,900 in home equity",
            "  🚗 Motor Vehicle:     up to $4,450",
            "  🛋️  Household Goods:  up to $700/item, $14,875 total",
            "  💍 Jewelry:           up to $1,875",
            "  🔧 Tools of Trade:    up to $2,800",
            "  🃏 Wildcard:          $1,475 + up to $13,950 unused homestead",
            "  💰 Retirement Accts: Unlimited (401k, IRA, pension — ERISA)",
            "  🏥 Health Aids:       Unlimited",
            "  📋 Life Insurance:    Cash value up to $14,875",
            "  💵 Social Security:   Unlimited (while in account)",
            "  ⚔️  VA Benefits:       Unlimited",
            "",
            "IMPORTANT: Many states let you choose EITHER federal or state",
            "exemptions — whichever is better for you. Some states OPT OUT",
            "of federal exemptions and require you to use state ones only.",
            "",
            "INSIGHT: If you have significant home equity, compare your state's",
            "homestead exemption vs. the federal one carefully.",
            "A bankruptcy attorney can run this analysis for you.",
        ]
    },
    "341_meeting": {
        "title": "The 341 Meeting of Creditors  (11 U.S.C. § 341)",
        "body": [
            "Every bankruptcy filer must attend a '341 Meeting' (named after",
            "the section of the bankruptcy code that requires it).",
            "",
            "What it is:",
            "  A short, informal hearing where a bankruptcy trustee asks you",
            "  questions about your filed documents under oath.",
            "",
            "What to expect:",
            "  • Usually held 21–40 days after you file",
            "  • Lasts 5–10 minutes for most cases",
            "  • Held at a federal courthouse or sometimes via phone/video",
            "  • Creditors CAN attend but rarely do",
            "  • You must bring valid photo ID + Social Security proof",
            "",
            "Common questions the trustee asks:",
            "  'Did you sign this petition? Is the information accurate?'",
            "  'Have you filed bankruptcy before?'",
            "  'Do you own any real estate?'",
            "  'Are you expecting any inheritance or lawsuits?'",
            "",
            "INSIGHT: The 341 meeting sounds scary but it's usually routine.",
            "If your paperwork is honest and complete, it should be quick.",
            "Having an attorney with you makes it even smoother.",
        ]
    },
    "credit_counseling": {
        "title": "Mandatory Credit Counseling  (11 U.S.C. § 109(h))",
        "body": [
            "FEDERAL LAW REQUIRES this before you can file for bankruptcy.",
            "",
            "What you must do:",
            "  • Complete an approved credit counseling course",
            "  • Must be done within 180 days BEFORE filing",
            "  • Course is typically online or by phone",
            "  • Takes about 60-90 minutes",
            "  • Costs $25-$50 (fee waivers available if you can't afford it)",
            "  • You receive a certificate — required to file",
            "",
            "SECOND requirement — Debtor Education:",
            "  • After filing (but before discharge), you must complete a",
            "    'debtor education' / financial management course",
            "  • Also online, about 2 hours",
            "  • Also costs $25-$50",
            "  • Without this certificate, your discharge can be DENIED",
            "",
            "WHERE TO FIND APPROVED PROVIDERS:",
            "  justice.gov/ust/credit-counseling-debtor-education-information",
            "",
            "INSIGHT: Don't wait until the last minute. Complete this as early",
            "as possible once you decide bankruptcy is right for you.",
        ]
    },
    "trustee": {
        "title": "The Bankruptcy Trustee — Who Are They?",
        "body": [
            "A trustee is a court-appointed person who administers your case.",
            "Their role differs between Chapter 7 and Chapter 13.",
            "",
            "Chapter 7 Trustee:",
            "  • Reviews your paperwork for accuracy and completeness",
            "  • Looks for non-exempt assets to sell and pay creditors",
            "  • Runs your 341 meeting",
            "  • In most cases ('no-asset cases'), does nothing and the",
            "    case closes after your discharge",
            "",
            "Chapter 13 Trustee:",
            "  • Reviews and approves your repayment plan",
            "  • Receives your monthly plan payments",
            "  • Distributes money to your creditors each month",
            "  • Monitors compliance for 3-5 years",
            "  • Can move to dismiss your case if you miss payments",
            "",
            "INSIGHT: The trustee works for creditors AND for the integrity",
            "of the bankruptcy system — NOT for you. Be 100% honest in all",
            "your filings. Hiding assets is bankruptcy fraud (a federal crime).",
        ]
    },
    "reaffirmation": {
        "title": "Reaffirmation Agreements  (11 U.S.C. § 524(c))",
        "body": [
            "When you file Chapter 7, a secured debt (car loan, mortgage) is",
            "technically discharged — but the lender can still repossess/",
            "foreclose if you stop paying, because their lien survives.",
            "",
            "A Reaffirmation Agreement is a contract where you agree to remain",
            "personally liable for a debt even after bankruptcy discharge.",
            "",
            "Why you might reaffirm:",
            "  • To keep your car and maintain the loan",
            "  • Your lender requires it to let you keep the car",
            "",
            "Why you might NOT want to reaffirm:",
            "  • If you later can't pay, the lender can sue you personally",
            "  • Without reaffirmation, if you return the car, you owe nothing",
            "  • Reaffirmed debt won't be reported positively to credit bureaus",
            "    unless the lender agrees to do so",
            "",
            "INSIGHT: Many people 'ride through' without reaffirming — they",
            "keep paying the car loan but don't sign a reaffirmation. Many",
            "lenders allow this. Consult your attorney before signing one.",
        ]
    }
}

# ─── Chapter 7 Content ──────────────────────────────────────────────────────
CH7_OVERVIEW = [
    "Chapter 7 is called 'Liquidation Bankruptcy.'",
    "",
    "The big picture:",
    "  • Most of your unsecured debt gets completely ERASED ('discharged')",
    "  • The entire process takes only 3-6 months",
    "  • A court-appointed trustee may sell non-exempt assets to pay creditors",
    "  • Most Chapter 7 cases are 'no-asset' cases — nothing gets sold",
    "",
    "Best for people who:",
    "  ✓ Have mostly unsecured debt (credit cards, medical bills)",
    "  ✓ Have little to no non-exempt property",
    "  ✓ Pass the 'Means Test' (income below state median or low disposable income)",
    "  ✓ Want the fastest path to a fresh start",
    "",
    "NOT ideal if you:",
    "  ✗ Are behind on a mortgage and want to keep your home",
    "  ✗ Have significant non-exempt assets you want to protect",
    "  ✗ Fail the Means Test (too much income)",
    "  ✗ Filed Chapter 7 in the last 8 years",
    "",
    "Effect on credit:",
    "  Stays on credit report for 10 years from filing date.",
    "  Most people can rebuild credit within 2-3 years.",
]

CH7_ELIGIBILITY = {
    "title": "Chapter 7 — Eligibility Requirements",
    "checks": [
        {
            "id": "no_prior_ch7",
            "label": "No Chapter 7 discharge in the last 8 years",
            "explain": "Federal law requires 8 years between Chapter 7 discharges. If you received a Ch7 discharge less than 8 years ago, you cannot file again."
        },
        {
            "id": "no_prior_ch13",
            "label": "No Chapter 13 discharge in the last 6 years",
            "explain": "If you received a Chapter 13 discharge less than 6 years ago, you're ineligible for Chapter 7 (with limited exceptions)."
        },
        {
            "id": "credit_counseling",
            "label": "Completed approved credit counseling within 180 days",
            "explain": "Mandatory under 11 U.S.C. § 109(h). Must be from a DOJ-approved agency. You get a certificate you file with your petition."
        },
        {
            "id": "means_test",
            "label": "Pass the Means Test (11 U.S.C. § 707(b)(2))",
            "explain": "If your income is above your state's median, you must show your disposable income after allowed expenses is below the threshold. Check: justice.gov/ust/means-testing"
        },
        {
            "id": "no_dismissal",
            "label": "No prior case dismissed in the last 180 days for abuse/non-compliance",
            "explain": "If a prior bankruptcy was dismissed 'with prejudice' you may have a waiting period before refiling."
        },
        {
            "id": "good_faith",
            "label": "Filing in good faith — not to defraud creditors",
            "explain": "Courts can dismiss a case filed in bad faith. Do not file bankruptcy to quickly transfer assets to family members or hide property."
        },
    ]
}

CH7_CHECKLIST = [
    {
        "phase": "PHASE 1 — Gather Financial Documents",
        "color": C.CYAN,
        "items": [
            {"id": "c7_tax_returns",   "task": "Last 2 years of federal tax returns"},
            {"id": "c7_paystubs",      "task": "Last 6 months of pay stubs / income records"},
            {"id": "c7_bank_stmts",    "task": "Last 3-6 months of bank statements (all accounts)"},
            {"id": "c7_credit_rpts",   "task": "Pull all 3 credit reports (free at annualcreditreport.com)"},
            {"id": "c7_debt_list",     "task": "List of ALL debts: creditor name, balance, account number, address"},
            {"id": "c7_asset_list",    "task": "List of everything you own: home, car, furniture, jewelry, savings"},
            {"id": "c7_prop_deed",     "task": "Property deed / mortgage statement (if you own real estate)"},
            {"id": "c7_car_value",     "task": "Vehicle value (check Kelley Blue Book or NADA)"},
            {"id": "c7_insurance",     "task": "Life insurance policy details (if any cash value)"},
            {"id": "c7_retirement",    "task": "Retirement account statements (401k, IRA, pension)"},
        ]
    },
    {
        "phase": "PHASE 2 — Pre-Filing Requirements",
        "color": C.MAGENTA,
        "items": [
            {"id": "c7_credit_course",  "task": "Complete credit counseling course (DOJ-approved provider)"},
            {"id": "c7_cert_saved",     "task": "Save the counseling certificate — you MUST file it with the court"},
            {"id": "c7_atty_consult",   "task": "Consult a bankruptcy attorney (strongly recommended)"},
            {"id": "c7_means_test",     "task": "Calculate/verify Means Test qualification"},
            {"id": "c7_exemptions",     "task": "Research which exemptions apply in your state (federal vs. state)"},
            {"id": "c7_stop_payments",  "task": "Decide which creditors to stop paying (non-essential unsecured debt)"},
            {"id": "c7_no_transfers",   "task": "Do NOT transfer property to family/friends — this can be reversed!"},
            {"id": "c7_no_luxury",      "task": "Avoid luxury purchases or cash advances on credit within 90 days"},
        ]
    },
    {
        "phase": "PHASE 3 — Prepare & File the Petition",
        "color": C.YELLOW,
        "items": [
            {"id": "c7_petition",       "task": "Complete Official Bankruptcy Forms (available at uscourts.gov)"},
            {"id": "c7_schedule_ab",    "task": "Schedule A/B: List all your property/assets"},
            {"id": "c7_schedule_c",     "task": "Schedule C: Claim your exemptions"},
            {"id": "c7_schedule_d",     "task": "Schedule D: Secured creditors (mortgage, car loan)"},
            {"id": "c7_schedule_ef",    "task": "Schedule E/F: Priority and unsecured creditors"},
            {"id": "c7_schedule_i",     "task": "Schedule I: Your current income"},
            {"id": "c7_schedule_j",     "task": "Schedule J: Your current monthly expenses"},
            {"id": "c7_means_form",     "task": "Official Form 122A-1: Chapter 7 Means Test Calculation"},
            {"id": "c7_filing_fee",     "task": "Pay filing fee: $338 (or apply for fee waiver if income < 150% poverty)"},
            {"id": "c7_file_court",     "task": "File petition at your local U.S. Bankruptcy Court"},
        ]
    },
    {
        "phase": "PHASE 4 — After Filing",
        "color": C.GREEN,
        "items": [
            {"id": "c7_case_number",    "task": "Receive your case number — the automatic stay is now active!"},
            {"id": "c7_trustee_docs",   "task": "Provide trustee any requested additional documents"},
            {"id": "c7_341_attend",     "task": "Attend 341 Meeting of Creditors (bring ID + SSN card)"},
            {"id": "c7_reaffirmation",  "task": "Decide on reaffirmation agreements for secured debts (car, home)"},
            {"id": "c7_debtor_ed",      "task": "Complete debtor education / financial management course"},
            {"id": "c7_debtor_cert",    "task": "File debtor education certificate with the court (Form 423)"},
            {"id": "c7_discharge",      "task": "Receive discharge order (about 60 days after 341 meeting)"},
            {"id": "c7_close",          "task": "Case closes — review discharge order and keep it FOREVER"},
        ]
    },
    {
        "phase": "PHASE 5 — After Discharge (Fresh Start)",
        "color": C.BLUE,
        "items": [
            {"id": "c7_credit_check",   "task": "Check credit reports — verify discharged debts show $0 balance"},
            {"id": "c7_budget",         "task": "Create a monthly budget to stay debt-free"},
            {"id": "c7_secured_card",   "task": "Consider a secured credit card to rebuild credit"},
            {"id": "c7_emergency_fund", "task": "Start building a $1,000 emergency fund"},
            {"id": "c7_credit_monitor", "task": "Set up credit monitoring (many free options available)"},
        ]
    }
]

CH7_TIMELINE = [
    ("Day 1",          "File petition → Automatic Stay begins immediately"),
    ("Day 1-7",        "Court mails notice to all listed creditors"),
    ("Day 21-40",      "341 Meeting of Creditors (you must attend)"),
    ("Day 60-90",      "Trustee investigation period expires"),
    ("Day 60-90",      "Complete debtor education course & file certificate"),
    ("~Day 90-120",    "Court issues discharge order"),
    ("~Day 120-180",   "Case closes (longer if trustee has assets to administer)"),
]

CH7_INSIGHTS = [
    ("Filing fee waivers",
     "If your income is below 150% of the federal poverty level, you can apply\n"
     "  to have the $338 filing fee completely waived. Use Official Form 103B."),
    ("The 90-day rule",
     "Payments to 'insiders' (family, friends) within 1 year before filing can\n"
     "  be 'clawed back' by the trustee. For other creditors, 90 days. Don't\n"
     "  pay off family loans before filing — it could hurt your case."),
    ("Retirement is safe",
     "ERISA-qualified retirement accounts (401k, 403b, most IRAs up to ~$1.5M)\n"
     "  are generally fully protected in bankruptcy. Never cash out your 401k\n"
     "  to pay debts before filing — that money is protected inside the account."),
    ("Honesty is everything",
     "Hiding assets, lying on the petition, or omitting debts can result in\n"
     "  your discharge being DENIED and criminal prosecution for bankruptcy fraud.\n"
     "  Disclose everything — even things you think you might keep."),
    ("Credit rebuilds faster than you think",
     "Most bankruptcy filers receive credit card offers within 6-12 months.\n"
     "  A secured card + on-time payments can put you at 650+ in 2 years.\n"
     "  Your score can recover more than people expect."),
    ("Tax refunds are an asset",
     "If you file in early spring and you have a large tax refund coming,\n"
     "  that refund may be an asset the trustee can take. Timing your filing\n"
     "  (or adjusting withholding beforehand) can protect it."),
    ("Pro se is possible but risky",
     "You CAN file without an attorney ('pro se'). But errors can result in\n"
     "  case dismissal, loss of assets, or denied discharge. Attorney fees\n"
     "  ($1,000–$2,000) are often worth the protection they provide."),
]

# ─── Chapter 13 Content ─────────────────────────────────────────────────────
CH13_OVERVIEW = [
    "Chapter 13 is called 'Reorganization' or 'Wage Earner's Plan.'",
    "",
    "The big picture:",
    "  • You KEEP all your property — nothing gets liquidated",
    "  • You propose a 3-5 year repayment plan to catch up on debts",
    "  • At the end of the plan, remaining eligible debts are discharged",
    "  • You must have regular income to fund the repayment plan",
    "",
    "Best for people who:",
    "  ✓ Are behind on mortgage payments and want to save their home",
    "  ✓ Have non-exempt assets (equity, business assets) they want to keep",
    "  ✓ Have income too high to pass the Chapter 7 Means Test",
    "  ✓ Need to pay non-dischargeable debts (back taxes, support arrears)",
    "  ✓ Filed Chapter 7 in the last 8 years (so can't file Ch7 again)",
    "",
    "NOT ideal if you:",
    "  ✗ Have no steady income",
    "  ✗ Have unsecured debt over $465,275 (2025 limit)",
    "  ✗ Have secured debt over $1,395,875 (2025 limit)",
    "  ✗ Are a corporation or LLC (individuals only)",
    "",
    "Effect on credit:",
    "  Stays on credit report for 7 years from filing date (shorter than Ch7).",
]

CH13_ELIGIBILITY = {
    "title": "Chapter 13 — Eligibility Requirements",
    "checks": [
        {
            "id": "individual",
            "label": "You are an individual (not a corporation or LLC)",
            "explain": "Chapter 13 is only for individuals and sole proprietors — not business entities."
        },
        {
            "id": "regular_income",
            "label": "You have regular income (wages, self-employment, Social Security, etc.)",
            "explain": "You must have stable income to fund a repayment plan. The source doesn't have to be employment — it can be rental income, SS benefits, pension, etc."
        },
        {
            "id": "debt_limits",
            "label": "Debts are within limits: unsecured < $465,275 / secured < $1,395,875",
            "explain": "These limits are set by Congress and adjust every 3 years. Check current limits at uscourts.gov. If you exceed these, Chapter 11 (business bankruptcy) may apply."
        },
        {
            "id": "credit_counseling",
            "label": "Completed approved credit counseling within 180 days",
            "explain": "Same requirement as Chapter 7 — mandatory under § 109(h). Get the certificate before filing."
        },
        {
            "id": "taxes_filed",
            "label": "Filed all required federal and state tax returns for last 4 years",
            "explain": "Under 11 U.S.C. § 1308, you must file all tax returns due for the 4 years before your case. Unfiled returns can cause your plan to be denied."
        },
        {
            "id": "no_prior_dismissal",
            "label": "No prior bankruptcy dismissed in last 180 days for failure to comply",
            "explain": "Serial filers who had a case dismissed for missing deadlines or court orders may face a 180-day bar on refiling."
        },
    ]
}

CH13_CHECKLIST = [
    {
        "phase": "PHASE 1 — Gather Financial Documents",
        "color": C.CYAN,
        "items": [
            {"id": "c13_tax_returns",    "task": "Last 4 years of federal AND state tax returns (all must be filed!)"},
            {"id": "c13_paystubs",       "task": "Last 6 months of pay stubs / proof of all income"},
            {"id": "c13_bank_stmts",     "task": "Last 3-6 months of bank statements (all accounts)"},
            {"id": "c13_mortgage",       "task": "Mortgage statement(s): balance, monthly payment, arrears amount"},
            {"id": "c13_car_loans",      "task": "Car loan statements: balance, monthly payment, purchase date"},
            {"id": "c13_credit_rpts",    "task": "All 3 credit reports — list EVERY creditor with address + balance"},
            {"id": "c13_asset_values",   "task": "Current value of all assets (home appraisal, car value, etc.)"},
            {"id": "c13_monthly_exp",    "task": "Document all monthly expenses in detail (rent, utilities, food, etc.)"},
            {"id": "c13_retirement",     "task": "Retirement account statements"},
            {"id": "c13_biz_docs",       "task": "Business income/expense records if self-employed"},
        ]
    },
    {
        "phase": "PHASE 2 — Pre-Filing Requirements",
        "color": C.MAGENTA,
        "items": [
            {"id": "c13_file_taxes",     "task": "FILE all unfiled tax returns for last 4 years (required by law)"},
            {"id": "c13_credit_course",  "task": "Complete credit counseling course (DOJ-approved provider)"},
            {"id": "c13_cert_saved",     "task": "Save the counseling certificate — file it with the petition"},
            {"id": "c13_atty_consult",   "task": "Consult a bankruptcy attorney (highly recommended for Ch13)"},
            {"id": "c13_plan_draft",     "task": "Draft repayment plan: calculate disposable income for plan payment"},
            {"id": "c13_mortgage_arrs",  "task": "Calculate total mortgage arrears to include in plan"},
            {"id": "c13_priority_debts", "task": "Identify priority debts (taxes, support) — must be paid 100% in plan"},
            {"id": "c13_exemptions",     "task": "Verify exemptions — must pay unsecured creditors at least what Ch7 would"},
        ]
    },
    {
        "phase": "PHASE 3 — Prepare & File the Petition",
        "color": C.YELLOW,
        "items": [
            {"id": "c13_petition",       "task": "Complete all Official Bankruptcy Forms (uscourts.gov)"},
            {"id": "c13_schedules",      "task": "Complete all Schedules A/B through J (assets, debts, income, expenses)"},
            {"id": "c13_means_form",     "task": "Official Form 122C: Chapter 13 Calculation of Disposable Income"},
            {"id": "c13_plan_form",      "task": "Official Form 113: Chapter 13 Plan (detailed repayment plan)"},
            {"id": "c13_filing_fee",     "task": "Pay filing fee: $313 (fee waivers NOT available for Chapter 13)"},
            {"id": "c13_file_court",     "task": "File petition at local U.S. Bankruptcy Court"},
            {"id": "c13_auto_stay",      "task": "Automatic stay begins — notify mortgage servicer immediately!"},
        ]
    },
    {
        "phase": "PHASE 4 — Plan Confirmation Process",
        "color": C.GREEN,
        "items": [
            {"id": "c13_first_payment",  "task": "Begin plan payments within 30 days of filing (before confirmation!)"},
            {"id": "c13_341_attend",     "task": "Attend 341 Meeting of Creditors (bring ID + SSN card)"},
            {"id": "c13_creditor_obj",   "task": "Respond to any creditor objections to your plan"},
            {"id": "c13_confirmation",   "task": "Attend confirmation hearing (court approves/modifies your plan)"},
            {"id": "c13_plan_approved",  "task": "Receive plan confirmation order from court"},
        ]
    },
    {
        "phase": "PHASE 5 — During the Plan (3-5 Years)",
        "color": C.BLUE,
        "items": [
            {"id": "c13_payments",       "task": "Make EVERY plan payment on time — missing payments = dismissal"},
            {"id": "c13_tax_returns",    "task": "File all tax returns every year — provide copies to trustee"},
            {"id": "c13_tax_refunds",    "task": "Report all tax refunds to trustee (may need to turn over large ones)"},
            {"id": "c13_notify_changes", "task": "Notify attorney/court of income changes, new debts, or major expenses"},
            {"id": "c13_debtor_ed",      "task": "Complete debtor education course before end of plan"},
            {"id": "c13_modify_plan",    "task": "Modify plan if circumstances change (job loss, income increase)"},
        ]
    },
    {
        "phase": "PHASE 6 — Completing the Plan & Discharge",
        "color": C.MAGENTA,
        "items": [
            {"id": "c13_all_paid",       "task": "All plan payments completed successfully"},
            {"id": "c13_cert_filed",     "task": "File debtor education certificate with court"},
            {"id": "c13_cert_payments",  "task": "Certify no domestic support obligation arrears (if applicable)"},
            {"id": "c13_discharge",      "task": "Receive discharge order — remaining eligible debts erased!"},
            {"id": "c13_credit_check",   "task": "Check credit reports — verify all discharged debts reflect correctly"},
        ]
    }
]

CH13_TIMELINE = [
    ("Day 1",           "File petition → Automatic Stay begins immediately"),
    ("Within 30 days",  "FIRST plan payment due to trustee (before confirmation!)"),
    ("Day 21-50",       "341 Meeting of Creditors"),
    ("Day 45",          "Deadline for secured creditors to file claims"),
    ("Day 90",          "Deadline for unsecured creditors to file claims"),
    ("Day 45-90+",      "Plan confirmation hearing (court approves your plan)"),
    ("Month 1-60",      "Monthly plan payments to trustee"),
    ("Year 3 or 5",     "Final plan payment made"),
    ("After final pmt", "Complete debtor education + file certificate"),
    ("~30 days later",  "Discharge order issued — case closes"),
]

CH13_PLAN_EXPLAINER = [
    "Your repayment plan is the heart of Chapter 13. Here's how it works:",
    "",
    "What gets paid FIRST (Priority Debts — must be paid 100%):",
    "  1. Back child support / alimony arrears",
    "  2. Recent income taxes (generally last 3 years)",
    "  3. Administrative costs (trustee fee, attorney fees)",
    "",
    "What gets paid SECOND (Secured Debts):",
    "  • Mortgage arrears (catch up on overdue payments over plan term)",
    "  • Car loans (possibly at reduced interest rate — 'cramdown'*)",
    "  • Other secured debts",
    "",
    "What gets paid LAST (Unsecured Debts):",
    "  • Credit cards, medical bills, personal loans",
    "  • Must receive AT LEAST what they'd get in Chapter 7 ('best interest test')",
    "  • Often pennies on the dollar or nothing",
    "  • Remaining balance discharged at end of plan",
    "",
    "How your plan payment is calculated:",
    "  Monthly Disposable Income = Income − Allowed Expenses",
    "  Plan Payment ≥ Monthly Disposable Income",
    "  Plan Payment must also cover all priority and secured debt in full",
    "",
    "* Cramdown: If you bought your car 910+ days before filing, you can reduce",
    "  the loan balance to the car's current market value — potentially saving",
    "  thousands. The interest rate is also reduced to ~prime + 1-2%.",
]

CH13_INSIGHTS = [
    ("Save your home from foreclosure",
     "Chapter 13's #1 superpower. Once you file, the automatic stay stops\n"
     "  foreclosure. Your plan can spread mortgage arrears over 3-5 years.\n"
     "  If you can afford current payments + arrear catch-up, you keep the home."),
    ("The 910-day car rule",
     "If you've owned your car for 910+ days (about 2.5 years) before filing,\n"
     "  you can 'cram down' the loan to the car's current value. Example:\n"
     "  You owe $18,000 on a car worth $10,000 — you only pay $10,000 in the plan."),
    ("Strip a second mortgage",
     "If your home is worth LESS than what you owe on your first mortgage,\n"
     "  a second mortgage or HELOC can be 'stripped' off (treated as unsecured\n"
     "  debt and discharged at end of plan). This is huge for underwater homeowners."),
    ("Missing a payment is serious",
     "Miss your trustee payments and your case can be dismissed. With dismissal,\n"
     "  the automatic stay ends and creditors can immediately resume collections.\n"
     "  Set up automatic payments to the trustee if at all possible."),
    ("Tax refunds go to the trustee",
     "In Chapter 13, large tax refunds may need to be turned over to the trustee\n"
     "  to pay creditors. Consider adjusting your W-4 withholding to reduce refunds\n"
     "  and take home more money each paycheck instead."),
    ("The hardship discharge",
     "If you can't complete the plan due to circumstances beyond your control\n"
     "  (serious illness, job loss), you may qualify for a 'hardship discharge'\n"
     "  under 11 U.S.C. § 1328(b). It's harder to get but it exists."),
    ("Attorney fees are built into the plan",
     "Chapter 13 attorney fees ($3,000–$5,000) are typically paid through the\n"
     "  repayment plan — not all upfront. This makes it more accessible even when\n"
     "  you're already struggling financially."),
]

# ─── Comparison Content ─────────────────────────────────────────────────────
COMPARISON_TABLE = [
    ("Process Time",         "3–6 months",            "3–5 years"),
    ("Filing Fee",           "$338",                  "$313"),
    ("Keep Property?",       "Maybe (exempt assets)",  "Yes — all of it"),
    ("Income Requirement",   "Low/no income preferred","Must have regular income"),
    ("Debt Limits",          "None",                  "Secured < $1.4M, Unsecured < $465K"),
    ("Mortgage Arrears",     "Cannot cure arrears",   "Can cure in plan (save home)"),
    ("Student Loans",        "Not discharged",        "Not discharged"),
    ("Tax Debt",             "Old taxes only",        "Can pay over plan term"),
    ("Credit Report Impact", "10 years",              "7 years"),
    ("Prior Ch7 bar",        "8 years between filings","4 years after Ch7"),
    ("Co-signer protection", "None",                  "Co-debtor stay available"),
    ("Disposable income",    "Can keep it",           "Must pay to creditors"),
]

# ─── Resources ──────────────────────────────────────────────────────────────
RESOURCES = [
    ("U.S. Courts — Bankruptcy Forms",
     "uscourts.gov/forms/bankruptcy-forms",
     "Official petition forms, all schedules, plan forms — all free"),
    ("DOJ U.S. Trustee — Means Test Data",
     "justice.gov/ust/means-testing",
     "Current median income figures and expense standards by state"),
    ("DOJ — Approved Credit Counseling Agencies",
     "justice.gov/ust/credit-counseling-debtor-education-information",
     "Find a court-approved credit counseling or debtor education provider"),
    ("PACER — Federal Court Records",
     "pacer.gov",
     "Access your filed court documents and case docket"),
    ("AnnualCreditReport.com",
     "annualcreditreport.com",
     "Free credit reports from all 3 bureaus — required for filing"),
    ("National Association of Consumer Bankruptcy Attorneys",
     "nacba.org",
     "Find a certified bankruptcy attorney near you"),
    ("Legal Aid Resources",
     "lawhelp.org",
     "Free or low-cost legal help if you can't afford an attorney"),
    ("Federal Poverty Guidelines",
     "aspe.hhs.gov/poverty-guidelines",
     "Used to determine fee waivers and eligibility thresholds"),
    ("IRS Collection Financial Standards",
     "irs.gov/businesses/small-businesses-self-employed/collection-financial-standards",
     "The expense standards used in the Chapter 7 Means Test"),
]

# ─── Interactive Checklist ──────────────────────────────────────────────────
def run_checklist(chapter_label, phases, state_key, state):
    tasks = state.get(state_key, {})
    while True:
        clear()
        section(f"{chapter_label} — Interactive Checklist")
        all_done = 0
        all_total = 0
        for phase in phases:
            done = sum(1 for item in phase["items"] if tasks.get(item["id"]))
            total = len(phase["items"])
            all_done += done
            all_total += total
            pct = int(done / total * 100)
            bar = "█" * (pct // 5) + "░" * (20 - pct // 5)
            print(f"  {phase['color']}{phase['phase']}{C.RESET}")
            print(f"  Progress: [{bar}] {done}/{total}  ({pct}%)\n")

        overall_pct = int(all_done / all_total * 100) if all_total else 0
        print(f"{C.BOLD}  Overall progress: {all_done}/{all_total} tasks ({overall_pct}%){C.RESET}")

        choice = menu("Checklist Options", [
            "View & mark tasks in a phase",
            "View all incomplete tasks",
            "Reset progress for this chapter",
        ])

        if choice == 0:
            break
        elif choice == 1:
            phase_names = [p["phase"] for p in phases]
            ph_choice = menu("Select Phase", phase_names)
            if ph_choice == 0:
                continue
            phase = phases[ph_choice - 1]
            while True:
                clear()
                print(f"\n{phase['color']}{C.BOLD}{phase['phase']}{C.RESET}\n")
                for i, item in enumerate(phase["items"], 1):
                    status = ok("✓") if tasks.get(item["id"]) else warn("○")
                    print(f"  {status} {i:2}. {item['task']}")
                print(f"\n  {C.CYAN}0{C.RESET}. Back")
                raw = input(f"\n{C.BOLD}Toggle task number (or 0 to go back): {C.RESET}").strip()
                if raw == "0":
                    break
                if raw.isdigit() and 1 <= int(raw) <= len(phase["items"]):
                    item = phase["items"][int(raw) - 1]
                    tasks[item["id"]] = not tasks.get(item["id"], False)
                    state[state_key] = tasks
                    save_state(state)
                    status_word = ok("DONE") if tasks[item["id"]] else warn("not done")
                    print(f"  Marked as {status_word}: {item['task']}")
                    pause()

        elif choice == 2:
            clear()
            section("Incomplete Tasks")
            found = False
            for phase in phases:
                incomplete = [item for item in phase["items"] if not tasks.get(item["id"])]
                if incomplete:
                    found = True
                    print(f"  {phase['color']}{phase['phase']}{C.RESET}")
                    for item in incomplete:
                        print(f"    {warn('○')} {item['task']}")
                    print()
            if not found:
                print(ok("  All tasks complete! Congratulations!"))
            pause()

        elif choice == 3:
            confirm = input(warn("  Reset ALL progress for this chapter? (yes/no): ")).strip().lower()
            if confirm == "yes":
                state[state_key] = {}
                tasks = {}
                save_state(state)
                print(ok("  Progress reset."))
                pause()

# ─── Explainer Menu ──────────────────────────────────────────────────────────
def show_explainer(key):
    e = EXPLAINERS[key]
    clear()
    box(e["title"], e["body"], C.CYAN)
    pause()

def explainer_menu():
    titles = {
        "automatic_stay":      "Automatic Stay — Collections stop immediately",
        "means_test":          "The Means Test — Do you qualify for Chapter 7?",
        "dischargeable_debts": "Dischargeable Debts — What gets erased?",
        "exemptions":          "Exemptions — What property you keep",
        "341_meeting":         "The 341 Meeting — What to expect",
        "credit_counseling":   "Credit Counseling — Mandatory requirement",
        "trustee":             "The Bankruptcy Trustee — Their role",
        "reaffirmation":       "Reaffirmation Agreements — Keeping secured debt",
    }
    keys = list(titles.keys())
    labels = list(titles.values())
    while True:
        choice = menu("Key Concepts — Explainers", labels)
        if choice == 0:
            break
        show_explainer(keys[choice - 1])

# ─── Comparison Screen ──────────────────────────────────────────────────────
def show_comparison():
    clear()
    section("Chapter 7 vs. Chapter 13 — Side-by-Side Comparison")
    col1 = 28
    col2 = 24
    col3 = 30
    header = f"  {'Feature':<{col1}} {C.CYAN}{'Chapter 7':<{col2}}{C.RESET} {C.MAGENTA}{'Chapter 13':<{col3}}{C.RESET}"
    sep    = "  " + "─" * (col1 + col2 + col3 + 2)
    print(header)
    print(sep)
    for feat, ch7, ch13 in COMPARISON_TABLE:
        print(f"  {bold(feat):<{col1+9}} {C.CYAN}{ch7:<{col2}}{C.RESET} {C.MAGENTA}{ch13:<{col3}}{C.RESET}")
    print()
    section("Quick Decision Guide")
    print(f"  {C.CYAN}Choose Chapter 7 if:{C.RESET}")
    print("    • You mostly have credit cards, medical bills, or personal loans")
    print("    • You have few non-exempt assets")
    print("    • Your income is low or you pass the Means Test")
    print("    • You want this resolved quickly (3-6 months)")
    print()
    print(f"  {C.MAGENTA}Choose Chapter 13 if:{C.RESET}")
    print("    • You're behind on your mortgage and want to save your home")
    print("    • You have assets you'd lose in Chapter 7")
    print("    • Your income is too high for Chapter 7")
    print("    • You have significant tax or support debt to repay over time")
    print()
    print(dim("  Note: A bankruptcy attorney can run both scenarios and tell you"))
    print(dim("  which provides the most benefit for your specific situation."))
    pause()

# ─── Insights Screen ────────────────────────────────────────────────────────
def show_insights(chapter_label, insights):
    clear()
    section(f"{chapter_label} — Insights & Tips")
    for i, (title, body) in enumerate(insights, 1):
        print(f"  {C.CYAN}{C.BOLD}{i}. {title}{C.RESET}")
        for line in body.split("\n"):
            print(f"  {line}")
        print()
    pause()

# ─── Timeline Screen ────────────────────────────────────────────────────────
def show_timeline(chapter_label, timeline):
    clear()
    section(f"{chapter_label} — Timeline Overview")
    for timing, event in timeline:
        print(f"  {C.CYAN}{timing:<20}{C.RESET}  {event}")
    print()
    pause()

# ─── Resources Screen ───────────────────────────────────────────────────────
def show_resources():
    clear()
    section("Federal Resources & Important Links")
    print(dim("  These are official government and trusted resources.\n"))
    for name, url, desc in RESOURCES:
        print(f"  {C.BOLD}{name}{C.RESET}")
        print(f"  {C.CYAN}  → {url}{C.RESET}")
        print(f"     {dim(desc)}\n")
    print(warn("  IMPORTANT: Always verify current figures and forms at official"))
    print(warn("  government websites — rules and dollar amounts change periodically."))
    pause()

# ─── Eligibility Checker ────────────────────────────────────────────────────
def check_eligibility(chapter_label, checks):
    clear()
    section(f"{chapter_label} — Eligibility Checklist")
    print(dim("  Answer honestly. This is for your information only — not legal advice.\n"))
    results = []
    for check in checks:
        print(f"  {C.BOLD}{check['label']}{C.RESET}")
        print(f"  {dim(check['explain'])}\n")
        while True:
            ans = input(f"  {C.CYAN}Do you meet this requirement? (y/n/skip): {C.RESET}").strip().lower()
            if ans in ("y", "n", "skip", ""):
                break
        results.append((check["label"], ans))
        print()

    clear()
    section(f"{chapter_label} — Eligibility Results")
    passed = 0
    failed = 0
    skipped = 0
    for label, ans in results:
        if ans == "y":
            print(f"  {ok('✓')} {label}")
            passed += 1
        elif ans == "n":
            print(f"  {err('✗')} {label}")
            failed += 1
        else:
            print(f"  {warn('?')} {label} {dim('(skipped)')}")
            skipped += 1

    print()
    if failed == 0 and passed > 0:
        print(ok(f"  Preliminary result: You appear to meet the requirements."))
        print(ok(f"  ({passed} requirements met, {skipped} skipped)"))
    elif failed > 0:
        print(warn(f"  Note: You indicated {failed} requirement(s) may not be met."))
        print(warn("  This does NOT mean you cannot file — consult a bankruptcy attorney"))
        print(warn("  to review your specific situation before concluding you're ineligible."))
    print(f"\n  {dim('This tool is not a substitute for legal advice.')}")
    pause()

# ─── Chapter 7 Menu ─────────────────────────────────────────────────────────
def chapter7_menu(state):
    while True:
        choice = menu("CHAPTER 7 — Liquidation Bankruptcy", [
            "Overview — What is Chapter 7?",
            "Eligibility Checker",
            "Step-by-Step Checklist (track your progress)",
            "Timeline",
            "Key Concepts & Explainers",
            "Insights & Tips",
        ])
        if choice == 0:
            break
        elif choice == 1:
            clear()
            section("Chapter 7 — Overview")
            for line in CH7_OVERVIEW:
                print(f"  {line}")
            pause()
        elif choice == 2:
            check_eligibility("Chapter 7", CH7_ELIGIBILITY["checks"])
        elif choice == 3:
            run_checklist("Chapter 7", CH7_CHECKLIST, "ch7", state)
        elif choice == 4:
            show_timeline("Chapter 7", CH7_TIMELINE)
        elif choice == 5:
            explainer_menu()
        elif choice == 6:
            show_insights("Chapter 7", CH7_INSIGHTS)

# ─── Chapter 13 Menu ────────────────────────────────────────────────────────
def chapter13_menu(state):
    while True:
        choice = menu("CHAPTER 13 — Repayment Plan Bankruptcy", [
            "Overview — What is Chapter 13?",
            "Eligibility Checker",
            "Step-by-Step Checklist (track your progress)",
            "Timeline",
            "How the Repayment Plan Works",
            "Key Concepts & Explainers",
            "Insights & Tips",
        ])
        if choice == 0:
            break
        elif choice == 1:
            clear()
            section("Chapter 13 — Overview")
            for line in CH13_OVERVIEW:
                print(f"  {line}")
            pause()
        elif choice == 2:
            check_eligibility("Chapter 13", CH13_ELIGIBILITY["checks"])
        elif choice == 3:
            run_checklist("Chapter 13", CH13_CHECKLIST, "ch13", state)
        elif choice == 4:
            show_timeline("Chapter 13", CH13_TIMELINE)
        elif choice == 5:
            clear()
            section("Chapter 13 — How Your Repayment Plan Works")
            for line in CH13_PLAN_EXPLAINER:
                print(f"  {line}")
            pause()
        elif choice == 6:
            explainer_menu()
        elif choice == 7:
            show_insights("Chapter 13", CH13_INSIGHTS)

# ─── Intake & Assessment Flow ───────────────────────────────────────────────
def ask(prompt, options=None, yes_no=False):
    """Ask a question and return the answer."""
    if yes_no:
        print(f"  {C.BOLD}{prompt}{C.RESET}")
        while True:
            ans = input(f"  {C.CYAN}(y/n): {C.RESET}").strip().lower()
            if ans in ("y", "yes"):
                return True
            if ans in ("n", "no"):
                return False
            print(warn("  Please enter y or n."))
    elif options:
        print(f"  {C.BOLD}{prompt}{C.RESET}")
        for i, opt in enumerate(options, 1):
            print(f"    {C.CYAN}{i}{C.RESET}. {opt}")
        while True:
            ans = input(f"  {C.CYAN}Choose (1-{len(options)}): {C.RESET}").strip()
            if ans.isdigit() and 1 <= int(ans) <= len(options):
                return int(ans)
            print(warn(f"  Please enter a number 1-{len(options)}."))
    else:
        print(f"  {C.BOLD}{prompt}{C.RESET}")
        return input(f"  {C.CYAN}→ {C.RESET}").strip()

def intake_flow(state):
    clear()
    section("Personal Intake Assessment")
    print(f"  {dim('Answer a few questions so we can guide you to the right path.')}")
    print(f"  {dim('All answers are private — nothing is sent anywhere.')}\n")

    # Collect answers
    answers = {}

    print(f"  {C.MAGENTA}── About You ──────────────────────────────{C.RESET}\n")
    answers["name"] = ask("What should we call you? (first name or nickname)")

    answers["income"] = ask(
        f"\nDo you have regular income? (job, self-employment, Social Security, pension, etc.)",
        yes_no=True
    )
    if answers["income"]:
        answers["income_level"] = ask(
            "\nApproximately how much is your gross monthly income?",
            options=[
                "Under $2,000 / month",
                "$2,000 – $4,000 / month",
                "$4,000 – $7,000 / month",
                "Over $7,000 / month",
                "It varies significantly month to month",
            ]
        )

    print(f"\n  {C.MAGENTA}── About Your Debts ───────────────────────{C.RESET}\n")
    answers["debt_types"] = ask(
        "What types of debt are you dealing with? (pick the MAIN type)",
        options=[
            "Credit cards / personal loans / medical bills",
            "Mortgage arrears (behind on home payments)",
            "Car loan trouble (behind or owe more than car is worth)",
            "Back taxes (federal or state income taxes)",
            "Student loans",
            "A mix of several types",
        ]
    )
    answers["debt_amount"] = ask(
        "\nApproximately how much total debt do you have?",
        options=[
            "Under $10,000",
            "$10,000 – $50,000",
            "$50,000 – $150,000",
            "$150,000 – $500,000",
            "Over $500,000",
        ]
    )

    print(f"\n  {C.MAGENTA}── About Your Property ────────────────────{C.RESET}\n")
    answers["owns_home"] = ask("Do you own a home or real estate?", yes_no=True)
    if answers["owns_home"]:
        answers["home_behind"] = ask("Are you behind on your mortgage payments?", yes_no=True)
        answers["home_equity"] = ask(
            "Does your home have equity? (it's worth MORE than you owe on the mortgage)",
            yes_no=True
        )
    answers["owns_car"] = ask("\nDo you own a vehicle?", yes_no=True)
    if answers["owns_car"]:
        answers["car_loan"] = ask("Do you have a car loan you're struggling with?", yes_no=True)

    answers["has_retirement"] = ask(
        "\nDo you have a retirement account (401k, IRA, pension)?", yes_no=True
    )

    print(f"\n  {C.MAGENTA}── Prior Bankruptcy History ────────────────{C.RESET}\n")
    answers["prior_bk"] = ask("Have you ever filed for bankruptcy before?", yes_no=True)
    if answers["prior_bk"]:
        answers["prior_ch7"] = ask("Was it a Chapter 7 (debt erasure / discharge)?", yes_no=True)
        answers["prior_when"] = ask(
            "Approximately when was it?",
            options=[
                "Less than 4 years ago",
                "4-6 years ago",
                "6-8 years ago",
                "More than 8 years ago",
            ]
        )

    print(f"\n  {C.MAGENTA}── Urgency ─────────────────────────────────{C.RESET}\n")
    answers["urgency"] = ask(
        "Is there an urgent situation driving your interest in bankruptcy?",
        options=[
            "Foreclosure is pending or scheduled",
            "Wage garnishment is happening",
            "Bank account has been levied / frozen",
            "Lawsuit has been filed against me",
            "Repossession is threatened",
            "No immediate emergency — planning ahead",
        ]
    )

    # ── Analysis ──
    clear()
    section(f"Your Assessment Results — {answers.get('name', 'Hello')}")

    name = answers.get("name", "")
    rec = None       # "ch7", "ch13", "either", "consult"
    flags = []       # list of highlighted notes
    next_steps = []

    # Emergency flag
    if answers.get("urgency") in (1, 2, 3, 4, 5):
        urgency_map = {
            1: ("FORECLOSURE ALERT", "Filing bankruptcy today triggers the automatic stay and immediately stops foreclosure proceedings. Do not delay — every day matters."),
            2: ("WAGE GARNISHMENT ALERT", "Filing bankruptcy triggers the automatic stay which halts wage garnishment the same day the case is filed."),
            3: ("BANK LEVY ALERT", "Filing triggers the automatic stay — bank levies stop immediately. Act quickly; funds already taken may be harder to recover."),
            4: ("LAWSUIT ALERT", "Filing triggers the automatic stay and freezes the lawsuit. This buys time regardless of which chapter you file."),
            5: ("REPOSSESSION ALERT", "Filing triggers the automatic stay — repossession attempts must stop immediately upon filing."),
        }
        key = answers["urgency"]
        if key in urgency_map:
            title, msg = urgency_map[key]
            print(f"  {C.BG_RED}{C.WHITE}{C.BOLD}  ⚠  {title}  {C.RESET}")
            print(f"\n  {msg}\n")
            flags.append(("Contact a bankruptcy attorney TODAY", "Given your urgent situation, time is critical. Many attorneys offer same-day emergency filings."))
            next_steps.insert(0, "URGENT: Call a bankruptcy attorney today — emergency filing may be possible same-day")

    # Chapter recommendation logic
    income_ok_ch7 = answers.get("income_level") in (1, 2, 3, None) or not answers.get("income")
    wants_home    = answers.get("owns_home") and answers.get("home_behind")
    has_excess    = answers.get("owns_home") and answers.get("home_equity")
    has_income    = answers.get("income", False)
    prior_ch7_bar = answers.get("prior_bk") and answers.get("prior_ch7") and answers.get("prior_when") in (1, 2, 3)

    debt_type = answers.get("debt_types", 1)
    debt_amt  = answers.get("debt_amount", 2)

    if prior_ch7_bar:
        rec = "ch13"
        flags.append(("Prior Chapter 7 may bar refiling", "If your last Chapter 7 discharge was within 8 years, you cannot receive another Chapter 7 discharge. Chapter 13 may still be available."))
    elif wants_home:
        rec = "ch13"
        flags.append(("Mortgage arrears — Chapter 13 is ideal", "Chapter 13's single biggest advantage is the ability to cure mortgage arrears in a repayment plan and save your home."))
    elif debt_type == 2:  # mortgage focused
        rec = "ch13"
    elif debt_type == 5:  # student loans
        flags.append(("Student loans — largely non-dischargeable", "Student loans survive bankruptcy in almost all cases. However, if other debts are erased, it frees up cash to pay student loans. Consider this carefully."))
        rec = "consult"
    elif has_excess and not income_ok_ch7:
        rec = "ch13"
        flags.append(("Home equity & higher income", "You have home equity to protect AND your income may disqualify you from Chapter 7. Chapter 13 may be the better fit."))
    elif income_ok_ch7 and not has_excess:
        rec = "ch7"
    elif not has_income:
        flags.append(("No regular income", "Chapter 13 requires regular income to fund a repayment plan. Without income, Chapter 13 may not be available to you. Chapter 7 may be more appropriate."))
        rec = "ch7"
    else:
        rec = "either"

    # High debt check
    if debt_amt == 5 and rec != "consult":
        flags.append(("Very high debt levels", "With over $500K in total debt, if much of it is secured, you may be approaching Chapter 13's debt limits. An attorney should evaluate whether Chapter 11 might apply."))

    # Display recommendation
    rec_labels = {
        "ch7":     ("Chapter 7", C.CYAN,    "Liquidation — erase most debt in 3-6 months"),
        "ch13":    ("Chapter 13", C.MAGENTA,"Repayment plan — keep assets, save home, 3-5 years"),
        "either":  ("Either Chapter", C.YELLOW, "Both may work — see comparison for details"),
        "consult": ("Attorney Consultation", C.RED, "Your situation needs professional review first"),
    }
    r_label, r_color, r_desc = rec_labels.get(rec, rec_labels["either"])
    print(f"  {r_color}{C.BOLD}Recommended Path:  {r_label}{C.RESET}")
    print(f"  {dim(r_desc)}\n")

    # Flags
    if flags:
        print(f"  {C.BOLD}Important Notes for Your Situation:{C.RESET}")
        for ftitle, fmsg in flags:
            print(f"\n  {warn('►')} {C.BOLD}{ftitle}{C.RESET}")
            print(f"    {fmsg}")
        print()

    # Retirement note
    if answers.get("has_retirement"):
        print(f"  {ok('✓')} {C.BOLD}Your retirement accounts are protected.{C.RESET}")
        print(f"    ERISA-qualified accounts (401k, IRA, pension) are fully exempt in bankruptcy.")
        print(f"    {warn('DO NOT cash out retirement savings to pay debts before filing.')}\n")

    # Credit counseling
    print(f"  {C.BOLD}Universal Next Steps — Required Before ANY Filing:{C.RESET}")
    next_steps_standard = [
        f"Complete a DOJ-approved credit counseling course (justice.gov/ust — search 'approved agencies')",
        f"Pull your credit reports from all 3 bureaus at annualcreditreport.com",
        f"List every debt: creditor name, balance, last-known address",
        f"Gather last 6 months of pay stubs and last 2 years of tax returns",
        f"Consult a bankruptcy attorney (nacba.org for referrals; many offer free consults)",
    ]
    if rec == "ch13":
        next_steps_standard.insert(1, "File any unfiled tax returns for the last 4 years (required for Chapter 13)")
    for i, step in enumerate(next_steps, 1):
        print(f"\n  {C.RED}{C.BOLD}! {step}{C.RESET}")
    for i, step in enumerate(next_steps_standard, len(next_steps) + 1):
        print(f"\n  {C.CYAN}{i}. {step}{C.RESET}")

    print()
    print(f"  {dim('Your intake assessment is complete. Use the main menu to')}")
    print(f"  {dim('open your personalized checklist and step-by-step guide.')}")
    pause()
    return rec

# ─── Disclaimer ─────────────────────────────────────────────────────────────
def show_disclaimer():
    clear()
    lines = [
        "This planner is for EDUCATIONAL PURPOSES ONLY.",
        "",
        "It is NOT legal advice and does NOT create an attorney-client",
        "relationship. Bankruptcy law is complex and fact-specific.",
        "",
        "Dollar amounts, income limits, and exemption figures change",
        "periodically. Always verify current figures at:",
        "  uscourts.gov  |  justice.gov/ust",
        "",
        "STRONGLY RECOMMENDED: Consult a licensed bankruptcy attorney",
        "before filing. Many offer free initial consultations.",
        "Search: nacba.org  or  lawhelp.org",
        "",
        f"Last updated reference: Federal law as of 2025.",
        f"Your session date: {date.today().strftime('%B %d, %Y')}",
    ]
    box("IMPORTANT LEGAL DISCLAIMER", lines, C.RED)
    input(f"\n  {dim('I understand — press Enter to continue.')}")

# ─── Main Menu ──────────────────────────────────────────────────────────────
def main():
    show_disclaimer()

    state = load_state()

    while True:
        clear()
        print(f"""
{C.BOLD}{C.CYAN}╔══════════════════════════════════════════════════════════╗
║         BANKRUPTCY PREPARATION PLANNER                  ║
║         Chapter 7 & Chapter 13  |  Federal Guidelines  ║
║         Designed for Novices — Not Legal Advice         ║
╚══════════════════════════════════════════════════════════╝{C.RESET}
""")

        # Progress summary
        ch7_tasks  = state.get("ch7", {})
        ch13_tasks = state.get("ch13", {})
        ch7_done   = sum(1 for p in CH7_CHECKLIST  for i in p["items"] if ch7_tasks.get(i["id"]))
        ch7_total  = sum(len(p["items"]) for p in CH7_CHECKLIST)
        ch13_done  = sum(1 for p in CH13_CHECKLIST for i in p["items"] if ch13_tasks.get(i["id"]))
        ch13_total = sum(len(p["items"]) for p in CH13_CHECKLIST)

        print(f"  {C.BOLD}Your Progress:{C.RESET}")
        print(f"  Chapter 7:  {ok(str(ch7_done))}/{ch7_total} tasks  |  Chapter 13: {ok(str(ch13_done))}/{ch13_total} tasks")
        print()

        choice = menu("Main Menu", [
            "Start Here — Personal Intake & Guided Assessment",
            "Chapter 7  — Liquidation Bankruptcy (erase debt in 3-6 months)",
            "Chapter 13 — Repayment Plan (save home, keep assets, 3-5 years)",
            "Compare Chapter 7 vs. Chapter 13",
            "Key Concepts & Explainers (terms explained simply)",
            "Federal Resources & Important Links",
        ])

        if choice == 0:
            clear()
            print(f"\n{ok('Thank you for using the Bankruptcy Preparation Planner.')}")
            print(f"{dim('Your progress has been saved to: bankruptcy_progress.json')}")
            print(f"{dim('Consult a bankruptcy attorney before filing.')}\n")
            sys.exit(0)
        elif choice == 1:
            rec = intake_flow(state)
            # After intake, offer to jump directly to recommended chapter
            if rec == "ch7":
                go = input(f"\n  {C.CYAN}Open Chapter 7 checklist now? (y/n): {C.RESET}").strip().lower()
                if go == "y":
                    chapter7_menu(state)
            elif rec == "ch13":
                go = input(f"\n  {C.CYAN}Open Chapter 13 checklist now? (y/n): {C.RESET}").strip().lower()
                if go == "y":
                    chapter13_menu(state)
            elif rec == "either":
                show_comparison()
        elif choice == 2:
            chapter7_menu(state)
        elif choice == 3:
            chapter13_menu(state)
        elif choice == 4:
            show_comparison()
        elif choice == 5:
            explainer_menu()
        elif choice == 6:
            show_resources()

if __name__ == "__main__":
    main()
