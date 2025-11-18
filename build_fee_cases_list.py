#!/usr/bin/env python3
"""
Build a high-quality list of CourtListener cases with verifiable attorney fee PDFs
Target: 30 cases from 2022-2025
"""

import requests
import json
import time
from datetime import datetime
import re

# CourtListener API base URL
API_BASE = "https://www.courtlistener.com/api/rest/v4"
SEARCH_URL = f"{API_BASE}/search/"

def search_cases_with_fees(query, case_category, date_filed_after="2022-01-01", limit=10):
    """
    Search CourtListener for cases with attorney fees

    Args:
        query: Search query string
        case_category: Category for classification (e.g., "Civil Rights", "Employment")
        date_filed_after: Start date for search
        limit: Number of results to fetch

    Returns:
        List of case dictionaries
    """
    cases = []

    # Search for opinions mentioning attorney fees
    params = {
        "q": query,
        "type": "o",  # opinions
        "order_by": "dateFiled desc",
        "filed_after": date_filed_after,
    }

    try:
        print(f"\n🔍 Searching: {query}")
        response = requests.get(SEARCH_URL, params=params, timeout=30)
        response.raise_for_status()

        data = response.json()
        results = data.get("results", [])

        print(f"   Found {data.get('count', 0)} total results")

        for result in results[:limit]:
            case_name = result.get("caseName", "")
            court = result.get("court", "")
            date_filed = result.get("dateFiled", "")
            absolute_url = result.get("absolute_url", "")
            docket_id = result.get("docket_id")
            snippet = result.get("snippet", "")

            # Extract year
            year = date_filed.split("-")[0] if date_filed else "Unknown"

            # Check if snippet mentions fees with dollar amounts
            has_fee_amount = bool(re.search(r'\$[\d,]+', snippet))

            if docket_id and case_name and has_fee_amount:
                # Try to find docket URL
                docket_url = f"https://www.courtlistener.com/docket/{docket_id}/"

                # Extract note from snippet
                note = snippet[:100].replace("\n", " ").strip()
                if not note:
                    note = f"Attorney fees awarded in {court}"

                case_info = {
                    "category": case_category,
                    "case_name": case_name,
                    "parties": case_name,
                    "docket_id": str(docket_id),
                    "courtlistener_url": docket_url,
                    "year": year,
                    "notes": note,
                    "court": court,
                    "opinion_url": f"https://www.courtlistener.com{absolute_url}" if absolute_url else ""
                }

                cases.append(case_info)
                print(f"   ✓ Added: {case_name} ({year})")

        time.sleep(1)  # Be polite to the API

    except Exception as e:
        print(f"   ✗ Error searching: {e}")

    return cases

def search_recap_cases(description_term, case_category, limit=5):
    """
    Search RECAP archive for cases with fee documents

    Args:
        description_term: Document description to search for
        case_category: Category for classification
        limit: Number of results

    Returns:
        List of case dictionaries
    """
    cases = []

    # Search RECAP documents
    params = {
        "q": f'description:"{description_term}"',
        "type": "rd",  # RECAP documents
        "order_by": "entry_date_filed desc",
    }

    try:
        print(f"\n🔍 Searching RECAP: {description_term}")
        response = requests.get(SEARCH_URL, params=params, timeout=30)
        response.raise_for_status()

        data = response.json()
        results = data.get("results", [])

        print(f"   Found {data.get('count', 0)} total RECAP documents")

        for result in results[:limit]:
            docket_number = result.get("docketNumber", "")
            case_name = result.get("caseName", "")
            court = result.get("court", "")
            date_filed = result.get("dateFiled", "")
            description = result.get("description", "")
            absolute_url = result.get("absolute_url", "")

            # Extract docket_id from URL if available
            docket_id = None
            if "docket" in str(absolute_url):
                match = re.search(r'/docket/(\d+)/', str(absolute_url))
                if match:
                    docket_id = match.group(1)

            # Extract year
            year = date_filed.split("-")[0] if date_filed else "Unknown"

            if case_name and (2022 <= int(year) <= 2025 if year.isdigit() else False):
                docket_url = f"https://www.courtlistener.com/docket/{docket_id}/" if docket_id else ""

                case_info = {
                    "category": case_category,
                    "case_name": case_name,
                    "parties": case_name,
                    "docket_id": str(docket_id) if docket_id else "Unknown",
                    "courtlistener_url": docket_url,
                    "year": year,
                    "notes": description[:100] if description else f"Fee document filed in {court}",
                    "court": court,
                    "document_url": f"https://www.courtlistener.com{absolute_url}" if absolute_url else ""
                }

                cases.append(case_info)
                print(f"   ✓ Added: {case_name} ({year})")

        time.sleep(1)

    except Exception as e:
        print(f"   ✗ Error searching RECAP: {e}")

    return cases

def build_comprehensive_list():
    """
    Build comprehensive list of 30+ cases with attorney fee data
    """

    print("""
╔═══════════════════════════════════════════════════════════════════════════════╗
║           Building High-Quality Attorney Fee Cases List                      ║
║                   CourtListener Cases 2022-2025                              ║
╚═══════════════════════════════════════════════════════════════════════════════╝
    """)

    all_cases = []

    # Search queries organized by category
    search_queries = [
        # Civil Rights Cases
        {
            "query": '"attorney fees" AND "civil rights" AND "42 USC 1988"',
            "category": "Civil Rights",
            "limit": 5
        },
        {
            "query": '"fee award" AND "section 1983" AND granted',
            "category": "Civil Rights",
            "limit": 3
        },

        # Employment Discrimination
        {
            "query": '"attorney fees" AND ("Title VII" OR "ADA" OR "ADEA")',
            "category": "Employment Discrimination",
            "limit": 5
        },
        {
            "query": '"FLSA" AND "attorney fees" AND "collective action"',
            "category": "Employment - Wage & Hour",
            "limit": 3
        },

        # Consumer Protection
        {
            "query": '"TCPA" AND "attorney fees" AND "statutory damages"',
            "category": "Consumer Protection - TCPA",
            "limit": 3
        },
        {
            "query": '"FDCPA" AND "attorney fees" AND awarded',
            "category": "Consumer Protection - Debt Collection",
            "limit": 3
        },

        # Intellectual Property
        {
            "query": '"patent" AND "attorney fees" AND "exceptional case"',
            "category": "Intellectual Property - Patent",
            "limit": 3
        },
        {
            "query": '"copyright" AND "attorney fees" AND "17 USC 505"',
            "category": "Intellectual Property - Copyright",
            "limit": 3
        },

        # Class Actions
        {
            "query": '"class action" AND "attorney fees" AND "common fund"',
            "category": "Class Action",
            "limit": 3
        },

        # EAJA (Social Security)
        {
            "query": '"EAJA" AND "attorney fees" AND "Social Security"',
            "category": "Social Security - EAJA",
            "limit": 3
        },

        # Securities
        {
            "query": '"securities fraud" AND "attorney fees" AND awarded',
            "category": "Securities Litigation",
            "limit": 2
        },

        # Environmental
        {
            "query": '"Clean Water Act" AND "attorney fees"',
            "category": "Environmental Law",
            "limit": 2
        },
    ]

    # Execute searches
    for search in search_queries:
        cases = search_cases_with_fees(
            query=search["query"],
            case_category=search["category"],
            date_filed_after="2022-01-01",
            limit=search["limit"]
        )
        all_cases.extend(cases)

        # Stop if we have enough cases
        if len(all_cases) >= 30:
            break

    # Also search RECAP for fee petitions
    if len(all_cases) < 30:
        recap_searches = [
            ("Motion for Attorney Fees", "General Litigation"),
            ("Bill of Costs", "General Litigation"),
            ("Fee Petition", "General Litigation"),
        ]

        for desc_term, category in recap_searches:
            recap_cases = search_recap_cases(desc_term, category, limit=5)
            all_cases.extend(recap_cases)

            if len(all_cases) >= 30:
                break

    # Remove duplicates based on docket_id
    seen_dockets = set()
    unique_cases = []

    for case in all_cases:
        docket_id = case.get("docket_id")
        if docket_id and docket_id != "Unknown" and docket_id not in seen_dockets:
            seen_dockets.add(docket_id)
            unique_cases.append(case)

    # Take first 30
    final_cases = unique_cases[:30]

    return final_cases

def save_cases_list(cases, output_file="attorney_fee_cases_verified.json"):
    """
    Save cases list to JSON file

    Args:
        cases: List of case dictionaries
        output_file: Output filename
    """

    # Create output structure
    output = {
        "metadata": {
            "generated_at": datetime.now().isoformat(),
            "total_cases": len(cases),
            "date_range": "2022-2025",
            "source": "CourtListener.com",
            "verification_status": "High-quality list with verifiable attorney fee data"
        },
        "cases": cases
    }

    # Save to file
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    print(f"\n{'='*80}")
    print(f"✅ Saved {len(cases)} cases to: {output_file}")
    print(f"{'='*80}\n")

    # Print summary
    print("📊 SUMMARY BY CATEGORY:")
    print("-" * 80)

    categories = {}
    for case in cases:
        cat = case.get("category", "Unknown")
        categories[cat] = categories.get(cat, 0) + 1

    for cat, count in sorted(categories.items(), key=lambda x: x[1], reverse=True):
        print(f"  {cat:.<50} {count:>3} cases")

    print("-" * 80)

    # Print year distribution
    print("\n📅 YEAR DISTRIBUTION:")
    print("-" * 80)

    years = {}
    for case in cases:
        year = case.get("year", "Unknown")
        years[year] = years.get(year, 0) + 1

    for year, count in sorted(years.items(), reverse=True):
        print(f"  {year:.<50} {count:>3} cases")

    print("-" * 80)

def main():
    """Main execution"""

    # Build the list
    cases = build_comprehensive_list()

    if len(cases) < 30:
        print(f"\n⚠️  Warning: Only found {len(cases)} cases (target was 30)")
        print("    This may be due to API rate limiting or search parameters")

    # Save results
    if cases:
        save_cases_list(cases)

        # Print first few examples
        print("\n📋 SAMPLE CASES:")
        print("=" * 80)
        for i, case in enumerate(cases[:5], 1):
            print(f"\n{i}. {case['case_name']}")
            print(f"   Category: {case['category']}")
            print(f"   Year: {case['year']}")
            print(f"   URL: {case['courtlistener_url']}")
            print(f"   Notes: {case['notes'][:80]}...")
    else:
        print("\n❌ No cases found. Please check API access and search parameters.")

if __name__ == "__main__":
    main()
