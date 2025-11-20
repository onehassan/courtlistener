#!/usr/bin/env python3
"""
Search CourtListener API for patent § 285 fee awards.
"""
import requests
import re
import json
from datetime import datetime
from time import sleep

API_BASE = "https://www.courtlistener.com/api/rest/v3"

# Major tech companies
TECH_COMPANIES = [
    'Google', 'Alphabet', 'YouTube',
    'Apple', 'Amazon', 'Meta', 'Facebook',
    'Netflix', 'Spotify', 'Adobe', 'Salesforce',
    'Microsoft', 'Oracle', 'Twitter', 'TikTok',
]

# Target courts
COURTS = {
    'cand': 'N.D. Cal.',
    'ded': 'D. Del.',
    'txed': 'E.D. Tex.',
    'txwd': 'W.D. Tex.',
    'cacd': 'C.D. Cal.',
}

def search_opinions(query, court=None, date_filed_after='2020-01-01'):
    """Search opinions via CourtListener API."""
    params = {
        'q': query,
        'type': 'o',  # Opinions
        'filed_after': date_filed_after,
        'order_by': 'score desc',
    }

    if court:
        params['court'] = court

    url = f"{API_BASE}/search/"
    print(f"  Searching: {query[:50]}... in {court or 'all courts'}")

    try:
        response = requests.get(url, params=params, timeout=30)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"  Error {response.status_code}: {response.text[:200]}")
            return None
    except Exception as e:
        print(f"  Exception: {e}")
        return None

def extract_fee_amounts(text):
    """Extract dollar amounts that might be attorney fees."""
    if not text:
        return []

    # Look for dollar amounts in reasonable range
    pattern = r'\$\s*([0-9]{1,3}(?:,?[0-9]{3})+(?:\.[0-9]{2})?)'
    matches = re.findall(pattern, text)

    amounts = []
    for match in matches:
        try:
            amount = float(match.replace(',', ''))
            if 500000 <= amount <= 10000000:
                amounts.append(amount)
        except:
            pass

    return list(set(amounts))

def search_by_company_and_statute(company, court_id):
    """Search for cases involving a company and § 285."""
    queries = [
        f'"{company}" AND ("35 U.S.C. § 285" OR "section 285" OR "exceptional case")',
        f'"{company}" AND "attorney fees" AND "patent" AND "exceptional"',
    ]

    results = []
    for query in queries:
        data = search_opinions(query, court=court_id, date_filed_after='2020-01-01')
        if data and 'results' in data:
            results.extend(data['results'])
        sleep(1)  # Rate limiting

    return results

def main():
    print("=" * 80)
    print("SEARCHING COURTLISTENER API FOR PATENT § 285 FEE AWARDS")
    print("=" * 80)

    all_results = {}

    # Search by tech company and court
    for court_id, court_name in COURTS.items():
        print(f"\n[{court_name}]")

        for company in TECH_COMPANIES[:5]:  # Limit for initial search
            print(f"\n  Searching for {company}...")
            results = search_by_company_and_statute(company, court_id)

            for result in results[:3]:  # Limit results per company
                case_name = result.get('caseName', 'Unknown')
                docket_number = result.get('docketNumber', 'N/A')
                date_filed = result.get('dateFiled', 'N/A')
                url = result.get('absolute_url', '')

                key = (case_name, docket_number)
                if key not in all_results:
                    all_results[key] = {
                        'case_name': case_name,
                        'docket_number': docket_number,
                        'court': court_name,
                        'date_filed': date_filed,
                        'url': f"https://www.courtlistener.com{url}" if url else 'N/A',
                        'snippet': result.get('snippet', ''),
                    }

            sleep(2)  # Rate limiting

    # Display results
    print("\n" + "=" * 80)
    print(f"FOUND {len(all_results)} UNIQUE CASES")
    print("=" * 80)

    with open('api_search_results.json', 'w') as f:
        json.dump(list(all_results.values()), f, indent=2)

    for i, (key, result) in enumerate(all_results.items(), 1):
        print(f"\n[{i}] {result['case_name']}")
        print(f"    Docket: {result['docket_number']}")
        print(f"    Court: {result['court']}")
        print(f"    Filed: {result['date_filed']}")
        print(f"    URL: {result['url']}")
        if result['snippet']:
            print(f"    Snippet: {result['snippet'][:150]}...")

    print(f"\n\nResults saved to: api_search_results.json")

if __name__ == '__main__':
    main()
