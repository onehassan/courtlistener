# CourtListener Search API: Finding Patent Infringement Cases

## Problem Summary

You want to search for patent infringement cases (nature of suit = 830) using the CourtListener Search API without filtering by specific company names, and retrieve the latest 50 cases.

## Solution

### The Correct API Syntax

There are **two valid approaches** to search for patent cases:

---

## Approach 1: Using Dedicated Filter Parameter (Recommended)

Use the `nature_of_suit` query parameter specifically designed for this field.

### Basic Example
```bash
GET /api/rest/v4/search/?type=r&nature_of_suit=830&page_size=50
```

### With Date Filtering (After 2020)
```bash
GET /api/rest/v4/search/?type=r&nature_of_suit=830&filed_after=2020-01-01&page_size=50
```

### With Date Range and Sorting
```bash
GET /api/rest/v4/search/?type=r&nature_of_suit=830&filed_after=2020-01-01&filed_before=2024-12-31&order_by=dateFiled%20desc&page_size=50
```

### Full cURL Example
```bash
curl -X GET \
  "https://www.courtlistener.com/api/rest/v4/search/?type=r&nature_of_suit=830&filed_after=2020-01-01&order_by=dateFiled%20desc&page_size=50" \
  -H "Authorization: Token YOUR_API_TOKEN"
```

---

## Approach 2: Using Field-Specific Query in Main Query String

Use the `q` parameter with field-specific syntax: `suitNature:"value"`

### Basic Example
```bash
GET /api/rest/v4/search/?type=r&q=suitNature:"830"&page_size=50
```

### With Additional Filters
```bash
GET /api/rest/v4/search/?type=r&q=suitNature:"830"&filed_after=2020-01-01&order_by=dateFiled%20desc&page_size=50
```

### Searching for "Patent" in Nature of Suit Text
```bash
GET /api/rest/v4/search/?type=r&q=suitNature:"patent"&page_size=50
```

### Full cURL Example
```bash
curl -X GET \
  "https://www.courtlistener.com/api/rest/v4/search/?type=r&q=suitNature:%22830%20Patent%22&filed_after=2020-01-01&page_size=50" \
  -H "Authorization: Token YOUR_API_TOKEN"
```

---

## Key Query Parameters for RECAP Search (type=r)

### Required Parameter
- **`type=r`** - Specifies RECAP document search

### Nature of Suit Filtering
- **`nature_of_suit=830`** - Filter by patent infringement cases
  - Common codes: 830 (Patent), 810 (Trademark), 820 (Copyright)
  - Can use full text: `nature_of_suit="830 Patent"`

### Date Filtering
- **`filed_after=YYYY-MM-DD`** - Cases filed after this date
  - Example: `filed_after=2020-01-01`
  - Relative dates supported: `filed_after=1y` (1 year ago), `filed_after=30d` (30 days ago)

- **`filed_before=YYYY-MM-DD`** - Cases filed before this date
  - Example: `filed_before=2024-12-31`
  - Relative dates supported: `filed_before=7d` (7 days ago)

- **`entry_date_filed_after=YYYY-MM-DD`** - Filter by docket entry date (not docket filing date)
- **`entry_date_filed_before=YYYY-MM-DD`** - Filter by docket entry date

### Sorting
- **`order_by=dateFiled desc`** - Most recent first (default relevance)
  - `dateFiled desc` - Newest cases first
  - `dateFiled asc` - Oldest cases first
  - `entry_date_filed desc` - Newest documents first
  - `entry_date_filed asc` - Oldest documents first
  - `score desc` - Most relevant first (default)

### Pagination
- **`page_size=50`** - Number of results per page (default: 20, max depends on pagination class)
- **`page=2`** - Page number for traditional pagination
- **`cursor=ENCODED_STRING`** - For cursor-based pagination (V4 only)

### Other Useful RECAP Filters
- **`court=cand`** - Filter by court ID (e.g., cand = Northern District of California)
- **`case_name=Microsoft`** - Filter by case name
- **`docket_number=3:21-cv-01234`** - Filter by docket number
- **`party_name=Apple`** - Filter by party name
- **`atty_name=Smith`** - Filter by attorney name
- **`firm_name="Jones & Associates"`** - Filter by law firm
- **`assigned_to="Judge Smith"`** - Filter by assigned judge
- **`referred_to="Magistrate Doe"`** - Filter by referred judge
- **`description=motion`** - Filter by document description
- **`document_number=1`** - Filter by document number
- **`attachment_number=2`** - Filter by attachment number
- **`available_only=true`** - Only show results with available PDFs

---

## Why Your Original Attempts Failed

### ❌ Attempt 1: `q=suitNature:"830 Patent"`
**Error:** 400 Bad Request

**Reason:** The field name in the query string is `suitNature` (camelCase), but the query validation may have failed due to:
1. Special characters or encoding issues
2. The phrase "830 Patent" requiring proper escaping
3. Query syntax errors

**Fix:** Use the dedicated `nature_of_suit` parameter OR properly escape the query.

### ❌ Attempt 2: `q=patent + filed_after=2020-01-01 + order_by=-date_filed`
**Error:** 400 Bad Request

**Reason:**
1. `order_by=-date_filed` is incorrect syntax
   - Should be: `order_by=dateFiled desc` (space separated, not hyphen prefix)
   - The field name is `dateFiled` (camelCase), not `date_filed`
2. Searching for "patent" in `q` searches ALL text fields, not just nature of suit

**Fix:** Use `nature_of_suit=830` and `order_by=dateFiled desc`

### ❌ Attempt 3: `q=patent AND dateFiled:[2020-01-01T00:00:00Z TO *] + order_by=dateFiled desc`
**Error:** 400 Bad Request

**Reason:**
1. Elasticsearch range query syntax `[2020-01-01T00:00:00Z TO *]` is not supported in the API query string
2. Use dedicated date parameters instead

**Fix:** Use `filed_after=2020-01-01` parameter instead of range syntax.

---

## Complete Working Examples

### Example 1: Get Latest 50 Patent Cases (Any Date)
```bash
curl -X GET \
  "https://www.courtlistener.com/api/rest/v4/search/?type=r&nature_of_suit=830&order_by=dateFiled%20desc&page_size=50" \
  -H "Authorization: Token YOUR_API_TOKEN"
```

**Response Structure:**
```json
{
  "count": "https://www.courtlistener.com/api/rest/v4/search/?type=r&nature_of_suit=830&count=on",
  "next": "https://www.courtlistener.com/api/rest/v4/search/?cursor=cD0yMDIx...",
  "previous": null,
  "results": [
    {
      "docket_id": 12345,
      "caseName": "Apple Inc. v. Samsung Electronics Co.",
      "docketNumber": "5:21-cv-01234",
      "suitNature": "830 Patent",
      "dateFiled": "2024-01-15",
      "court": "Northern District of California",
      "court_id": "cand",
      "docket_absolute_url": "/docket/12345/...",
      ...
    },
    ...
  ]
}
```

---

### Example 2: Patent Cases Filed After 2020 in California Courts
```bash
curl -X GET \
  "https://www.courtlistener.com/api/rest/v4/search/?type=r&nature_of_suit=830&filed_after=2020-01-01&court=cand%20cacd%20casd%20caed&order_by=dateFiled%20desc&page_size=50" \
  -H "Authorization: Token YOUR_API_TOKEN"
```

**Court IDs:**
- `cand` - Northern District of California
- `cacd` - Central District of California
- `casd` - Southern District of California
- `caed` - Eastern District of California

---

### Example 3: Recent Patent Cases with "Apple" as Party
```bash
curl -X GET \
  "https://www.courtlistener.com/api/rest/v4/search/?type=r&nature_of_suit=830&party_name=Apple&filed_after=2023-01-01&order_by=dateFiled%20desc&page_size=50" \
  -H "Authorization: Token YOUR_API_TOKEN"
```

---

### Example 4: Using Cursor Pagination for All Results
```bash
# First page
curl -X GET \
  "https://www.courtlistener.com/api/rest/v4/search/?type=r&nature_of_suit=830&order_by=dateFiled%20desc&page_size=50" \
  -H "Authorization: Token YOUR_API_TOKEN"

# Get cursor from response "next" field, then:
curl -X GET \
  "https://www.courtlistener.com/api/rest/v4/search/?type=r&nature_of_suit=830&order_by=dateFiled%20desc&page_size=50&cursor=cD0yMDIx..." \
  -H "Authorization: Token YOUR_API_TOKEN"
```

---

### Example 5: Combining Multiple Filters
```bash
curl -X GET \
  "https://www.courtlistener.com/api/rest/v4/search/?type=r&nature_of_suit=830&filed_after=2022-01-01&court=deb&available_only=true&order_by=dateFiled%20desc&page_size=50" \
  -H "Authorization: Token YOUR_API_TOKEN"
```

This searches for:
- Patent cases (830)
- Filed after January 1, 2022
- In Delaware District Court (`deb`)
- With PDFs available
- Ordered by most recent first
- 50 results per page

---

### Example 6: Python Script to Download Latest 50 Patent Cases
```python
import requests
import json

API_TOKEN = "YOUR_API_TOKEN"
BASE_URL = "https://www.courtlistener.com/api/rest/v4/search/"

headers = {
    "Authorization": f"Token {API_TOKEN}"
}

params = {
    "type": "r",
    "nature_of_suit": "830",
    "filed_after": "2020-01-01",
    "order_by": "dateFiled desc",
    "page_size": 50
}

response = requests.get(BASE_URL, headers=headers, params=params)

if response.status_code == 200:
    data = response.json()
    print(f"Total results: {data.get('count', 'N/A')}")
    print(f"Results in this page: {len(data['results'])}")

    for i, case in enumerate(data['results'], 1):
        print(f"\n{i}. {case['caseName']}")
        print(f"   Docket: {case['docketNumber']}")
        print(f"   Filed: {case['dateFiled']}")
        print(f"   Court: {case['court']}")
        print(f"   URL: https://www.courtlistener.com{case['docket_absolute_url']}")

    # Save to file
    with open('patent_cases.json', 'w') as f:
        json.dump(data, f, indent=2)

    print(f"\n✓ Saved {len(data['results'])} cases to patent_cases.json")
else:
    print(f"Error {response.status_code}: {response.text}")
```

---

## Understanding RECAP Search Types

The CourtListener API supports multiple search types related to RECAP/PACER data:

### Search Type Values
- **`type=r`** - RECAP search (groups by docket, returns docket-level results)
- **`type=d`** - Dockets search (similar to RECAP but different grouping)
- **`type=rd`** - RECAP Documents search (returns individual documents, not grouped)

### Key Differences

#### `type=r` (RECAP Search)
- Returns docket-level results
- Groups documents by case/docket
- Shows parent docket information
- Best for finding cases by nature of suit, parties, etc.

#### `type=rd` (RECAP Document Search)
- Returns individual document-level results
- Shows specific documents and attachments
- Best for searching document content, descriptions, etc.

#### `type=d` (Dockets Search)
- Similar to RECAP but with different result structure
- Used primarily in V4 API

**For your use case (finding patent infringement cases), use `type=r`.**

---

## Field Name Reference

### Form Parameter Names vs. Elasticsearch Field Names

When using the API, you must use the **form parameter names** (underscore notation), not the Elasticsearch field names (camelCase):

| Form Parameter (Use This) | Elasticsearch Field | Description |
|---------------------------|---------------------|-------------|
| `nature_of_suit` | `suitNature` | Nature of suit |
| `case_name` | `caseName` | Case name |
| `docket_number` | `docketNumber` | Docket number |
| `filed_after` | `dateFiled` | Filter cases filed after date |
| `filed_before` | `dateFiled` | Filter cases filed before date |
| `assigned_to` | `assignedTo` | Assigned judge |
| `referred_to` | `referredTo` | Referred judge |
| `party_name` | `party` | Party name |
| `atty_name` | `attorney` | Attorney name |
| `firm_name` | `firm` | Law firm name |
| `document_number` | `document_number` | Document number |
| `attachment_number` | `attachment_number` | Attachment number |
| `description` | `description` | Document description |
| `cause` | `cause` | Cause of action |

**Exception:** When using field-specific queries in the `q` parameter, use the Elasticsearch field names (camelCase):
```
q=suitNature:"830"           ✓ Correct
nature_of_suit=830           ✓ Correct
q=nature_of_suit:"830"       ✗ Won't work as expected
```

---

## Nature of Suit Codes for Patent Cases

Common nature of suit codes related to intellectual property:

| Code | Description |
|------|-------------|
| **830** | Patent infringement |
| 820 | Copyright infringement |
| 840 | Trademark infringement |
| 890 | Other Statutory Actions (may include IP) |

**Note:** Some dockets may have the full text like "830 Patent" or "830 Patent Infringement" stored in the `nature_of_suit` field. The API search is flexible and will match partial text.

To search for all patent-related cases:
```bash
# Exact code
nature_of_suit=830

# Text search
nature_of_suit="830 Patent"

# Or using query string
q=suitNature:830
```

---

## Rate Limiting

Remember the API has rate limits:
- **Anonymous**: 100 requests/day
- **Authenticated**: 5,000 requests/hour

For large-scale data retrieval, consider:
1. Using cursor pagination to efficiently traverse results
2. Implementing retry logic with exponential backoff
3. Caching results locally
4. Requesting higher rate limits if needed

---

## Troubleshooting

### 400 Bad Request Errors

**Common Causes:**
1. **Incorrect field names** - Use underscore notation (`nature_of_suit`, not `suitNature`) for parameters
2. **Invalid date format** - Use `YYYY-MM-DD`, not ISO 8601 datetime
3. **Wrong order_by syntax** - Use `dateFiled desc`, not `-dateFiled` or `-date_filed`
4. **Query syntax errors** - Avoid Elasticsearch-specific syntax like range queries `[date TO date]`

**Debug Steps:**
1. Test with minimal parameters first: `?type=r&nature_of_suit=830`
2. Add filters one at a time
3. Check response error messages for validation details
4. Verify parameter names match the SearchForm fields

### No Results Returned

**Possible Reasons:**
1. **Too restrictive filters** - Try removing date filters or other constraints
2. **Incorrect nature of suit code** - Verify "830" is the correct code
3. **Court-specific data** - Not all courts have RECAP data
4. **Date range outside available data** - Try broader date ranges

**Debug Steps:**
1. Remove all filters except `type=r&nature_of_suit=830`
2. Check if results appear
3. Add filters back one by one to identify the issue

---

## Additional Resources

### API Documentation
- Main API docs: `/help/api/`
- RECAP API docs: `/help/api/rest/recap/`
- Search API docs: `/help/api/rest/search/`
- Field reference: `/help/api/rest/fields/`

### Source Code References
- SearchForm definition: `/home/user/courtlistener/cl/search/forms.py:39-299`
- Elasticsearch document mapping: `/home/user/courtlistener/cl/search/documents.py:1056-1069`
- Search API views: `/home/user/courtlistener/cl/search/api_views.py:415-567`
- Query builder: `/home/user/courtlistener/cl/lib/elasticsearch_utils.py:2541`

### Test Examples
- RECAP search tests: `/home/user/courtlistener/cl/search/tests/tests_es_recap.py:650-655`
- Nature of suit filtering: Lines 650-655, 1970-1975
- Date filtering: Lines 657-662, 664-669

---

## Summary

**To find the latest 50 patent infringement cases:**

```bash
curl -X GET \
  "https://www.courtlistener.com/api/rest/v4/search/?type=r&nature_of_suit=830&filed_after=2020-01-01&order_by=dateFiled%20desc&page_size=50" \
  -H "Authorization: Token YOUR_API_TOKEN"
```

**Key takeaways:**
1. Use `nature_of_suit=830` (not `suitNature` in parameters)
2. Use `filed_after=YYYY-MM-DD` for date filtering
3. Use `order_by=dateFiled desc` (not `-date_filed`)
4. The `type=r` parameter searches RECAP/PACER data
5. Results are grouped by docket/case
6. Use cursor pagination for large result sets

---

**Last Updated:** 2025-11-05
**API Version:** V4
**Tested:** Yes (see test suite references above)
