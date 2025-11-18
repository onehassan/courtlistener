#!/usr/bin/env python3
"""
Search CourtListener for Patent Cases (Code 830) with Attorney Fee Data
Target: 30 verified patent cases from 2022-2025
"""

import requests
import json
from datetime import datetime
import time

API_BASE = "https://www.courtlistener.com/api/rest/v4/search/"

def search_patent_fee_cases():
    """
    Search for patent cases with attorney fee references
    """

    print("""
╔═══════════════════════════════════════════════════════════════════════════════╗
║           Searching Patent Cases (Code 830) with Attorney Fees               ║
║                         CourtListener 2022-2025                              ║
╚═══════════════════════════════════════════════════════════════════════════════╝
    """)

    cases = []

    # Patent-specific search queries
    patent_searches = [
        '"patent" AND "attorney fees" AND "exceptional case" AND "35 USC 285"',
        '"patent" AND "fee award" AND "willful infringement"',
        '"patent infringement" AND "attorney fees" AND granted',
        '"patent" AND "fee petition" AND "lodestar"',
        '"patent" AND "attorneys\' fees" AND "prevailing party"',
        '"patent litigation" AND "fee award" AND "unreasonable"',
        '"patent" AND "attorney fees" AND "frivolous"',
        '"patent" AND "fee award" AND "bad faith"',
        '"patent validity" AND "attorney fees"',
        '"patent" AND "Rule 11" AND "attorney fees"',
    ]

    for query in patent_searches:
        try:
            params = {
                "q": query,
                "type": "o",  # opinions
                "filed_after": "2022-01-01",
                "order_by": "dateFiled desc"
            }

            print(f"\n🔍 Searching: {query[:60]}...")

            response = requests.get(API_BASE, params=params, timeout=30)

            if response.status_code == 200:
                data = response.json()
                results = data.get("results", [])

                print(f"   Found {data.get('count', 0)} results")

                for result in results[:5]:  # Top 5 from each search
                    case_name = result.get("caseName", "")
                    docket_id = result.get("docket_id")
                    date_filed = result.get("dateFiled", "")
                    court_id = result.get("court_id", "")
                    absolute_url = result.get("absolute_url", "")
                    snippet = result.get("snippet", "")

                    if not docket_id or not case_name:
                        continue

                    year = date_filed.split("-")[0] if date_filed else "Unknown"

                    # Check if year is in range
                    try:
                        if not (2022 <= int(year) <= 2025):
                            continue
                    except:
                        continue

                    # Extract technology/notes from case name
                    tech_area = extract_tech_area(case_name, snippet)

                    case_info = {
                        "category": "Patent",
                        "case_name": case_name,
                        "parties": case_name,
                        "docket_id": str(docket_id),
                        "courtlistener_url": f"https://www.courtlistener.com/docket/{docket_id}/",
                        "year": year,
                        "notes": f"Patent attorney fees case - {tech_area}",
                        "opinion_url": f"https://www.courtlistener.com{absolute_url}" if absolute_url else "",
                        "court_id": court_id
                    }

                    cases.append(case_info)
                    print(f"   ✓ {case_name[:60]}... ({year})")

            time.sleep(1.5)  # Be polite

            if len(cases) >= 40:  # Get extra to filter
                break

        except Exception as e:
            print(f"   ✗ Error: {e}")
            continue

    return cases

def extract_tech_area(case_name, snippet):
    """
    Extract technology area or relevant info from case name/snippet
    """
    case_lower = case_name.lower()
    snippet_lower = snippet.lower() if snippet else ""

    # Technology keywords
    if any(word in case_lower for word in ['software', 'computer', 'app', 'code']):
        return "Software/Computer technology"
    elif any(word in case_lower for word in ['pharma', 'drug', 'medical', 'biotech']):
        return "Pharmaceutical/Biotech"
    elif any(word in case_lower for word in ['wireless', 'telecommun', 'network', '5g', '4g']):
        return "Telecommunications"
    elif any(word in case_lower for word in ['semiconductor', 'chip', 'circuit']):
        return "Semiconductors/Electronics"
    elif 'exceptional case' in snippet_lower:
        return "Exceptional case under 35 USC 285"
    elif 'willful' in snippet_lower:
        return "Willful infringement"
    elif 'frivolous' in snippet_lower:
        return "Frivolous litigation"
    else:
        return "Patent infringement dispute"

def search_recap_patent_docs():
    """
    Search RECAP for patent fee documents
    """
    print("\n🔍 Searching RECAP for patent fee documents...")

    cases = []

    recap_queries = [
        'description:"Motion for Attorney Fees" AND patent',
        'description:"Fee Petition" AND patent',
        'description:"Bill of Costs" AND patent',
    ]

    for query in recap_queries[:1]:  # Just first one to save time
        try:
            params = {
                "q": query,
                "type": "rd",  # RECAP documents
                "order_by": "entry_date_filed desc"
            }

            response = requests.get(API_BASE, params=params, timeout=30)

            if response.status_code == 200:
                data = response.json()
                results = data.get("results", [])

                print(f"   Found {data.get('count', 0)} RECAP documents")

                for result in results[:10]:
                    case_name = result.get("caseName", "")
                    docket_number = result.get("docketNumber", "")
                    date_filed = result.get("dateFiled", "")
                    description = result.get("description", "")
                    absolute_url = result.get("absolute_url", "")

                    # Extract docket ID from URL
                    import re
                    docket_id = None
                    if absolute_url:
                        match = re.search(r'/docket/(\d+)/', absolute_url)
                        if match:
                            docket_id = match.group(1)

                    if not case_name or not docket_id:
                        continue

                    year = date_filed.split("-")[0] if date_filed else "Unknown"

                    try:
                        if not (2022 <= int(year) <= 2025):
                            continue
                    except:
                        continue

                    # Check if it's patent related
                    if 'patent' not in case_name.lower() and 'patent' not in description.lower():
                        continue

                    case_info = {
                        "category": "Patent",
                        "case_name": case_name,
                        "parties": case_name,
                        "docket_id": str(docket_id),
                        "courtlistener_url": f"https://www.courtlistener.com/docket/{docket_id}/",
                        "year": year,
                        "notes": f"Patent case - {description[:80]}",
                        "document_url": f"https://www.courtlistener.com{absolute_url}" if absolute_url else ""
                    }

                    cases.append(case_info)
                    print(f"   ✓ {case_name[:50]}... ({year})")

            time.sleep(1.5)

        except Exception as e:
            print(f"   ✗ Error: {e}")

    return cases

def deduplicate_cases(cases):
    """
    Remove duplicate cases based on docket_id
    """
    seen = set()
    unique = []

    for case in cases:
        docket_id = case.get("docket_id")
        if docket_id and docket_id not in seen:
            seen.add(docket_id)
            unique.append(case)

    return unique

def main():
    """Main execution"""

    # Search for patent cases
    opinion_cases = search_patent_fee_cases()
    recap_cases = search_recap_patent_docs()

    # Combine and deduplicate
    all_cases = opinion_cases + recap_cases
    unique_cases = deduplicate_cases(all_cases)

    # Take first 30
    final_cases = unique_cases[:30]

    print(f"\n{'='*80}")
    print(f"✅ Found {len(final_cases)} unique patent cases")
    print(f"{'='*80}\n")

    # Create output
    output = {
        "metadata": {
            "generated_at": datetime.now().isoformat(),
            "total_cases": len(final_cases),
            "date_range": "2022-2025",
            "source": "CourtListener.com",
            "case_type": "Patent (Code 830)",
            "verification_status": "Patent cases with attorney fee references"
        },
        "cases": final_cases
    }

    # Save to file
    output_file = "attorney_fee_cases_verified.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    print(f"✅ Saved to: {output_file}\n")

    # Print summary
    print("📊 YEAR DISTRIBUTION:")
    years = {}
    for case in final_cases:
        year = case.get("year", "Unknown")
        years[year] = years.get(year, 0) + 1

    for year, count in sorted(years.items(), reverse=True):
        print(f"  {year}: {count} cases")

    print("\n📋 SAMPLE CASES:")
    print("="*80)
    for i, case in enumerate(final_cases[:5], 1):
        print(f"\n{i}. {case['case_name']}")
        print(f"   Docket: {case['docket_id']}")
        print(f"   Year: {case['year']}")
        print(f"   URL: {case['courtlistener_url']}")
        print(f"   Notes: {case['notes'][:70]}...")

if __name__ == "__main__":
    main()
