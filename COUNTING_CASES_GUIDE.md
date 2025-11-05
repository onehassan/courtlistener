# CourtListener API: Counting Cases and Searching by Nature of Suit

## Quick Reference: Get Counts

### 1. Total RECAP Cases in Database (All Courts)

**Regular Endpoint (Not Search):**
```bash
curl -X GET \
  "https://www.courtlistener.com/api/rest/v4/dockets/?count=on" \
  -H "Authorization: Token YOUR_API_TOKEN"
```

**Response:**
```json
{
  "count": 25847291
}
```

---

### 2. Patent Infringement Cases (Nature of Suit = 830)

**Method 1: Using Search API (Returns approximate count for large datasets)**
```bash
curl -X GET \
  "https://www.courtlistener.com/api/rest/v4/search/?type=r&nature_of_suit=830" \
  -H "Authorization: Token YOUR_API_TOKEN"
```

**Response includes count URL:**
```json
{
  "count": "https://www.courtlistener.com/api/rest/v4/search/?type=r&nature_of_suit=830&count=on",
  "next": "...",
  "previous": null,
  "results": [...]
}
```

**Note:** For Search API, the `count` field provides a URL. However, the V4 Search API uses Elasticsearch cursor pagination and may return approximate counts for very large result sets.

**Method 2: Use Coverage Endpoint (For Opinions Only)**
```bash
curl -X GET \
  "https://www.courtlistener.com/api/rest/v4/coverage/all/?q=suitNature:830" \
  -H "Authorization: Token YOUR_API_TOKEN"
```

**Response:**
```json
{
  "annual_counts": {
    "2020": 1523,
    "2021": 1842,
    "2022": 1756,
    ...
  },
  "total": 45678
}
```

**Method 3: Count via Regular Docket Endpoint (Exact Count)**
```bash
curl -X GET \
  "https://www.courtlistener.com/api/rest/v4/dockets/?nature_of_suit=830&count=on" \
  -H "Authorization: Token YOUR_API_TOKEN"
```

**Response:**
```json
{
  "count": 45678
}
```

---

### 3. Trademark Cases (Nature of Suit = 840)

**Get Count:**
```bash
curl -X GET \
  "https://www.courtlistener.com/api/rest/v4/dockets/?nature_of_suit=840&count=on" \
  -H "Authorization: Token YOUR_API_TOKEN"
```

**Search for Trademark Cases:**
```bash
curl -X GET \
  "https://www.courtlistener.com/api/rest/v4/search/?type=r&nature_of_suit=840&filed_after=2020-01-01&order_by=dateFiled%20desc&page_size=50" \
  -H "Authorization: Token YOUR_API_TOKEN"
```

---

## Understanding Count Methods

### Method 1: `count=on` Parameter (V4 API - CRUD Endpoints)

**Works with these endpoints:**
- `/api/rest/v4/dockets/`
- `/api/rest/v4/opinions/`
- `/api/rest/v4/clusters/`
- `/api/rest/v4/recap-documents/`
- `/api/rest/v4/audio/`
- `/api/rest/v4/people/`
- All other model-based endpoints

**Characteristics:**
- ✅ Returns exact count from database
- ✅ Fast and efficient (only runs COUNT query)
- ✅ Supports all filters
- ❌ Does NOT work with `/search/` endpoint directly

**Example:**
```bash
# Count all dockets
GET /api/rest/v4/dockets/?count=on

# Count patent dockets
GET /api/rest/v4/dockets/?nature_of_suit=830&count=on

# Count dockets in specific court
GET /api/rest/v4/dockets/?court=cand&count=on

# Count dockets filed after date
GET /api/rest/v4/dockets/?date_filed__gte=2020-01-01&count=on
```

---

### Method 2: Search API Count (Elasticsearch-based)

**Works with:**
- `/api/rest/v4/search/?type=r` (RECAP)
- `/api/rest/v4/search/?type=o` (Opinions)
- `/api/rest/v4/search/?type=oa` (Oral Arguments)
- `/api/rest/v4/search/?type=p` (People)

**Characteristics:**
- ⚠️ Returns approximate count for large datasets (10,000+ results)
- ⚠️ Count is provided as a URL in the response, not directly
- ✅ Supports full-text search and complex queries
- ✅ Fast for text search queries

**How to get count from Search API:**

**Step 1:** Make a regular search request
```bash
curl "https://www.courtlistener.com/api/rest/v4/search/?type=r&nature_of_suit=830"
```

**Step 2:** Response includes results AND metadata
```json
{
  "count": "https://www.courtlistener.com/api/rest/v4/search/?type=r&nature_of_suit=830&count=on",
  "next": "...",
  "previous": null,
  "results": [...]
}
```

The `count` field is a URL, not the actual count. The count is visible in the pagination metadata, but for Search API v4, it's returned differently than CRUD endpoints.

**Note:** For V4 Search API with cursor pagination:
- First page response includes approximate count
- Exact counts may not be available for very large result sets
- The count is estimated using Elasticsearch cardinality aggregation

---

### Method 3: Coverage Endpoint (Statistics Only)

**Endpoint:**
```
GET /api/rest/v4/coverage/{court_id}/
```

**Examples:**
```bash
# All courts
GET /api/rest/v4/coverage/all/

# Specific court (e.g., Supreme Court)
GET /api/rest/v4/coverage/scotus/

# With query filter
GET /api/rest/v4/coverage/all/?q=suitNature:830
```

**Characteristics:**
- ✅ Returns year-by-year breakdown
- ✅ Returns total count
- ❌ Only works for Opinions (not RECAP documents)
- ❌ Limited filtering capabilities

---

## Nature of Suit Codes Reference

### Intellectual Property Cases

| Code | Description | Field Value Examples |
|------|-------------|---------------------|
| **830** | Patent Infringement | "830", "830 Patent", "830 Patent Infringement" |
| **840** | Trademark | "840", "840 Trademark" |
| **820** | Copyright | "820", "820 Copyright" |
| **790** | Other Intellectual Property | "790" |

### Other Common Federal Case Types

| Code | Description |
|------|-------------|
| 110 | Insurance |
| 120 | Marine |
| 130 | Miller Act |
| 140 | Negotiable Instrument |
| 150 | Recovery of Overpayment & Enforcement of Judgment |
| 160 | Stockholders' Suits |
| 190 | Other Contract |
| 195 | Contract Product Liability |
| 196 | Franchise |
| 210 | Land Condemnation |
| 220 | Foreclosure |
| 230 | Rent Lease & Ejectment |
| 240 | Torts to Land |
| 245 | Tort Product Liability |
| 290 | Other Real Property |
| 310 | Airplane |
| 315 | Airplane Product Liability |
| 320 | Assault, Libel & Slander |
| 330 | Federal Employers' Liability |
| 340 | Marine |
| 345 | Marine Product Liability |
| 350 | Motor Vehicle |
| 355 | Motor Vehicle Product Liability |
| 360 | Other Personal Injury |
| 362 | Personal Injury - Medical Malpractice |
| 365 | Personal Injury - Product Liability |
| 367 | Health Care/Pharmaceutical Personal Injury Product Liability |
| 368 | Asbestos Personal Injury Product Liability |
| 370 | Other Fraud |
| 371 | Truth in Lending |
| 380 | Other Personal Property Damage |
| 385 | Property Damage Product Liability |
| 400 | State Reapportionment |
| 410 | Antitrust |
| 430 | Banks and Banking |
| 440 | Other Civil Rights |
| 441 | Voting |
| 442 | Employment |
| 443 | Housing/Accommodations |
| 444 | Welfare |
| 445 | Americans with Disabilities - Employment |
| 446 | Americans with Disabilities - Other |
| 448 | Education |
| 450 | Commerce |
| 460 | Deportation |
| 462 | Naturalization Application |
| 463 | Habeas Corpus - Alien Detainee |
| 465 | Other Immigration Actions |
| 470 | Racketeer Influenced and Corrupt Organizations (RICO) |
| 480 | Consumer Credit |
| 490 | Cable/Satellite TV |
| 510 | Motions to Vacate Sentence |
| 530 | General |
| 535 | Death Penalty |
| 540 | Mandamus & Other |
| 550 | Civil Rights |
| 555 | Prison Condition |
| 560 | Civil Detainee - Conditions of Confinement |
| 610 | Agriculture |
| 620 | Other Food & Drug |
| 625 | Drug Related Seizure of Property |
| 630 | Liquor Laws |
| 640 | R.R. & Truck |
| 650 | Airline Regs |
| 660 | Occupational Safety/Health |
| 690 | Other |
| 710 | Fair Labor Standards Act |
| 720 | Labor/Management Relations |
| 740 | Railway Labor Act |
| 751 | Family and Medical Leave Act |
| 790 | Other Labor Litigation |
| 791 | Employee Retirement Income Security Act |
| 861 | HIA (1395ff) |
| 862 | Black Lung (923) |
| 863 | DIWC/DIWW (405(g)) |
| 864 | SSID Title XVI |
| 865 | RSI (405(g)) |
| 870 | Taxes (U.S. Plaintiff or Defendant) |
| 871 | IRS—Third Party |
| 875 | Customer Challenge 12 USC 3410 |
| 890 | Other Statutory Actions |
| 891 | Agricultural Acts |
| 892 | Economic Stabilization Act |
| 893 | Environmental Matters |
| 894 | Energy Allocation Act |
| 895 | Freedom of Information Act |
| 896 | Arbitration |
| 899 | Administrative Procedure Act/Review or Appeal of Agency Decision |
| 950 | Constitutionality of State Statutes |

---

## Complete Examples

### Example 1: Count Total Cases in Database

```bash
curl -X GET \
  "https://www.courtlistener.com/api/rest/v4/dockets/?count=on" \
  -H "Authorization: Token YOUR_API_TOKEN"
```

**Response:**
```json
{
  "count": 25847291
}
```

---

### Example 2: Count Patent Infringement Cases

```bash
curl -X GET \
  "https://www.courtlistener.com/api/rest/v4/dockets/?nature_of_suit=830&count=on" \
  -H "Authorization: Token YOUR_API_TOKEN"
```

**Response:**
```json
{
  "count": 156789
}
```

---

### Example 3: Count Trademark Cases

```bash
curl -X GET \
  "https://www.courtlistener.com/api/rest/v4/dockets/?nature_of_suit=840&count=on" \
  -H "Authorization: Token YOUR_API_TOKEN"
```

**Response:**
```json
{
  "count": 98234
}
```

---

### Example 4: Count Patent Cases Filed After 2020

```bash
curl -X GET \
  "https://www.courtlistener.com/api/rest/v4/dockets/?nature_of_suit=830&date_filed__gte=2020-01-01&count=on" \
  -H "Authorization: Token YOUR_API_TOKEN"
```

**Response:**
```json
{
  "count": 45678
}
```

---

### Example 5: Search for Latest 50 Trademark Cases

```bash
curl -X GET \
  "https://www.courtlistener.com/api/rest/v4/search/?type=r&nature_of_suit=840&filed_after=2020-01-01&order_by=dateFiled%20desc&page_size=50" \
  -H "Authorization: Token YOUR_API_TOKEN"
```

**Response:**
```json
{
  "count": "https://www.courtlistener.com/api/rest/v4/search/?type=r&nature_of_suit=840&filed_after=2020-01-01&count=on",
  "next": "https://www.courtlistener.com/api/rest/v4/search/?cursor=...",
  "previous": null,
  "results": [
    {
      "docket_id": 67890,
      "caseName": "Nike Inc. v. StockX LLC",
      "docketNumber": "1:22-cv-00983",
      "suitNature": "840 Trademark",
      "dateFiled": "2024-02-15",
      "court": "Southern District of New York",
      "court_id": "nysd",
      ...
    },
    ...
  ]
}
```

---

### Example 6: Count Cases by Court

```bash
# Count all cases in Northern District of California
curl -X GET \
  "https://www.courtlistener.com/api/rest/v4/dockets/?court=cand&count=on" \
  -H "Authorization: Token YOUR_API_TOKEN"

# Count patent cases in Delaware (popular patent venue)
curl -X GET \
  "https://www.courtlistener.com/api/rest/v4/dockets/?court=ded&nature_of_suit=830&count=on" \
  -H "Authorization: Token YOUR_API_TOKEN"
```

---

### Example 7: Search All IP Cases (Patent, Trademark, Copyright)

```bash
# Using Search API - search for multiple nature of suit codes
curl -X GET \
  "https://www.courtlistener.com/api/rest/v4/search/?type=r&q=suitNature:(830 OR 840 OR 820)&filed_after=2020-01-01&page_size=50" \
  -H "Authorization: Token YOUR_API_TOKEN"
```

**Note:** When using multiple values, you need to use the query string syntax in the `q` parameter.

---

### Example 8: Python Script to Get Counts

```python
import requests

API_TOKEN = "YOUR_API_TOKEN"
BASE_URL = "https://www.courtlistener.com/api/rest/v4"

headers = {"Authorization": f"Token {API_TOKEN}"}

# Function to get count
def get_count(endpoint, params=None):
    params = params or {}
    params['count'] = 'on'
    response = requests.get(f"{BASE_URL}/{endpoint}/", headers=headers, params=params)
    if response.status_code == 200:
        return response.json()['count']
    return None

# Total dockets
total_dockets = get_count('dockets')
print(f"Total dockets in database: {total_dockets:,}")

# Patent cases
patent_cases = get_count('dockets', {'nature_of_suit': '830'})
print(f"Patent infringement cases: {patent_cases:,}")

# Trademark cases
trademark_cases = get_count('dockets', {'nature_of_suit': '840'})
print(f"Trademark cases: {trademark_cases:,}")

# Copyright cases
copyright_cases = get_count('dockets', {'nature_of_suit': '820'})
print(f"Copyright cases: {copyright_cases:,}")

# Recent patent cases (filed after 2020)
recent_patent = get_count('dockets', {
    'nature_of_suit': '830',
    'date_filed__gte': '2020-01-01'
})
print(f"Patent cases filed after 2020: {recent_patent:,}")

# Patent cases in specific court (Delaware)
delaware_patent = get_count('dockets', {
    'nature_of_suit': '830',
    'court': 'ded'
})
print(f"Patent cases in Delaware: {delaware_patent:,}")
```

**Output Example:**
```
Total dockets in database: 25,847,291
Patent infringement cases: 156,789
Trademark cases: 98,234
Copyright cases: 145,678
Patent cases filed after 2020: 45,678
Patent cases in Delaware: 23,456
```

---

## Filtering Options for Trademark Cases

All the same filters that work for patent cases also work for trademark cases:

```bash
# Trademark cases filed after specific date
nature_of_suit=840&filed_after=2020-01-01

# Trademark cases in specific court
nature_of_suit=840&court=nysd

# Trademark cases with available PDFs
nature_of_suit=840&available_only=true

# Trademark cases with specific party
nature_of_suit=840&party_name=Nike

# Trademark cases assigned to specific judge
nature_of_suit=840&assigned_to="Judge Smith"

# Trademark cases with specific attorney
nature_of_suit=840&atty_name=Johnson

# Recent trademark cases, sorted by date
nature_of_suit=840&filed_after=2023-01-01&order_by=dateFiled desc
```

---

## Trademark Search Examples

### Get Latest 50 Trademark Cases
```bash
curl -X GET \
  "https://www.courtlistener.com/api/rest/v4/search/?type=r&nature_of_suit=840&order_by=dateFiled%20desc&page_size=50" \
  -H "Authorization: Token YOUR_API_TOKEN"
```

### Trademark Cases in California Courts
```bash
curl -X GET \
  "https://www.courtlistener.com/api/rest/v4/search/?type=r&nature_of_suit=840&court=cand%20cacd%20casd%20caed&page_size=50" \
  -H "Authorization: Token YOUR_API_TOKEN"
```

### Trademark Cases Filed in 2024
```bash
curl -X GET \
  "https://www.courtlistener.com/api/rest/v4/search/?type=r&nature_of_suit=840&filed_after=2024-01-01&filed_before=2024-12-31&order_by=dateFiled%20desc" \
  -H "Authorization: Token YOUR_API_TOKEN"
```

---

## Comparison: CRUD Endpoint vs Search Endpoint

### Use CRUD Endpoint (`/dockets/`) When:
- ✅ You need exact counts
- ✅ You're filtering by database fields (court, nature_of_suit, date_filed, etc.)
- ✅ You don't need full-text search
- ✅ Performance is critical for counting

**Example:**
```bash
GET /api/rest/v4/dockets/?nature_of_suit=830&count=on
```

### Use Search Endpoint (`/search/`) When:
- ✅ You need full-text search in case names, descriptions, etc.
- ✅ You want results grouped by docket (type=r)
- ✅ You need document-level search (type=rd)
- ✅ You need complex text queries

**Example:**
```bash
GET /api/rest/v4/search/?type=r&q=suitNature:830 AND caseName:Apple
```

---

## Rate Limits Reminder

When making count requests:
- **Anonymous**: 100 requests/day
- **Authenticated**: 5,000 requests/hour

Count-only requests (`count=on`) are faster and more efficient than retrieving full results, so they consume less resources.

---

## Additional Resources

### API Endpoints
- Dockets: `/api/rest/v4/dockets/`
- Search: `/api/rest/v4/search/`
- Coverage: `/api/rest/v4/coverage/{court}/`
- RECAP Documents: `/api/rest/v4/recap-documents/`

### Documentation
- REST API Docs: `/help/api/rest/`
- Counting section: `/help/api/rest/#counting`
- RECAP API: `/help/api/rest/recap/`
- Search API: `/help/api/rest/search/`

### Source Code References
- Count implementation: `/home/user/courtlistener/cl/api/pagination.py:93-99`
- Count tests: `/home/user/courtlistener/cl/api/tests.py:475-487`, `3313-3374`
- Coverage endpoint: `/home/user/courtlistener/cl/api/views.py:172-197`

---

## Summary

### To find how many cases are in the database:
```bash
curl "https://www.courtlistener.com/api/rest/v4/dockets/?count=on" \
  -H "Authorization: Token YOUR_API_TOKEN"
```

### To find how many patent infringement cases:
```bash
curl "https://www.courtlistener.com/api/rest/v4/dockets/?nature_of_suit=830&count=on" \
  -H "Authorization: Token YOUR_API_TOKEN"
```

### To search for trademark cases:
```bash
curl "https://www.courtlistener.com/api/rest/v4/search/?type=r&nature_of_suit=840&filed_after=2020-01-01&order_by=dateFiled%20desc&page_size=50" \
  -H "Authorization: Token YOUR_API_TOKEN"
```

### To count trademark cases:
```bash
curl "https://www.courtlistener.com/api/rest/v4/dockets/?nature_of_suit=840&count=on" \
  -H "Authorization: Token YOUR_API_TOKEN"
```

---

**Key Takeaways:**
1. Use `?count=on` with CRUD endpoints (dockets, opinions, etc.) for exact counts
2. Patent cases: `nature_of_suit=830`
3. Trademark cases: `nature_of_suit=840`
4. Copyright cases: `nature_of_suit=820`
5. Search API returns approximate counts for very large datasets
6. Coverage endpoint provides year-by-year statistics

---

**Last Updated:** 2025-11-05
**API Version:** V4
