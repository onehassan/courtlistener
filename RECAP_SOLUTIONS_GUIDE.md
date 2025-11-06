# RECAP 403 Error: Solutions and Implementation Guide

## Problem Summary

When trying to access `/api/rest/v3/recap-documents/` or `/api/rest/v4/recap-documents/`, you get a **403 Forbidden** error. This is because the endpoint requires the `has_recap_api_access` permission, which is a custom permission that must be explicitly granted by administrators.

---

## Solution Overview

There are **3 main solutions** depending on your situation:

| Situation | Solution | Permissions Required |
|-----------|----------|---------------------|
| **No admin access** | Use Search API | None (public) |
| **Have admin access** | Grant permission | Admin role |
| **Want direct access** | Use Docket Entries endpoint | Same as RECAP (if you have it) |

---

## SOLUTION 1: Search API (Recommended for Public Access)

### Why Use This?
- **No special permissions needed**
- Works for anonymous users
- Powerful Elasticsearch-backed search
- Returns dockets with nested documents
- No authentication required

### Implementation

#### Basic Usage (No Authentication)

```python
import requests

def get_documents_for_docket(docket_number):
    """
    Get all documents for a docket using the public Search API.
    """
    response = requests.get(
        "https://api.courtlistener.com/api/rest/v4/search/",
        params={
            "q": f"docket_number:{docket_number}",
            "type": "rd",  # RECAP_DOCUMENT type
            "cursor": None  # For pagination, provide cursor from response
        }
    )
    
    if response.status_code == 200:
        data = response.json()
        documents = data.get("results", [])
        return documents
    else:
        raise Exception(f"API Error: {response.status_code}")

# Usage
docs = get_documents_for_docket("2024-cv-01234")
for doc in docs:
    print(f"Document {doc['id']}: {doc['description']}")
```

#### Search by Docket ID

```python
def get_all_documents_by_docket_id(docket_id):
    """
    Get all documents for a specific docket ID using the Search API.
    
    Args:
        docket_id: The numerical ID of the docket
    
    Returns:
        List of all documents (handles pagination automatically)
    """
    all_documents = []
    cursor = None
    
    while True:
        params = {
            "q": f"docket_id:{docket_id}",
            "type": "r",  # type=r returns dockets with child documents
            "limit": 100  # Maximum results per page
        }
        
        if cursor:
            params["cursor"] = cursor
        
        response = requests.get(
            "https://api.courtlistener.com/api/rest/v4/search/",
            params=params
        )
        
        if response.status_code != 200:
            break
        
        data = response.json()
        results = data.get("results", [])
        
        # Extract nested documents from each docket result
        for result in results:
            recap_documents = result.get("recap_documents", [])
            all_documents.extend(recap_documents)
        
        # Check for next page
        next_cursor = data.get("next")
        if not next_cursor or not results:
            break
        
        cursor = next_cursor
    
    return all_documents

# Usage
all_docs = get_all_documents_by_docket_id(12345)
print(f"Found {len(all_docs)} documents")
```

#### Advanced Search with Filters

```python
def advanced_search(query, court=None, filed_after=None, filed_before=None):
    """
    Advanced search with multiple filters.
    
    Args:
        query: Search query string
        court: Court ID (e.g., 'ca1', 'scotus')
        filed_after: Start date (YYYY-MM-DD)
        filed_before: End date (YYYY-MM-DD)
    """
    params = {
        "q": query,
        "type": "rd",  # Individual documents
    }
    
    if court:
        params["court"] = court
    
    if filed_after:
        params["filed_after"] = filed_after
    
    if filed_before:
        params["filed_before"] = filed_before
    
    response = requests.get(
        "https://api.courtlistener.com/api/rest/v4/search/",
        params=params
    )
    
    return response.json()

# Usage
results = advanced_search(
    query="patent infringement",
    court="cafc",  # Court of Appeals for the Federal Circuit
    filed_after="2020-01-01"
)

for doc in results["results"]:
    print(f"{doc['id']}: {doc['description']}")
```

### Curl Examples

```bash
# Simple search for documents
curl "https://api.courtlistener.com/api/rest/v4/search/?q=patent&type=rd"

# Search by docket number
curl "https://api.courtlistener.com/api/rest/v4/search/?q=docket_number:2024-cv-01234&type=rd"

# Search with date range
curl "https://api.courtlistener.com/api/rest/v4/search/?q=bankruptcy&type=rd&filed_after=2023-01-01&filed_before=2023-12-31"

# Search specific court
curl "https://api.courtlistener.com/api/rest/v4/search/?q=test&type=rd&court=ca1"
```

---

## SOLUTION 2: Grant has_recap_api_access Permission (Admin Only)

### Prerequisites
- You have admin/superuser access to the CourtListener installation
- You can access Django admin or the database

### Option A: Via Django Admin

```python
# 1. In Django shell (python manage.py shell)
from django.contrib.auth.models import User, Permission

# Get the user
user = User.objects.get(username='your_username')

# Get the permission
permission = Permission.objects.get(codename='has_recap_api_access')

# Grant it
user.user_permissions.add(permission)

# Verify
print(user.has_perm('search.has_recap_api_access'))  # Should be True
```

### Option B: Via Management Command

```bash
# Create a Django management command (if not exists)
python manage.py shell << 'EOF'
from django.contrib.auth.models import User, Permission

user = User.objects.get(username='your_username')
permission = Permission.objects.get(codename='has_recap_api_access')
user.user_permissions.add(permission)
print(f"Permission granted to {user.username}")
EOF
```

### Option C: Direct Database (PostgreSQL)

```sql
INSERT INTO auth_user_user_permissions (user_id, permission_id)
SELECT u.id, p.id
FROM auth_user u, auth_permission p
WHERE u.username = 'your_username'
AND p.codename = 'has_recap_api_access'
AND NOT EXISTS (
    SELECT 1 FROM auth_user_user_permissions
    WHERE user_id = u.id AND permission_id = p.id
);
```

### After Granting Permission

Users can now use the direct endpoint:

```python
import requests

def get_recap_documents_direct(docket_id, api_token):
    """
    Get RECAP documents directly using the restricted endpoint.
    
    Requires: has_recap_api_access permission
    """
    headers = {"Authorization": f"Token {api_token}"}
    
    response = requests.get(
        "https://api.courtlistener.com/api/rest/v3/recap-documents/",
        headers=headers,
        params={"docket_entry__docket__id": docket_id}
    )
    
    if response.status_code == 200:
        return response.json()["results"]
    elif response.status_code == 403:
        raise PermissionError("User does not have has_recap_api_access permission")
    else:
        raise Exception(f"API Error: {response.status_code}")

# Usage
token = "your_api_token_here"
documents = get_recap_documents_direct(12345, token)
```

---

## SOLUTION 3: Docket Entries Endpoint

### Use Case
If you have `has_recap_api_access` permission but prefer nested document structures, use the docket-entries endpoint instead.

### Why This Approach?
- Returns documents nested within entries
- Can filter by entry or document properties
- Optimized with prefetch_related
- Same permission as direct endpoint

### Implementation

```python
import requests

def get_docket_entries_with_documents(docket_id, api_token):
    """
    Get all docket entries for a docket with their nested documents.
    
    Requires: has_recap_api_access permission
    """
    headers = {"Authorization": f"Token {api_token}"}
    
    all_data = []
    page = 1
    
    while True:
        response = requests.get(
            "https://api.courtlistener.com/api/rest/v3/docket-entries/",
            headers=headers,
            params={
                "docket__id": docket_id,
                "page": page,
                "page_size": 100
            }
        )
        
        if response.status_code != 200:
            break
        
        data = response.json()
        results = data.get("results", [])
        
        if not results:
            break
        
        all_data.extend(results)
        
        # Check if there's a next page
        if not data.get("next"):
            break
        
        page += 1
    
    return all_data

def extract_documents_from_entries(entries):
    """
    Extract all documents from docket entries.
    """
    documents = []
    
    for entry in entries:
        docs = entry.get("recap_documents", [])
        for doc in docs:
            # Add reference to parent entry
            doc["entry_number"] = entry.get("entry_number")
            doc["entry_description"] = entry.get("description")
            documents.append(doc)
    
    return documents

# Usage
token = "your_api_token_here"
entries = get_docket_entries_with_documents(12345, token)
documents = extract_documents_from_entries(entries)

for doc in documents:
    print(f"Entry {doc['entry_number']}: Doc {doc['id']} - {doc['description']}")
```

### Advanced Filtering

```python
def get_documents_by_tags(api_token, tag_ids):
    """
    Get all documents with specific tags.
    """
    headers = {"Authorization": f"Token {api_token}"}
    
    params = {}
    for i, tag_id in enumerate(tag_ids):
        params[f"recap_documents__tags"] = tag_id
    
    response = requests.get(
        "https://api.courtlistener.com/api/rest/v3/docket-entries/",
        headers=headers,
        params=params
    )
    
    return response.json()

def get_documents_by_date_range(api_token, start_date, end_date):
    """
    Get documents created within a date range.
    """
    headers = {"Authorization": f"Token {api_token}"}
    
    response = requests.get(
        "https://api.courtlistener.com/api/rest/v3/recap-documents/",
        headers=headers,
        params={
            "date_upload__gte": start_date,
            "date_upload__lte": end_date
        }
    )
    
    return response.json()
```

---

## Troubleshooting

### Error: "403 Forbidden"

**Cause:** Missing `has_recap_api_access` permission

**Solution:** Use Solution 1 (Search API) or Solution 2 (Grant permission)

```python
# Check if API token is valid
import requests

response = requests.get(
    "https://api.courtlistener.com/api/rest/v3/dockets/?id=1",
    headers={"Authorization": f"Token {api_token}"}
)
print(response.status_code)  # Should be 200
```

### Error: "401 Unauthorized"

**Cause:** Invalid or missing API token

**Solution:** Verify API token and add it correctly:

```python
# Correct way
headers = {"Authorization": f"Token {your_token}"}

# Wrong ways
headers = {"Authorization": f"Bearer {your_token}"}  # Don't use Bearer
headers = {"Authorization": your_token}  # Token keyword is required
```

### Error: "429 Too Many Requests"

**Cause:** Rate limiting (applies to authenticated users)

**Solution:** Add delays between requests:

```python
import time
import requests

for docket_id in docket_ids:
    response = requests.get(
        f"https://api.courtlistener.com/api/rest/v4/search/?q=docket_id:{docket_id}&type=r"
    )
    data = response.json()
    
    # Wait before next request to avoid rate limiting
    time.sleep(1)  # 1 second delay
```

### V3 API Blocking (New Users)

**Error:** 403 when using V3 API endpoints

**Cause:** `V3APIPermission` blocks new users randomly

**Solution:** Use V4 API instead:

```python
# Change from v3 to v4
url_v3 = "https://api.courtlistener.com/api/rest/v3/recap-documents/"
url_v4 = "https://api.courtlistener.com/api/rest/v4/search/"  # Use this instead
```

---

## Performance Comparison

| Method | Speed | Accuracy | Flexibility |
|--------|-------|----------|------------|
| Search API (type=r) | Very Fast (ES) | High | High |
| Search API (type=rd) | Very Fast (ES) | High | High |
| Direct Endpoint | Medium (DB) | Exact | Medium |
| Docket Entries | Medium (DB) | Exact | Medium |

### Recommended Approach by Use Case

**Use Search API if:**
- You don't have special permissions
- You need to search across many documents
- You want fastest results
- You're building a public-facing application

**Use Direct Endpoint if:**
- You have special permissions
- You need exact filtering by specific fields
- You want database-level accuracy
- You're integrating with internal systems

---

## Complete Example: Bulk Document Retrieval

```python
import requests
import json
from datetime import datetime

class RECAPDocumentFetcher:
    """
    Fetches RECAP documents using the public Search API.
    No authentication required.
    """
    
    BASE_URL = "https://api.courtlistener.com/api/rest/v4/search"
    
    def __init__(self, docket_ids):
        self.docket_ids = docket_ids
        self.all_documents = []
    
    def fetch_documents(self):
        """Fetch documents for all dockets."""
        for docket_id in self.docket_ids:
            print(f"Fetching documents for docket {docket_id}...")
            docs = self._fetch_for_docket(docket_id)
            self.all_documents.extend(docs)
            print(f"  Found {len(docs)} documents")
        
        return self.all_documents
    
    def _fetch_for_docket(self, docket_id):
        """Fetch documents for a single docket."""
        documents = []
        cursor = None
        
        while True:
            params = {
                "q": f"docket_id:{docket_id}",
                "type": "r",
                "limit": 100
            }
            
            if cursor:
                params["cursor"] = cursor
            
            response = requests.get(self.BASE_URL, params=params)
            
            if response.status_code != 200:
                print(f"  Error: {response.status_code}")
                break
            
            data = response.json()
            results = data.get("results", [])
            
            if not results:
                break
            
            for result in results:
                documents.extend(result.get("recap_documents", []))
            
            cursor = data.get("next")
            if not cursor:
                break
        
        return documents
    
    def save_to_json(self, filename):
        """Save documents to JSON file."""
        with open(filename, 'w') as f:
            json.dump(self.all_documents, f, indent=2)
        print(f"Saved {len(self.all_documents)} documents to {filename}")
    
    def export_csv(self, filename):
        """Export documents to CSV."""
        import csv
        
        if not self.all_documents:
            print("No documents to export")
            return
        
        with open(filename, 'w', newline='') as f:
            writer = csv.DictWriter(
                f,
                fieldnames=['id', 'pacer_doc_id', 'description', 'date_upload']
            )
            writer.writeheader()
            
            for doc in self.all_documents:
                writer.writerow({
                    'id': doc.get('id'),
                    'pacer_doc_id': doc.get('pacer_doc_id'),
                    'description': doc.get('description'),
                    'date_upload': doc.get('date_upload')
                })
        
        print(f"Exported {len(self.all_documents)} documents to {filename}")

# Usage
docket_ids = [123456, 789012, 345678]
fetcher = RECAPDocumentFetcher(docket_ids)
documents = fetcher.fetch_documents()

# Save results
fetcher.save_to_json("documents.json")
fetcher.export_csv("documents.csv")

print(f"\nTotal documents fetched: {len(documents)}")
```

---

## API Reference Summary

### Search API Endpoints

```
GET /api/rest/v4/search/
Parameters:
  q             - Search query
  type          - Search type (r=dockets, rd=documents)
  court         - Court ID filter
  filed_after   - Date filter (YYYY-MM-DD)
  filed_before  - Date filter
  page          - Page number
  cursor        - Cursor for pagination
```

### RECAP Document Endpoints (Requires Permission)

```
GET /api/rest/v3/recap-documents/
Parameters:
  id                      - Document ID
  docket_entry__docket__id - Docket ID
  pacer_doc_id            - PACER document ID
  date_upload__gte        - Date range start
  date_upload__lte        - Date range end
  is_available            - Filter by availability
  tags                    - Filter by tags
  page                    - Page number
```

### Docket Entries Endpoint (Requires Permission)

```
GET /api/rest/v3/docket-entries/
Parameters:
  docket__id              - Filter by docket
  recap_documents__id     - Filter by document
  recap_documents__tags   - Filter by document tags
  page                    - Page number
```

---

## References

- Main Investigation: [RECAP_403_INVESTIGATION.md](RECAP_403_INVESTIGATION.md)
- Access Flow Diagrams: [RECAP_ACCESS_FLOW.md](RECAP_ACCESS_FLOW.md)
- API Documentation: https://api.courtlistener.com/help/api/
- CourtListener GitHub: https://github.com/freelawproject/courtlistener/

