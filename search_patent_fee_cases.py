#!/usr/bin/env python
"""
Search for patent infringement cases with § 285 attorney fee awards.

Criteria:
- Filed 2020-2025
- NPE plaintiff vs. major tech defendant
- Software patents (streaming, cloud, mobile, SaaS, etc.)
- § 285 exceptional case fee awards granted ($500K-$10M)
- Courts: N.D. Cal, D. Del, E.D. Tex, W.D. Tex, C.D. Cal
"""
import os
import sys
import django
import re
from datetime import datetime
from collections import defaultdict

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cl.settings')
sys.path.insert(0, '/home/user/courtlistener')
django.setup()

from cl.search.models import Docket, Opinion, OpinionCluster, Court
from cl.recap.models import RECAPDocument
from cl.people_db.models import Party, PartyType
from django.db.models import Q, Count, Prefetch

# Major tech companies to search for as defendants
TECH_COMPANIES = [
    'Google', 'Alphabet', 'YouTube',
    'Apple', 'Amazon', 'Meta', 'Facebook', 'Instagram', 'WhatsApp',
    'Netflix', 'Spotify', 'Adobe', 'Salesforce',
    'Microsoft', 'Oracle', 'Twitter', 'X Corp',
    'TikTok', 'ByteDance', 'Hulu', 'Twitch',
    'Dropbox', 'Box.com', 'AWS',
]

# Software technology keywords
SOFTWARE_KEYWORDS = [
    'streaming', 'video', 'cloud', 'software', 'mobile', 'app', 'application',
    'SaaS', 'platform', 'web', 'online', 'internet', 'digital',
    'computer', 'network', 'server', 'database', 'API',
    'recommendation', 'personalization', 'algorithm',
    'analytics', 'visualization', 'dashboard',
    'social media', 'content platform',
]

# Target court IDs
TARGET_COURTS = ['cand', 'ded', 'txed', 'txwd', 'cacd']

def extract_fee_amount(text):
    """Extract attorney fee amounts from text."""
    if not text:
        return []

    # Patterns for fee amounts
    patterns = [
        r'\$\s*([0-9]{1,3}(?:,?[0-9]{3})*(?:\.[0-9]{2})?)\s*(?:in\s+)?(?:attorney|attorneys\'?|legal)\s+fees',
        r'(?:attorney|attorneys\'?|legal)\s+fees?\s+(?:in\s+the\s+amount\s+of\s+)?\$\s*([0-9]{1,3}(?:,?[0-9]{3})*(?:\.[0-9]{2})?)',
        r'(?:award|granted|grants?)\s+(?:plaintiff|defendant)\s+\$\s*([0-9]{1,3}(?:,?[0-9]{3})*(?:\.[0-9]{2})?)',
        r'fee\s+award\s+of\s+\$\s*([0-9]{1,3}(?:,?[0-9]{3})*(?:\.[0-9]{2})?)',
    ]

    amounts = []
    for pattern in patterns:
        matches = re.finditer(pattern, text, re.IGNORECASE)
        for match in matches:
            amount_str = match.group(1).replace(',', '')
            try:
                amount = float(amount_str)
                if 500000 <= amount <= 10000000:  # $500K to $10M range
                    amounts.append(amount)
            except ValueError:
                continue

    return amounts

def is_npe_plaintiff(party_name):
    """Heuristic to identify NPE/patent assertion entities."""
    if not party_name:
        return False

    party_lower = party_name.lower()

    # NPE indicators
    npe_keywords = [
        'technologies', 'innovations', 'licensing', 'ip', 'intellectual property',
        'patents', 'solutions', 'holdings', 'ventures',
    ]

    # Exclude actual operating companies
    exclude_keywords = [
        'microsoft', 'google', 'apple', 'amazon', 'facebook', 'meta',
        'oracle', 'ibm', 'samsung', 'sony', 'intel', 'qualcomm',
    ]

    if any(keyword in party_lower for keyword in exclude_keywords):
        return False

    if any(keyword in party_lower for keyword in npe_keywords):
        return True

    # Short names with LLC/Corp might be NPEs
    if ('llc' in party_lower or 'corp' in party_lower) and len(party_name) < 40:
        return True

    return False

def is_tech_defendant(party_name):
    """Check if party is a major tech company."""
    if not party_name:
        return False

    party_lower = party_name.lower()
    return any(company.lower() in party_lower for company in TECH_COMPANIES)

def contains_software_keywords(text):
    """Check if text contains software-related keywords."""
    if not text:
        return False

    text_lower = text.lower()
    return any(keyword in text_lower for keyword in SOFTWARE_KEYWORDS)

def main():
    print("=" * 80)
    print("SEARCHING FOR PATENT § 285 FEE AWARDS (2020-2025)")
    print("=" * 80)

    # Step 1: Find patent dockets in target courts and date range
    print("\n[1] Querying patent dockets in target courts (2020-2025)...")

    patent_dockets = Docket.objects.filter(
        court_id__in=TARGET_COURTS,
        nature_of_suit__in=['830', '835'],  # Patent cases
        date_filed__gte='2020-01-01',
        date_filed__lte='2025-12-31',
    ).select_related('court').prefetch_related(
        'parties',
        'docket_entries',
        'docket_entries__recap_documents',
    )

    print(f"   Found {patent_dockets.count()} patent dockets")

    # Step 2: Search for § 285 references in documents
    print("\n[2] Searching for § 285 attorney fee awards in documents...")

    results = []
    checked = 0

    for docket in patent_dockets[:500]:  # Limit for performance
        checked += 1
        if checked % 50 == 0:
            print(f"   Checked {checked} dockets, found {len(results)} matches so far...")

        # Check parties
        parties = docket.parties.all()
        plaintiff_names = [p.name for p in parties if 'plaintiff' in
                          PartyType.objects.filter(party=p, docket=docket).values_list('name', flat=True)]
        defendant_names = [p.name for p in parties if 'defendant' in
                          PartyType.objects.filter(party=p, docket=docket).values_list('name', flat=True)]

        # Check for NPE plaintiff and tech defendant
        has_npe_plaintiff = any(is_npe_plaintiff(name) for name in plaintiff_names)
        has_tech_defendant = any(is_tech_defendant(name) for name in defendant_names)

        if not (has_npe_plaintiff or has_tech_defendant):
            continue

        # Search documents for § 285
        for entry in docket.docket_entries.all():
            for doc in entry.recap_documents.all():
                if not doc.plain_text:
                    continue

                text = doc.plain_text

                # Look for § 285 references
                if not (
                    '§ 285' in text or '§285' in text or
                    '35 U.S.C. § 285' in text or '35 USC 285' in text or
                    'Section 285' in text
                ):
                    continue

                # Look for fee award language
                if not (
                    'attorney' in text.lower() and
                    ('fee' in text.lower() or 'fees' in text.lower()) and
                    ('grant' in text.lower() or 'award' in text.lower() or 'exceptional' in text.lower())
                ):
                    continue

                # Extract fee amounts
                fee_amounts = extract_fee_amount(text)
                if not fee_amounts:
                    continue

                # Check for software keywords
                if not contains_software_keywords(text):
                    continue

                # This looks like a match!
                results.append({
                    'docket': docket,
                    'document': doc,
                    'entry': entry,
                    'plaintiffs': plaintiff_names,
                    'defendants': defendant_names,
                    'fee_amounts': fee_amounts,
                    'text_snippet': text[:2000],
                })

                print(f"\n   ✓ MATCH: {docket.case_name} ({docket.court.id})")
                print(f"     Docket: {docket.docket_number}")
                print(f"     Fee amounts: {fee_amounts}")
                break  # Found a match in this docket

    # Step 3: Display results
    print("\n" + "=" * 80)
    print(f"RESULTS: Found {len(results)} cases matching criteria")
    print("=" * 80)

    for i, result in enumerate(results, 1):
        docket = result['docket']
        doc = result['document']

        print(f"\n[{i}] {docket.case_name}")
        print(f"    Docket: {docket.docket_number} ({docket.court.id})")
        print(f"    Filed: {docket.date_filed}")
        print(f"    Plaintiffs: {', '.join(result['plaintiffs'][:3])}")
        print(f"    Defendants: {', '.join(result['defendants'][:3])}")
        print(f"    Fee amounts found: ${', $'.join(str(int(amt)) for amt in result['fee_amounts'])}")
        print(f"    CourtListener: https://www.courtlistener.com{docket.get_absolute_url()}")
        print(f"    Document: {doc.description if doc.description else 'N/A'}")

    # Save detailed results to file
    output_file = '/home/user/courtlistener/patent_fee_results.txt'
    with open(output_file, 'w') as f:
        f.write("PATENT § 285 ATTORNEY FEE AWARDS (2020-2025)\n")
        f.write("=" * 80 + "\n\n")

        for i, result in enumerate(results, 1):
            docket = result['docket']
            doc = result['document']

            f.write(f"[{i}] {docket.case_name}\n")
            f.write(f"Docket: {docket.docket_number}\n")
            f.write(f"Court: {docket.court.full_name} ({docket.court.id})\n")
            f.write(f"Filed: {docket.date_filed}\n")
            f.write(f"Plaintiffs: {', '.join(result['plaintiffs'])}\n")
            f.write(f"Defendants: {', '.join(result['defendants'])}\n")
            f.write(f"Fee amounts: ${', $'.join(str(int(amt)) for amt in result['fee_amounts'])}\n")
            f.write(f"CourtListener: https://www.courtlistener.com{docket.get_absolute_url()}\n")
            f.write(f"\nDocument snippet:\n{result['text_snippet']}\n")
            f.write("\n" + "-" * 80 + "\n\n")

    print(f"\nDetailed results saved to: {output_file}")

if __name__ == '__main__':
    main()
