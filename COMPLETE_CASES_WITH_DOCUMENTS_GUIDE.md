# Finding Complete Patent Cases with Downloadable Documents

## Overview

You can filter patent cases to find those that are:
1. **Complete/Terminated** - Cases that have been fully resolved
2. **Have Downloadable Documents** - Cases with available PDF documents

---

## Quick Answer

### Get Complete Patent Cases with Documents (Search API)

```bash
curl -X GET \
  "https://www.courtlistener.com/api/rest/v4/search/?type=r&nature_of_suit=830&available_only=true&filed_after=2020-01-01&order_by=dateFiled%20desc&page_size=50" \
  -H "Authorization: Token YOUR_API_TOKEN"
```

### Get Terminated Patent Cases with Documents (Docket Endpoint)

```bash
curl -X GET \
  "https://www.courtlistener.com/api/rest/v4/dockets/?nature_of_suit=830&date_terminated__isnull=false&count=on" \
  -H "Authorization: Token YOUR_API_TOKEN"
```

---

## Understanding Completeness Indicators

### 1. Case Termination Status

**Field:** `date_terminated` / `dateTerminated`

A case is considered "complete" when it has a termination date. This typically means:
- Final judgment has been entered
- Case has been dismissed
- Case has been settled and closed
- Appeal period has expired

**Filter Options:**

| Filter | Description | Example |
|--------|-------------|---------|
| `date_terminated__isnull=false` | Has termination date (completed) | All terminated cases |
| `date_terminated__isnull=true` | No termination date (ongoing) | Active cases |
| `date_terminated__gte=2020-01-01` | Terminated after specific date | Recently closed |
| `date_terminated__lte=2024-12-31` | Terminated before specific date | Closed by date |

---

### 2. Document Availability

**Field:** `is_available` (RECAP documents) / `available_only` (Search parameter)

Documents are marked as available when:
- PDF file has been uploaded to RECAP
- File is stored and accessible
- Document is not sealed or restricted

**Search API Parameter:**
- `available_only=true` - Only return results with available PDF documents

**CRUD API Filter:**
- `is_available=true` - Filter RECAP documents that are available

---

## Methods to Find Complete Patent Cases with Documents

### Method 1: Search API with `available_only` (Recommended)

**Best for:** Finding cases with searchable documents

```bash
curl -X GET \
  "https://www.courtlistener.com/api/rest/v4/search/?type=r&nature_of_suit=830&available_only=true&page_size=50" \
  -H "Authorization: Token YOUR_API_TOKEN"
```

**Parameters:**
- `type=r` - RECAP search
- `nature_of_suit=830` - Patent cases
- `available_only=true` - Only cases with PDF documents
- `page_size=50` - Return 50 results

**Characteristics:**
- ✅ Fast full-text search
- ✅ Filters for document availability
- ✅ Grouped by docket
- ⚠️ Doesn't directly filter by termination status

---

### Method 2: Docket Endpoint with Terminated Cases

**Best for:** Finding terminated cases with exact counts

```bash
curl -X GET \
  "https://www.courtlistener.com/api/rest/v4/dockets/?nature_of_suit=830&date_terminated__isnull=false&order_by=-date_terminated&page_size=50" \
  -H "Authorization: Token YOUR_API_TOKEN"
```

**Parameters:**
- `nature_of_suit=830` - Patent cases
- `date_terminated__isnull=false` - Only terminated cases
- `order_by=-date_terminated` - Most recently terminated first

**Characteristics:**
- ✅ Exact database filtering
- ✅ Direct access to termination data
- ❌ Doesn't filter by document availability directly
- ❌ Need to check documents separately

---

### Method 3: RECAP Documents Endpoint

**Best for:** Finding specific documents that are available

```bash
curl -X GET \
  "https://www.courtlistener.com/api/rest/v4/recap-documents/?docket__nature_of_suit=830&is_available=true&page_size=50" \
  -H "Authorization: Token YOUR_API_TOKEN"
```

**Parameters:**
- `docket__nature_of_suit=830` - Patent cases (relationship filter)
- `is_available=true` - Only available documents
- `page_size=50` - Return 50 results

**Characteristics:**
- ✅ Document-level filtering
- ✅ Direct access to availability status
- ✅ Can filter by document type, page count, etc.
- ⚠️ Returns documents, not dockets

---

### Method 4: Combined Approach (Most Complete)

**Best for:** Finding terminated patent cases and checking document availability

**Step 1: Find terminated patent cases**
```bash
curl -X GET \
  "https://www.courtlistener.com/api/rest/v4/dockets/?nature_of_suit=830&date_terminated__isnull=false&date_terminated__gte=2020-01-01&order_by=-date_terminated&page_size=50" \
  -H "Authorization: Token YOUR_API_TOKEN"
```

**Step 2: For each docket, check document availability**
```bash
curl -X GET \
  "https://www.courtlistener.com/api/rest/v4/recap-documents/?docket={docket_id}&is_available=true" \
  -H "Authorization: Token YOUR_API_TOKEN"
```

---

## Detailed Filter Combinations

### Terminated Patent Cases with Recent Termination

```bash
# Terminated in last year
curl "https://www.courtlistener.com/api/rest/v4/dockets/?nature_of_suit=830&date_terminated__gte=2024-01-01&order_by=-date_terminated"

# Terminated in 2023
curl "https://www.courtlistener.com/api/rest/v4/dockets/?nature_of_suit=830&date_terminated__gte=2023-01-01&date_terminated__lte=2023-12-31"
```

### Patent Cases with Available Documents in Specific Court

```bash
# Delaware District Court (popular patent venue)
curl "https://www.courtlistener.com/api/rest/v4/search/?type=r&nature_of_suit=830&court=ded&available_only=true"

# Northern District of California
curl "https://www.courtlistener.com/api/rest/v4/search/?type=r&nature_of_suit=830&court=cand&available_only=true"
```

### Terminated Patent Cases by Date Range

```bash
# Filed after 2020 and terminated
curl "https://www.courtlistener.com/api/rest/v4/dockets/?nature_of_suit=830&date_filed__gte=2020-01-01&date_terminated__isnull=false"

# Filed and terminated in same year (quick cases)
curl "https://www.courtlistener.com/api/rest/v4/dockets/?nature_of_suit=830&date_filed__gte=2023-01-01&date_terminated__lte=2023-12-31"
```

---

## Counting Complete Patent Cases

### Count All Terminated Patent Cases

```bash
curl -X GET \
  "https://www.courtlistener.com/api/rest/v4/dockets/?nature_of_suit=830&date_terminated__isnull=false&count=on" \
  -H "Authorization: Token YOUR_API_TOKEN"
```

**Response:**
```json
{
  "count": 123456
}
```

### Count Patent Cases Terminated in Last Year

```bash
curl -X GET \
  "https://www.courtlistener.com/api/rest/v4/dockets/?nature_of_suit=830&date_terminated__gte=2024-01-01&count=on" \
  -H "Authorization: Token YOUR_API_TOKEN"
```

### Count Available RECAP Documents for Patent Cases

```bash
curl -X GET \
  "https://www.courtlistener.com/api/rest/v4/recap-documents/?docket__nature_of_suit=830&is_available=true&count=on" \
  -H "Authorization: Token YOUR_API_TOKEN"
```

---

## Understanding Document Types

Not all documents in a case may be available. Common document types include:

| Document Type | Description | Likely Availability |
|---------------|-------------|---------------------|
| Complaint | Initial filing | High |
| Answer | Defendant's response | High |
| Motion | Various motions | Medium-High |
| Order | Court orders | High |
| Judgment | Final judgment | Very High |
| Brief | Legal briefs | Medium |
| Exhibit | Evidence/attachments | Low-Medium |
| Minute Entry | Court notes | Low |

**To filter by document type:**

```bash
# Search for judgments in patent cases
curl "https://www.courtlistener.com/api/rest/v4/recap-documents/?docket__nature_of_suit=830&is_available=true&description__icontains=judgment"

# Search for orders
curl "https://www.courtlistener.com/api/rest/v4/recap-documents/?docket__nature_of_suit=830&is_available=true&description__icontains=order"
```

---

## Python Example: Find Complete Patent Cases with Documents

```python
import requests

API_TOKEN = "YOUR_API_TOKEN"
BASE_URL = "https://www.courtlistener.com/api/rest/v4"
headers = {"Authorization": f"Token {API_TOKEN}"}

def get_complete_patent_cases(min_date="2020-01-01", limit=50):
    """
    Find terminated patent cases with available documents

    Args:
        min_date: Minimum termination date
        limit: Maximum number of cases to return

    Returns:
        List of docket IDs and metadata
    """

    # Step 1: Get terminated patent cases
    params = {
        "nature_of_suit": "830",
        "date_terminated__isnull": "false",
        "date_terminated__gte": min_date,
        "order_by": "-date_terminated",
        "page_size": limit
    }

    response = requests.get(
        f"{BASE_URL}/dockets/",
        headers=headers,
        params=params
    )

    if response.status_code != 200:
        print(f"Error: {response.status_code}")
        return []

    dockets = response.json()['results']
    print(f"Found {len(dockets)} terminated patent cases")

    # Step 2: Check document availability for each case
    complete_cases = []

    for docket in dockets:
        docket_id = docket['id']

        # Check if this docket has available documents
        doc_params = {
            "docket": docket_id,
            "is_available": "true",
            "count": "on"
        }

        doc_response = requests.get(
            f"{BASE_URL}/recap-documents/",
            headers=headers,
            params=doc_params
        )

        if doc_response.status_code == 200:
            doc_count = doc_response.json()['count']

            if doc_count > 0:
                complete_cases.append({
                    'docket_id': docket_id,
                    'case_name': docket['case_name'],
                    'docket_number': docket['docket_number'],
                    'court': docket['court'],
                    'date_filed': docket['date_filed'],
                    'date_terminated': docket['date_terminated'],
                    'available_documents': doc_count,
                    'resource_uri': docket['resource_uri']
                })

    return complete_cases

# Run the function
cases = get_complete_patent_cases(min_date="2023-01-01", limit=20)

print(f"\n{len(cases)} complete patent cases with documents:\n")
for i, case in enumerate(cases, 1):
    print(f"{i}. {case['case_name']}")
    print(f"   Docket: {case['docket_number']}")
    print(f"   Court: {case['court']}")
    print(f"   Filed: {case['date_filed']}")
    print(f"   Terminated: {case['date_terminated']}")
    print(f"   Available Documents: {case['available_documents']}")
    print(f"   URL: https://www.courtlistener.com{case['resource_uri']}")
    print()
```

**Output Example:**
```
Found 20 terminated patent cases

15 complete patent cases with documents:

1. Apple Inc. v. Samsung Electronics Co.
   Docket: 5:11-cv-01846
   Court: Northern District of California
   Filed: 2011-04-15
   Terminated: 2023-08-30
   Available Documents: 2341
   URL: https://www.courtlistener.com/api/rest/v4/dockets/12345/

2. Qualcomm Inc. v. Apple Inc.
   Docket: 3:17-cv-00108
   Court: Southern District of California
   Filed: 2017-01-20
   Terminated: 2023-04-16
   Available Documents: 1876
   URL: https://www.courtlistener.com/api/rest/v4/dockets/67890/
...
```

---

## Simplified Python Example: Using Search API

```python
import requests

API_TOKEN = "YOUR_API_TOKEN"
BASE_URL = "https://www.courtlistener.com/api/rest/v4"
headers = {"Authorization": f"Token {API_TOKEN}"}

# Search for patent cases with available documents
params = {
    "type": "r",
    "nature_of_suit": "830",
    "available_only": "true",
    "filed_after": "2020-01-01",
    "order_by": "dateFiled desc",
    "page_size": 50
}

response = requests.get(
    f"{BASE_URL}/search/",
    headers=headers,
    params=params
)

if response.status_code == 200:
    results = response.json()['results']

    print(f"Found {len(results)} patent cases with documents\n")

    for case in results:
        print(f"{case['caseName']}")
        print(f"  Docket: {case['docketNumber']}")
        print(f"  Court: {case['court']}")
        print(f"  Filed: {case['dateFiled']}")
        if case.get('dateTerminated'):
            print(f"  Terminated: {case['dateTerminated']} ✓")
        else:
            print(f"  Status: Active (not terminated)")
        print()
```

---

## Advanced Filtering: Document Characteristics

### Filter by Page Count (Substantial Documents)

```bash
# Patent cases with documents over 50 pages
curl "https://www.courtlistener.com/api/rest/v4/recap-documents/?docket__nature_of_suit=830&is_available=true&page_count__gte=50"

# Patent cases with documents between 10-100 pages
curl "https://www.courtlistener.com/api/rest/v4/recap-documents/?docket__nature_of_suit=830&is_available=true&page_count__gte=10&page_count__lte=100"
```

### Filter by Document Upload Date

```bash
# Recently uploaded documents
curl "https://www.courtlistener.com/api/rest/v4/recap-documents/?docket__nature_of_suit=830&is_available=true&date_upload__gte=2024-01-01"
```

### Filter by Docket Entry Date

```bash
# Documents filed in 2023
curl "https://www.courtlistener.com/api/rest/v4/recap-documents/?docket__nature_of_suit=830&is_available=true&docket_entry__date_filed__gte=2023-01-01&docket_entry__date_filed__lte=2023-12-31"
```

---

## Tips for Finding Complete Data

### 1. Check Multiple Indicators

A "complete" case typically has:
- ✅ Termination date set (`date_terminated` is not null)
- ✅ Multiple available documents (complaint, answer, judgment, etc.)
- ✅ Final judgment document available
- ✅ No recent docket activity (`date_last_filing` is old)

### 2. Popular Patent Courts (Higher Document Availability)

Courts with high RECAP coverage for patent cases:
- `ded` - Delaware District Court
- `cand` - Northern District of California
- `txed` - Eastern District of Texas
- `nysd` - Southern District of New York

```bash
# Delaware patent cases with documents
curl "https://www.courtlistener.com/api/rest/v4/search/?type=r&nature_of_suit=830&court=ded&available_only=true"
```

### 3. Filter by Case Age

Older terminated cases are more likely to have complete documentation:

```bash
# Cases terminated 2+ years ago
curl "https://www.courtlistener.com/api/rest/v4/dockets/?nature_of_suit=830&date_terminated__lte=2022-01-01&date_terminated__isnull=false"
```

### 4. Check Document Count

Cases with more documents tend to be more complete:

```bash
# Python: Filter cases with 50+ documents
for docket in dockets:
    doc_count = get_document_count(docket['id'])
    if doc_count >= 50:
        print(f"{docket['case_name']}: {doc_count} documents")
```

---

## Limitations and Considerations

### 1. Document Availability

- Not all court documents are available through RECAP
- Sealed documents won't show as available
- Some courts have better coverage than others
- Older cases may have incomplete digitization

### 2. Termination Status

- Not all courts consistently update termination dates
- Some cases may be effectively closed but not marked terminated
- Appeals may restart "terminated" cases

### 3. Search API Limitations

- `available_only` filters for documents, but doesn't guarantee complete case data
- Cannot directly combine `available_only` with termination status in single search

### 4. Best Practice: Multi-Step Approach

For truly complete cases, use a multi-step process:
1. Find terminated cases in your date range
2. Check document availability for each
3. Verify document count meets your threshold
4. Optionally check for specific document types (judgment, order, etc.)

---

## Summary Table: Filter Options

| What You Want | Endpoint | Key Parameters |
|---------------|----------|----------------|
| Cases with PDFs | Search API | `type=r&nature_of_suit=830&available_only=true` |
| Terminated cases | Dockets | `nature_of_suit=830&date_terminated__isnull=false` |
| Both | Dockets + RECAP Docs | First get terminated, then check `is_available=true` |
| Document count | RECAP Documents | `docket__nature_of_suit=830&is_available=true&count=on` |
| By court | Any | Add `court=ded` (or other court ID) |
| By date range | Any | Add date filters like `date_filed__gte=2020-01-01` |
| Recent terminations | Dockets | `date_terminated__gte=2023-01-01&order_by=-date_terminated` |

---

## Quick Reference Commands

```bash
# Get 50 patent cases with documents
curl "https://www.courtlistener.com/api/rest/v4/search/?type=r&nature_of_suit=830&available_only=true&page_size=50" \
  -H "Authorization: Token YOUR_API_TOKEN"

# Count terminated patent cases
curl "https://www.courtlistener.com/api/rest/v4/dockets/?nature_of_suit=830&date_terminated__isnull=false&count=on" \
  -H "Authorization: Token YOUR_API_TOKEN"

# Get terminated patent cases in Delaware
curl "https://www.courtlistener.com/api/rest/v4/dockets/?nature_of_suit=830&court=ded&date_terminated__isnull=false&page_size=50" \
  -H "Authorization: Token YOUR_API_TOKEN"

# Count available documents for patent cases
curl "https://www.courtlistener.com/api/rest/v4/recap-documents/?docket__nature_of_suit=830&is_available=true&count=on" \
  -H "Authorization: Token YOUR_API_TOKEN"

# Get recent terminations with documents
curl "https://www.courtlistener.com/api/rest/v4/dockets/?nature_of_suit=830&date_terminated__gte=2024-01-01&date_terminated__isnull=false&page_size=50" \
  -H "Authorization: Token YOUR_API_TOKEN"
```

---

## Related Documentation

- `PATENT_CASE_SEARCH_GUIDE.md` - How to search for patent cases
- `COUNTING_CASES_GUIDE.md` - How to count cases in the database
- `DJANGO_REST_API_DOCUMENTATION.md` - Complete API reference

---

**Last Updated:** 2025-11-05
**API Version:** V4
