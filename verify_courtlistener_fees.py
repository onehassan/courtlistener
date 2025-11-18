#!/usr/bin/env python3
"""
CourtListener Attorney Fees Verification Script

This script searches CourtListener for cases containing attorney fee information
and verifies which ones have downloadable PDFs with actual fee data.
"""

import requests
import json
import time
from datetime import datetime, timedelta

# CourtListener API base URL
API_BASE = "https://www.courtlistener.com/api/rest/v4"
SEARCH_URL = f"{API_BASE}/search/"

# Search terms related to attorney fees
FEE_SEARCH_TERMS = [
    "attorney fees",
    "attorneys' fees",
    "fee petition",
    "bill of costs",
    "taxation of costs",
    "fee award",
    "hourly rate",
    "lodestar",
    "fee application",
    "motion for attorney fees"
]

def search_courtlistener(query, result_type="r", date_filed_after=None, limit=20):
    """
    Search CourtListener for cases matching the query

    Args:
        query: Search query string
        result_type: Type of search (r=opinions, rd=dockets, etc.)
        date_filed_after: Filter for cases filed after this date (YYYY-MM-DD)
        limit: Maximum number of results to return

    Returns:
        List of results
    """
    params = {
        "q": query,
        "type": result_type,
        "order_by": "dateFiled desc",
        "stat_Precedential": "on",
    }

    if date_filed_after:
        params["filed_after"] = date_filed_after

    try:
        response = requests.get(SEARCH_URL, params=params, timeout=30)
        response.raise_for_status()

        data = response.json()
        results = data.get("results", [])

        print(f"Found {data.get('count', 0)} total results for: {query}")
        return results[:limit]

    except requests.exceptions.RequestException as e:
        print(f"Error searching CourtListener: {e}")
        return []

def check_docket_for_fee_docs(docket_id):
    """
    Check if a docket has entries with fee-related documents

    Args:
        docket_id: CourtListener docket ID

    Returns:
        List of docket entries with fee-related documents
    """
    docket_url = f"{API_BASE}/dockets/{docket_id}/"

    try:
        response = requests.get(docket_url, timeout=30)
        response.raise_for_status()

        docket_data = response.json()

        # Check docket entries for fee-related documents
        fee_entries = []
        entries = docket_data.get("docket_entries", [])

        for entry in entries:
            description = entry.get("description", "").lower()

            # Check if entry description contains fee-related keywords
            fee_keywords = ["fee", "cost", "bill", "taxation", "lodestar", "petition"]
            if any(keyword in description for keyword in fee_keywords):

                # Check if entry has attachments
                recap_documents = entry.get("recap_documents", [])
                if recap_documents:
                    for doc in recap_documents:
                        if doc.get("is_available"):
                            fee_entries.append({
                                "entry_number": entry.get("entry_number"),
                                "date_filed": entry.get("date_filed"),
                                "description": entry.get("description"),
                                "document_number": doc.get("document_number"),
                                "document_url": doc.get("filepath_local"),
                                "pacer_doc_id": doc.get("pacer_doc_id"),
                                "is_available": doc.get("is_available")
                            })

        return fee_entries

    except requests.exceptions.RequestException as e:
        print(f"Error checking docket {docket_id}: {e}")
        return []

def search_and_verify_fee_cases(search_term, days_back=365, max_results=10):
    """
    Search for cases with attorney fee information and verify PDF availability

    Args:
        search_term: Search query
        days_back: Number of days to look back
        max_results: Maximum number of results to process

    Returns:
        List of verified cases with fee documents
    """
    # Calculate date range
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days_back)
    date_filed_after = start_date.strftime("%Y-%m-%d")

    print(f"\n{'='*80}")
    print(f"Searching for: {search_term}")
    print(f"Date range: {date_filed_after} to present")
    print(f"{'='*80}\n")

    # Search for opinions
    opinion_results = search_courtlistener(
        query=search_term,
        result_type="o",
        date_filed_after=date_filed_after,
        limit=max_results
    )

    verified_cases = []

    for result in opinion_results:
        case_name = result.get("caseName", "Unknown Case")
        court = result.get("court", "Unknown Court")
        date_filed = result.get("dateFiled", "Unknown Date")
        absolute_url = result.get("absolute_url", "")

        # Extract relevant fee information from the opinion text
        snippet = result.get("snippet", "")

        print(f"\nCase: {case_name}")
        print(f"Court: {court}")
        print(f"Date Filed: {date_filed}")
        print(f"URL: https://www.courtlistener.com{absolute_url}")
        print(f"Snippet: {snippet[:200]}...")

        # Check if there's a docket associated with this opinion
        docket_id = result.get("docket_id")
        if docket_id:
            print(f"Checking docket {docket_id} for fee documents...")
            fee_docs = check_docket_for_fee_docs(docket_id)

            if fee_docs:
                print(f"✓ Found {len(fee_docs)} fee-related document(s) with PDFs")
                verified_cases.append({
                    "case_name": case_name,
                    "court": court,
                    "date_filed": date_filed,
                    "url": f"https://www.courtlistener.com{absolute_url}",
                    "docket_id": docket_id,
                    "fee_documents": fee_docs
                })

                for doc in fee_docs[:3]:  # Show first 3 documents
                    print(f"  - Entry #{doc['entry_number']}: {doc['description'][:80]}")
            else:
                print("✗ No downloadable fee documents found")

        time.sleep(0.5)  # Be polite to the API

    return verified_cases

def generate_verification_report(verified_cases, output_file="courtlistener_fee_cases_verified.json"):
    """
    Generate a report of verified cases with fee documents

    Args:
        verified_cases: List of verified cases
        output_file: Output file path
    """
    report = {
        "generated_at": datetime.now().isoformat(),
        "total_verified_cases": len(verified_cases),
        "cases": verified_cases
    }

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    print(f"\n{'='*80}")
    print(f"Report saved to: {output_file}")
    print(f"Total verified cases with fee documents: {len(verified_cases)}")
    print(f"{'='*80}\n")

def main():
    """Main execution function"""

    print("""
╔═══════════════════════════════════════════════════════════════════════════════╗
║              CourtListener Attorney Fees Verification Tool                    ║
║                                                                               ║
║  This tool searches CourtListener for cases with attorney fee information    ║
║  and verifies which ones have downloadable PDFs with actual fee data.        ║
╚═══════════════════════════════════════════════════════════════════════════════╝
    """)

    all_verified_cases = []

    # Search for multiple fee-related terms
    search_terms = [
        '"attorney fees" AND "hourly rate"',
        '"fee petition" AND (awarded OR granted)',
        '"bill of costs"',
        '"lodestar" AND "attorney fees"',
        '"fee award" AND ($ OR dollar)'
    ]

    for term in search_terms[:2]:  # Limit to first 2 terms for quick results
        verified = search_and_verify_fee_cases(
            search_term=term,
            days_back=730,  # Last 2 years
            max_results=5
        )
        all_verified_cases.extend(verified)
        time.sleep(1)  # Pause between searches

    # Generate report
    if all_verified_cases:
        generate_verification_report(all_verified_cases)

        # Print summary
        print("\n📊 SUMMARY OF VERIFIED CASES WITH FEE DATA PDFs")
        print("=" * 80)
        for i, case in enumerate(all_verified_cases, 1):
            print(f"\n{i}. {case['case_name']}")
            print(f"   Court: {case['court']}")
            print(f"   Date: {case['date_filed']}")
            print(f"   URL: {case['url']}")
            print(f"   Fee Documents: {len(case['fee_documents'])}")
    else:
        print("\n⚠ No verified cases with downloadable fee documents found.")
        print("This may be due to:")
        print("  - API rate limiting")
        print("  - Search parameters too restrictive")
        print("  - Recent cases not yet having fee petitions filed")
        print("\nTry adjusting the search parameters or date range.")

if __name__ == "__main__":
    main()
