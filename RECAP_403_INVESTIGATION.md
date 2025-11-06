# Investigation: /recap-documents/ Endpoint 403 Error

## Executive Summary

The `/recap-documents/` endpoint (RECAPDocumentViewSet) returns **403 Forbidden** because it requires users to have the **`has_recap_api_access`** permission. This is a deliberate access control mechanism implemented via the `RECAPUsersReadOnly` permission class.

## 1. Root Cause: Permission Requirements

### RECAPDocumentViewSet Permission Configuration
**File:** `/home/user/courtlistener/cl/search/api_views.py` (lines 182-206)

```python
class RECAPDocumentViewSet(
    LoggingMixin,
    NoFilterCacheListMixin,
    DeferredFieldsMixin,
    viewsets.ModelViewSet,
):
    permission_classes = (RECAPUsersReadOnly, V3APIPermission)
    serializer_class = RECAPDocumentSerializer
    filterset_class = RECAPDocumentFilter
    # ... rest of configuration
```

### RECAPUsersReadOnly Permission Class
**File:** `/home/user/courtlistener/cl/api/utils.py` (lines 747-762)

```python
class RECAPUsersReadOnly(DjangoModelPermissions):
    """Provides access to users with the right permissions.
    
    Such users must have the has_recap_api_access flag set on their account for
    this object type.
    """
    
    perms_map = {
        "GET": ["%(app_label)s.has_recap_api_access"],
        "OPTIONS": ["%(app_label)s.has_recap_api_access"],
        "HEAD": ["%(app_label)s.has_recap_api_access"],
        "POST": ["%(app_label)s.add_%(model_name)s"],
        "PUT": ["%(app_label)s.change_%(model_name)s"],
        "PATCH": ["%(app_label)s.change_%(model_name)s"],
        "DELETE": ["%(app_label)s.delete_%(model_name)s"],
    }
```

**Key Point:** GET requests require the `search.has_recap_api_access` permission.

### V3APIPermission
**File:** `/home/user/courtlistener/cl/api/api_permissions.py` (lines 22-97)

This permission class enforces a "new user blocking" policy for V3 API. It may also reject requests based on a V3 blocking list or if the user is flagged as new.

## 2. Alternative Approaches to Retrieve Documents

### APPROACH 1: Docket Entries Endpoint (Recommended)
**URL Pattern:** `/api/rest/v3/docket-entries/`

**Key Advantages:**
- Uses `RECAPUsersReadOnly` permission (same as RECAP documents)
- Returns nested `recap_documents` array
- More efficient for retrieving documents tied to a docket entry
- Includes prefetch_related optimization for child documents

**Permission:** Requires same `has_recap_api_access` permission

**Serialization:**
```python
class DocketEntrySerializer:
    docket = HyperlinkedRelatedField(...)
    recap_documents = RECAPDocumentSerializer(many=True, read_only=True)
```

**Example Query:**
```bash
# Get all docket entries for docket ID 1 with their documents
GET /api/rest/v3/docket-entries/?docket__id=1

# Filter by document ID
GET /api/rest/v3/docket-entries/?recap_documents__id=123

# Filter by document tags
GET /api/rest/v3/docket-entries/?recap_documents__tags=1
```

**Response Structure:**
```json
{
  "count": 5,
  "next": "...",
  "results": [
    {
      "id": 1,
      "docket": "http://api/.../dockets/1/",
      "entry_number": 1,
      "description": "...",
      "recap_documents": [
        {
          "id": 101,
          "pacer_doc_id": "...",
          "description": "Document",
          ...
        },
        {
          "id": 102,
          "pacer_doc_id": "...",
          ...
        }
      ]
    }
  ]
}
```

### APPROACH 2: Search API with type=r (RECAP)
**URL Pattern:** `/api/rest/v3/search/` or `/api/rest/v4/search/`

**Key Advantages:**
- No special permission required for v4 search endpoint
- Returns dockets with nested child documents
- Elasticsearch-powered search
- No `has_recap_api_access` permission needed

**Permissions:** `V3APIPermission` only (no RECAP-specific permission)

**Example Query:**
```bash
# V4 Search with type=r (returns dockets with child docs)
GET /api/rest/v4/search/?q=test&type=r

# V3 Search
GET /api/rest/v3/search/?q=test&type=r
```

**Response Structure (v4 with type=r):**
```json
{
  "count": 10,
  "next": "...",
  "results": [
    {
      "id": 1,
      "docket_number": "...",
      "recap_documents": [
        {
          "id": 101,
          "description": "...",
          "meta": { "timestamp": "..." }
        }
      ],
      "meta": {
        "timestamp": "...",
        "score": { "bm25": 123.45 },
        "more_docs": true
      }
    }
  ]
}
```

### APPROACH 3: Search API with type=rd (RECAP Document)
**URL Pattern:** `/api/rest/v4/search/`

**Key Advantages:**
- Searches individual RECAP documents directly
- No special permission required
- Better for document-level searches

**Permissions:** `V3APIPermission` only

**Example Query:**
```bash
GET /api/rest/v4/search/?q=patent&type=rd
```

### APPROACH 4: Docket Endpoint with Nested Docket Entries Filter
**URL Pattern:** `/api/rest/v3/dockets/`

**Key Advantages:**
- Uses `DjangoModelPermissions` (more permissive than `RECAPUsersReadOnly`)
- Can filter by nested recap documents

**Permissions:** `DjangoModelPermissions` only (allows anonymous read)

**Example Query:**
```bash
# Get dockets with specific document tags
GET /api/rest/v3/dockets/?docket_entries__recap_documents__tags=1

# Filter by document ID
GET /api/rest/v3/dockets/?docket_entries__recap_documents__id=123
```

**Important Note:** The DocketSerializer does NOT include nested docket_entries by default. This endpoint returns docket metadata but not the actual documents.

## 3. Endpoint Comparison Table

| Endpoint | Method | Path | Permissions | Returns Documents | Notes |
|----------|--------|------|-------------|-------------------|-------|
| RECAPDocumentViewSet | GET | `/api/rest/v3/recap-documents/` | `has_recap_api_access` (403) | Yes, individual | Direct document access |
| DocketEntryViewSet | GET | `/api/rest/v3/docket-entries/` | `has_recap_api_access` | Yes, nested | Documents nested in entries |
| DocketViewSet | GET | `/api/rest/v3/dockets/` | `DjangoModelPermissions` | No | No document nesting |
| SearchViewSet (v3) | GET | `/api/rest/v3/search/` | `V3APIPermission` | Yes (ES) | Type=r/rd for RECAP |
| SearchV4ViewSet | GET | `/api/rest/v4/search/` | `V3APIPermission` | Yes (ES) | Type=r/rd for RECAP |

## 4. Available Filters

### RECAPDocumentFilter
**File:** `/home/user/courtlistener/cl/search/filters.py` (lines 212-233)

Available filter fields:
- `id` (exact, gte, gt, lte, lt, range)
- `date_created` (exact, gte, gt, lte, lt, range, year, month, day, hour, minute, second)
- `date_modified` (same as above)
- `date_upload` (same as above)
- `document_type` (exact)
- `document_number` (exact, gte, gt, lte, lt)
- `pacer_doc_id` (exact, in)
- `is_available` (exact)
- `sha1` (exact)
- `ocr_status` (numeric lookups)
- `is_free_on_pacer` (exact)
- `docket_entry` (related filter)
- `tags` (related filter)

### DocketEntryFilter
Supports nested filters like:
- `recap_documents__id`
- `recap_documents__tags`
- `recap_documents__docket_entry__docket__id`
- `docket__id`
- `docket__court__id`

## 5. V3 API Permission Blocking

### How V3APIPermission Works
**File:** `/home/user/courtlistener/cl/api/api_permissions.py`

For V3 API requests, the permission class:
1. Checks if user is anonymous → raises PermissionDenied
2. Checks if user is in v3-blocked-users-list → raises PermissionDenied
3. Checks 1 in 50 requests randomly
4. If new user (not in v3-users-list) → blocks request and adds to blocked list

**Resolution:** Use V4 API instead of V3, or add user to v3-users-list via Redis

## 6. Search API Parameters

### SEARCH_TYPES
**File:** `/home/user/courtlistener/cl/search/models.py` (lines 3733-3760)

```python
class SEARCH_TYPES:
    OPINION = "o"           # Opinion clusters
    RECAP = "r"             # Dockets with child documents
    DOCKETS = "d"           # RECAP Dockets
    RECAP_DOCUMENT = "rd"   # Individual RECAP documents
    ORAL_ARGUMENT = "oa"    # Oral arguments
    PEOPLE = "p"            # People/judges
    PARENTHETICAL = "pa"    # Parenthetical statements
```

### Search Query Parameters

**V4 Search Endpoint:** `/api/rest/v4/search/`

Common parameters:
- `q` - Search query (required unless using semantic search)
- `type` - Search type (o, r, d, rd, oa, p, pa)
- `court` - Court ID filter
- `filed_after` - Date filter (YYYY-MM-DD)
- `filed_before` - Date filter
- `semantic` - Enable semantic search (true/false)
- `page` - Page number for pagination
- `cursor` - Cursor for cursor-based pagination

Example:
```bash
GET /api/rest/v4/search/?q=patent&type=rd&filed_after=2020-01-01
```

## 7. Examples from Test Code

**File:** `/home/user/courtlistener/cl/api/tests.py`

### Setting up API Access (from tests)
```python
# Grant has_recap_api_access permission
up = UserProfileWithParentsFactory.create(
    user__username="recap-user",
    user__password=make_password("password"),
)
ps = Permission.objects.filter(codename="has_recap_api_access")
up.user.user_permissions.add(*ps)
```

### Accessing RECAP Documents via Docket Entries
```python
# Test line 1431-1434
self.q = {"docket_entry__id": 1}
await self.assertCountInResults(1)

# Test line 1402-1405 - Filter docket entries by document ID
self.q = {"recap_documents__id": 1}
await self.assertCountInResults(1)
```

### Accessing Documents via Dockets
```python
# Test line 1383-1386 - Filter dockets by document tags
path = reverse("docket-list", kwargs={"version": "v3"})
self.q = {"docket_entries__recap_documents__tags": 1}
await self.assertCountInResults(1)
```

## 8. Throttling and Rate Limiting

The API does NOT appear to have special throttling for RECAP documents. The 403 is purely permission-based.

Rate limiting may apply to V3 API under heavy usage, but:
- The blocking is random (1 in 50 requests)
- Affects new users to the V3 API
- Can be bypassed by using V4 API

## 9. Key Findings Summary

| Finding | Details |
|---------|---------|
| 403 Root Cause | `RECAPUsersReadOnly` permission requiring `has_recap_api_access` |
| Permission Required | `search.has_recap_api_access` on user account |
| How to Get Permission | Request it from administrators (custom permission) |
| Best Alternative (No Permission) | `/api/rest/v4/search/?type=r` or `?type=rd` |
| Best Alternative (With Permission) | `/api/rest/v3/docket-entries/?docket__id=X` |
| Recommended for Users | Use SearchV4ViewSet with `type=r` (no special permission needed) |
| Recommended for Admins | Grant `has_recap_api_access` permission to allow direct RECAP endpoint access |

## 10. Implementation Recommendations

### For Users Without has_recap_api_access Permission

**Use Search API (Recommended):**
```bash
# Get all documents for a docket via search
curl "https://api.courtlistener.com/api/rest/v4/search/?q=docket_number:1:20-cv-00123&type=rd"

# Or with docket-specific search
curl "https://api.courtlistener.com/api/rest/v4/search/?q=pacer_case_id:123456&type=r"
```

### For Users With has_recap_api_access Permission

**Option 1: Direct RECAP Documents (Most Direct)**
```bash
curl -H "Authorization: Token YOUR_TOKEN" \
  "https://api.courtlistener.com/api/rest/v3/recap-documents/?docket_entry__docket__id=123456"
```

**Option 2: Via Docket Entries (Returns Nested Documents)**
```bash
curl -H "Authorization: Token YOUR_TOKEN" \
  "https://api.courtlistener.com/api/rest/v3/docket-entries/?docket__id=123456"
```

### For Full Application Integration

```python
# Python example using requests
import requests

# Approach 1: Search API (no authentication needed for basic searches)
response = requests.get(
    "https://api.courtlistener.com/api/rest/v4/search/",
    params={
        "q": "docket_number:2024-cv-01234",
        "type": "rd",  # RECAP documents
    }
)
documents = response.json()["results"]

# Approach 2: Docket Entries (requires authentication and permission)
headers = {"Authorization": "Token YOUR_TOKEN"}
response = requests.get(
    "https://api.courtlistener.com/api/rest/v3/docket-entries/",
    headers=headers,
    params={"docket__id": 12345}
)
entries_with_docs = response.json()["results"]
# Each entry has a "recap_documents" array
for entry in entries_with_docs:
    for doc in entry["recap_documents"]:
        print(f"Document {doc['id']}: {doc['description']}")
```

## Files Referenced

1. **RECAPDocumentViewSet:** `/home/user/courtlistener/cl/search/api_views.py` (lines 182-206)
2. **RECAPUsersReadOnly:** `/home/user/courtlistener/cl/api/utils.py` (lines 747-762)
3. **V3APIPermission:** `/home/user/courtlistener/cl/api/api_permissions.py` (lines 22-97)
4. **DocketEntryViewSet:** `/home/user/courtlistener/cl/search/api_views.py` (lines 144-179)
5. **DocketEntrySerializer:** `/home/user/courtlistener/cl/search/api_serializers.py` (lines 171-186)
6. **RECAPDocumentFilter:** `/home/user/courtlistener/cl/search/filters.py` (lines 212-233)
7. **SEARCH_TYPES:** `/home/user/courtlistener/cl/search/models.py` (lines 3733-3760)
8. **URL Routes:** `/home/user/courtlistener/cl/api/urls.py` (lines 19-31)
9. **API Tests:** `/home/user/courtlistener/cl/api/tests.py` (various test methods)
