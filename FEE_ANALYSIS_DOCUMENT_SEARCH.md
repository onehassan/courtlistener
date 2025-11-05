# Searching RECAP Documents for Fee Analysis and Market Comparisons

## Overview

This guide shows how to search CourtListener's RECAP documents for specific content related to:
- Attorney fees and billing rates
- Market rate comparisons
- Court fee analysis
- Geographic rate context
- Expert witness fees
- Damages calculations

## Understanding RECAP Document Search

### Search Types

CourtListener offers three search types for RECAP content:

| Type | Parameter | What It Searches | Returns |
|------|-----------|------------------|---------|
| **RECAP** | `type=r` | Dockets + Documents combined | Both parent dockets and child documents |
| **RECAP Documents** | `type=rd` | Individual documents only | Document-level results |
| **Dockets** | `type=d` | Docket metadata only | Docket records with limited child docs |

**For fee analysis, use `type=r` or `type=rd`** to search document text content.

### Searchable Fields

When you search RECAP documents, the query searches across:

1. **`plain_text`** - Full extracted text from PDF documents (primary search field)
2. **`short_description`** - Brief description of the document (e.g., "Motion for Attorney Fees")
3. **`description`** - Docket entry description
4. **OCR text** - Text extracted via OCR is included in `plain_text`

---

## Quick Start: Search for Fee Analysis Documents

### Basic Fee Search

Search for documents discussing attorney fees and rates:

```bash
curl -X GET \
  "https://www.courtlistener.com/api/rest/v4/search/?type=r&q=attorney+fees+hourly+rate+market&available_only=true&page_size=50" \
  -H "Authorization: Token YOUR_API_TOKEN"
```

### Key Query Components

```bash
type=r                    # Search RECAP documents
q=attorney+fees           # Search term (searches full text)
available_only=true       # Only documents with downloadable PDFs
page_size=50              # Results per page (max 100)
order_by=dateFiled desc   # Sort by filing date
```

---

## Specific Search Queries

### 1. Attorney Fee Awards with Market Analysis

Search for documents that discuss attorney fees with market rate comparisons:

```bash
curl -X GET \
  "https://www.courtlistener.com/api/rest/v4/search/?type=r&q=(attorney+fees+OR+legal+fees)+AND+(market+rate+OR+prevailing+rate+OR+reasonable+rate)&available_only=true" \
  -H "Authorization: Token YOUR_API_TOKEN"
```

**What this finds:**
- Fee petitions with market rate analysis
- Court orders analyzing reasonable fees
- Expert declarations on prevailing rates

---

### 2. Geographic Rate Context

Search for documents discussing fees with geographic/jurisdictional context:

```bash
curl -X GET \
  "https://www.courtlistener.com/api/rest/v4/search/?type=r&q=hourly+rate+AND+(district+OR+jurisdiction+OR+geographic+OR+locality+OR+forum)&available_only=true" \
  -H "Authorization: Token YOUR_API_TOKEN"
```

**What this finds:**
- Fee orders comparing rates across districts
- Declarations discussing local market rates
- Geographic wage surveys

---

### 3. Court Analysis of Fee Reasonableness

Search for court opinions analyzing fee reasonableness:

```bash
curl -X GET \
  "https://www.courtlistener.com/api/rest/v4/search/?type=r&q=(lodestar+OR+reasonable+fees+OR+fee+analysis)+AND+(court+finds+OR+court+concludes)&available_only=true" \
  -H "Authorization: Token YOUR_API_TOKEN"
```

**What this finds:**
- Court orders with detailed fee analysis
- Lodestar calculations
- Reasonableness determinations

---

### 4. Market Rate Surveys and Comparisons

Search for documents with market surveys or rate comparisons:

```bash
curl -X GET \
  "https://www.courtlistener.com/api/rest/v4/search/?type=r&q=(market+survey+OR+rate+comparison+OR+billing+rate+survey+OR+NALP)+AND+hourly&available_only=true" \
  -H "Authorization: Token YOUR_API_TOKEN"
```

**What this finds:**
- Expert reports citing rate surveys
- NALP (National Association for Law Placement) data
- Billing rate comparisons

---

### 5. Expert Witness Fee Analysis

Search for expert witness fee discussions:

```bash
curl -X GET \
  "https://www.courtlistener.com/api/rest/v4/search/?type=r&q=(expert+fees+OR+expert+witness)+AND+(hourly+rate+OR+market+rate)&available_only=true" \
  -H "Authorization: Token YOUR_API_TOKEN"
```

---

### 6. Fee Petitions and Motions

Search by document description for fee-related filings:

```bash
curl -X GET \
  "https://www.courtlistener.com/api/rest/v4/search/?type=r&description=attorney+fees&q=market+rate+OR+prevailing+rate&available_only=true" \
  -H "Authorization: Token YOUR_API_TOKEN"
```

**What this finds:**
- Motions for attorney fees
- Fee petitions
- Opposition to fee requests

---

## Advanced Search Techniques

### Using Boolean Operators

CourtListener supports Elasticsearch query syntax:

```bash
# AND operator (all terms must be present)
q=attorney+fees+AND+market+rate

# OR operator (any term can be present)
q=(attorney+fees+OR+legal+fees)

# NOT operator (exclude terms)
q=attorney+fees+NOT+sanctions

# Phrase search (exact phrase)
q="prevailing market rate"

# Proximity search (terms within N words)
q="attorney fees"~10  # "attorney" and "fees" within 10 words

# Wildcard search
q=fee*  # Matches: fees, fee-shifting, etc.
```

### Combining Multiple Criteria

**Example: Patent cases with detailed fee analysis**

```bash
curl -X GET \
  "https://www.courtlistener.com/api/rest/v4/search/?type=r&nature_of_suit=830&q=(attorney+fees+OR+costs)+AND+(market+rate+OR+lodestar)+AND+(district+OR+jurisdiction)&filed_after=2020-01-01&available_only=true&page_size=50" \
  -H "Authorization: Token YOUR_API_TOKEN"
```

This searches for:
- ✅ Patent cases (`nature_of_suit=830`)
- ✅ Documents mentioning attorney fees/costs
- ✅ With market rate or lodestar analysis
- ✅ Including geographic/jurisdictional context
- ✅ Filed since 2020
- ✅ With available PDFs

---

## Common Fee Analysis Search Terms

### Fee-Related Terms

```
attorney fees
legal fees
hourly rate
billing rate
fee petition
fee award
lodestar
reasonable fees
prevailing party
fee-shifting
costs and fees
```

### Market Analysis Terms

```
market rate
prevailing rate
reasonable rate
customary rate
comparable rate
market survey
rate comparison
billing rate survey
industry standard
geographic market
```

### Court Analysis Terms

```
court finds
court concludes
reasonableness analysis
lodestar calculation
multiplier
enhancement
reduction
fee analysis
proportionality
```

### Geographic/Context Terms

```
district
jurisdiction
locality
forum
geographic area
local market
regional rate
community
venue
```

---

## Filtering by Document Type

### Filter by Document Description

Many fee-related documents have specific descriptions:

```bash
# Motions for attorney fees
description=motion+attorney+fees

# Fee petitions
description=petition+fees

# Opposition to fees
description=opposition+fees

# Court orders on fees
description=order+fees

# Expert declarations
description=declaration+expert
```

### Example: Only Fee Motions with Market Analysis

```bash
curl -X GET \
  "https://www.courtlistener.com/api/rest/v4/search/?type=r&description=motion+attorney+fees&q=market+rate+AND+(survey+OR+comparison)&available_only=true" \
  -H "Authorization: Token YOUR_API_TOKEN"
```

---

## Python Script: Comprehensive Fee Document Search

```python
import requests
import json
import csv
from datetime import datetime

API_TOKEN = "YOUR_API_TOKEN"
BASE_URL = "https://www.courtlistener.com/api/rest/v4"

headers = {"Authorization": f"Token {API_TOKEN}"}

def search_fee_documents(query_params, max_results=100):
    """
    Search for RECAP documents matching fee analysis criteria.

    Args:
        query_params: Dictionary of search parameters
        max_results: Maximum number of results to retrieve

    Returns:
        List of matching documents
    """
    query_params['type'] = 'r'  # RECAP search
    query_params['available_only'] = 'true'  # Only docs with PDFs
    query_params['page_size'] = 50

    all_results = []
    cursor = None

    while len(all_results) < max_results:
        if cursor:
            query_params['cursor'] = cursor

        response = requests.get(
            f"{BASE_URL}/search/",
            headers=headers,
            params=query_params
        )

        if response.status_code != 200:
            print(f"Error: {response.status_code}")
            print(response.text)
            break

        data = response.json()
        results = data.get('results', [])

        if not results:
            break

        all_results.extend(results)
        print(f"Retrieved {len(all_results)} documents...")

        # Check if there's a next page
        cursor = data.get('next')
        if not cursor:
            break

    return all_results[:max_results]


def extract_document_info(doc):
    """Extract relevant information from search result."""
    return {
        'docket_id': doc.get('docket_id'),
        'case_name': doc.get('caseName', 'N/A'),
        'docket_number': doc.get('docketNumber', 'N/A'),
        'court': doc.get('court', 'N/A'),
        'date_filed': doc.get('dateFiled', 'N/A'),
        'nature_of_suit': doc.get('suitNature', 'N/A'),
        'document_number': doc.get('document_number', 'N/A'),
        'description': doc.get('short_description', 'N/A'),
        'snippet': doc.get('snippet', 'N/A'),
        'pdf_url': doc.get('filepath_local', 'N/A'),
    }


# Example 1: Search for attorney fee orders with market analysis
print("=" * 80)
print("SEARCH 1: Attorney Fee Orders with Market Rate Analysis")
print("=" * 80)

query1 = {
    'q': '(attorney fees OR legal fees) AND (market rate OR prevailing rate)',
    'description': 'order',
    'filed_after': '2020-01-01',
}

results1 = search_fee_documents(query1, max_results=50)
print(f"\nFound {len(results1)} documents")

# Print first 5 results
for i, doc in enumerate(results1[:5], 1):
    info = extract_document_info(doc)
    print(f"\n{i}. {info['case_name']}")
    print(f"   Docket: {info['docket_number']} ({info['court']})")
    print(f"   Filed: {info['date_filed']}")
    print(f"   Doc #{info['document_number']}: {info['description']}")
    if info['snippet'] != 'N/A':
        print(f"   Snippet: {info['snippet'][:200]}...")


# Example 2: Patent cases with detailed fee analysis
print("\n" + "=" * 80)
print("SEARCH 2: Patent Cases with Fee Analysis and Geographic Context")
print("=" * 80)

query2 = {
    'nature_of_suit': '830',
    'q': 'attorney fees AND (lodestar OR market rate) AND (district OR jurisdiction)',
    'filed_after': '2021-01-01',
}

results2 = search_fee_documents(query2, max_results=50)
print(f"\nFound {len(results2)} documents")


# Example 3: Fee petitions with billing rate surveys
print("\n" + "=" * 80)
print("SEARCH 3: Fee Petitions with Billing Rate Surveys")
print("=" * 80)

query3 = {
    'description': 'motion attorney fees',
    'q': '(billing rate OR hourly rate) AND (survey OR comparison OR NALP)',
    'filed_after': '2020-01-01',
}

results3 = search_fee_documents(query3, max_results=50)
print(f"\nFound {len(results3)} documents")


# Example 4: Expert fee analysis
print("\n" + "=" * 80)
print("SEARCH 4: Expert Witness Fee Analysis")
print("=" * 80)

query4 = {
    'q': '(expert fees OR expert witness) AND (hourly rate OR market rate) AND declaration',
    'filed_after': '2020-01-01',
}

results4 = search_fee_documents(query4, max_results=50)
print(f"\nFound {len(results4)} documents")


# Export results to CSV
def export_to_csv(results, filename):
    """Export search results to CSV file."""
    if not results:
        print(f"No results to export to {filename}")
        return

    with open(filename, 'w', newline='', encoding='utf-8') as f:
        fieldnames = ['docket_id', 'case_name', 'docket_number', 'court',
                     'date_filed', 'nature_of_suit', 'document_number',
                     'description', 'snippet', 'pdf_url']
        writer = csv.DictWriter(f, fieldnames=fieldnames)

        writer.writeheader()
        for doc in results:
            writer.writerow(extract_document_info(doc))

    print(f"\n✅ Exported {len(results)} results to {filename}")


# Export all searches
export_to_csv(results1, 'fee_orders_with_market_analysis.csv')
export_to_csv(results2, 'patent_fee_analysis_geographic.csv')
export_to_csv(results3, 'fee_petitions_with_surveys.csv')
export_to_csv(results4, 'expert_fee_analysis.csv')


# Summary statistics
print("\n" + "=" * 80)
print("SUMMARY")
print("=" * 80)
print(f"Search 1 (Fee Orders with Market Analysis): {len(results1)} documents")
print(f"Search 2 (Patent Fees with Geographic Context): {len(results2)} documents")
print(f"Search 3 (Fee Petitions with Surveys): {len(results3)} documents")
print(f"Search 4 (Expert Fee Analysis): {len(results4)} documents")
print(f"\nTotal documents found: {len(results1) + len(results2) + len(results3) + len(results4)}")
```

---

## Expected Document Types

When searching for fee analysis, you'll typically find:

### 1. **Fee Petitions/Motions**
- Filed by prevailing party
- Include billing records
- Expert declarations on rates
- Market rate analysis

### 2. **Court Orders on Fees**
- Lodestar calculations
- Reasonableness analysis
- Rate reductions/enhancements
- Geographic market analysis

### 3. **Opposition Briefs**
- Challenge to rates claimed
- Alternative market data
- Critiques of expert analysis

### 4. **Expert Declarations**
- Billing rate surveys
- Geographic market analysis
- Industry standards
- Comparative rate studies

### 5. **Reply Briefs**
- Response to opposition
- Additional market support
- Supplemental rate data

---

## Response Format

Search results include document metadata and text snippets:

```json
{
  "count": "https://www.courtlistener.com/api/rest/v4/search/?...",
  "next": "https://www.courtlistener.com/api/rest/v4/search/?cursor=...",
  "previous": null,
  "results": [
    {
      "docket_id": 123456,
      "caseName": "Apple Inc. v. Samsung Electronics Co.",
      "docketNumber": "5:11-cv-01846",
      "court": "Northern District of California",
      "court_id": "cand",
      "dateFiled": "2023-05-15",
      "suitNature": "830 Patent",
      "document_number": 542,
      "short_description": "Order Granting in Part Motion for Attorney Fees",
      "snippet": "The Court finds that the prevailing market rate for attorneys with similar experience in this district ranges from $500 to $800 per hour. Based on the lodestar calculation...",
      "filepath_local": "https://storage.courtlistener.com/...",
      "plain_text": "...full document text...",
      "is_available": true
    }
  ]
}
```

---

## Rate Limiting

**Remember the API rate limits:**
- Anonymous: 100 requests/day
- Authenticated: 5,000 requests/hour

For large searches, implement proper pagination and delay between requests.

---

## Tips for Effective Searches

### 1. **Use Specific Terms**
❌ Too broad: `q=fees`
✅ Better: `q=attorney fees AND market rate`
✅ Best: `q=(attorney fees OR legal fees) AND (market rate OR prevailing rate) AND (district OR jurisdiction)`

### 2. **Combine with Case Type Filters**
```bash
nature_of_suit=830  # Patent cases
nature_of_suit=840  # Trademark
nature_of_suit=442  # Employment discrimination
```

### 3. **Date Range for Recent Data**
```bash
filed_after=2020-01-01    # Cases filed after date
filed_before=2024-12-31   # Cases filed before date
```

### 4. **Filter by Court**
```bash
court=cand  # Northern District of California
court=ded   # District of Delaware
court=txed  # Eastern District of Texas
```

### 5. **Sort by Relevance or Date**
```bash
order_by=score desc      # Most relevant first
order_by=dateFiled desc  # Most recent first
```

---

## Common Search Patterns

### Pattern 1: Find Benchmark Fee Orders

Search for comprehensive fee orders that courts cite as benchmarks:

```bash
curl -X GET \
  "https://www.courtlistener.com/api/rest/v4/search/?type=r&q=attorney+fees+AND+lodestar+AND+(prevailing+rate+OR+market+rate)+AND+(experience+OR+expertise)&description=order&filed_after=2020-01-01&available_only=true&order_by=score+desc" \
  -H "Authorization: Token YOUR_API_TOKEN"
```

### Pattern 2: Geographic Rate Survey

Find documents with rate information for specific district:

```bash
curl -X GET \
  "https://www.courtlistener.com/api/rest/v4/search/?type=r&court=cand&q=hourly+rate+AND+(survey+OR+market+OR+prevailing)&filed_after=2020-01-01&available_only=true" \
  -H "Authorization: Token YOUR_API_TOKEN"
```

### Pattern 3: Expert Rate Analysis

Find expert declarations with detailed rate analysis:

```bash
curl -X GET \
  "https://www.courtlistener.com/api/rest/v4/search/?type=r&description=declaration+expert&q=(billing+rate+OR+hourly+rate)+AND+(survey+OR+market+comparison+OR+NALP)&available_only=true" \
  -H "Authorization: Token YOUR_API_TOKEN"
```

---

## Download Documents

Once you find relevant documents, download the PDFs:

### Method 1: Direct URL from Search Results

```python
import requests

pdf_url = result['filepath_local']
response = requests.get(pdf_url)

with open('document.pdf', 'wb') as f:
    f.write(response.content)
```

### Method 2: Via RECAP Document API

```python
recap_id = result['id']  # RECAP document ID from search

# Get document details
doc_response = requests.get(
    f"{BASE_URL}/recap-documents/{recap_id}/",
    headers=headers
)

doc_data = doc_response.json()
pdf_url = doc_data['filepath_local']

# Download PDF
pdf_response = requests.get(pdf_url)
with open(f'recap_{recap_id}.pdf', 'wb') as f:
    f.write(pdf_response.content)
```

---

## Key Search Combinations for Fee Analysis

| Goal | Search Query |
|------|--------------|
| **Market Rate Analysis** | `q=(attorney fees OR legal fees) AND (market rate OR prevailing rate)` |
| **Geographic Context** | `q=hourly rate AND (district OR jurisdiction OR geographic OR locality)` |
| **Court Analysis** | `q=(lodestar OR reasonable fees) AND (court finds OR court concludes)` |
| **Rate Surveys** | `q=(billing rate OR hourly rate) AND (survey OR comparison OR NALP)` |
| **Expert Analysis** | `q=(expert fees OR expert witness) AND (hourly rate OR market rate)` |
| **Patent Fee Awards** | `nature_of_suit=830&q=attorney fees AND (market rate OR lodestar)` |
| **Employment Cases** | `nature_of_suit=442&q=attorney fees AND prevailing rate` |

---

## Source Code References

- RECAP Document Model: `/home/user/courtlistener/cl/search/models.py:3281` (plain_text field)
- Search Documents (ES): `/home/user/courtlistener/cl/search/documents.py:1235-1246`
- Search Form: `/home/user/courtlistener/cl/search/forms.py:128-204`
- API Query Utils: `/home/user/courtlistener/cl/search/api_utils.py:83-84`

---

## Additional Resources

- **API Documentation**: https://www.courtlistener.com/help/api/rest/
- **Search Syntax**: Uses Elasticsearch query string syntax
- **Field Reference**: See DJANGO_REST_API_DOCUMENTATION.md
- **Rate Limits**: See API documentation for current limits

---

**Last Updated:** 2025-11-05
**API Version:** V4

---

## Quick Reference: Complete Search Examples

### 1. Comprehensive Fee Analysis Search
```bash
https://www.courtlistener.com/api/rest/v4/search/?type=r&q=(attorney+fees+OR+legal+fees)+AND+(market+rate+OR+prevailing+rate)+AND+(district+OR+jurisdiction)&available_only=true&filed_after=2020-01-01
```

### 2. Patent Cases Only
```bash
https://www.courtlistener.com/api/rest/v4/search/?type=r&nature_of_suit=830&q=attorney+fees+AND+market+rate&available_only=true
```

### 3. Specific District (Northern California)
```bash
https://www.courtlistener.com/api/rest/v4/search/?type=r&court=cand&q=hourly+rate+AND+market&available_only=true
```

### 4. Expert Declarations with Rate Surveys
```bash
https://www.courtlistener.com/api/rest/v4/search/?type=r&description=declaration+expert&q=billing+rate+AND+survey&available_only=true
```
