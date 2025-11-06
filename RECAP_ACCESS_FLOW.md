# RECAP Documents Access Flow Diagram

## Permission Hierarchy

```
┌─────────────────────────────────────────────────────────────────┐
│                    API Request to Endpoint                       │
└────────────────────────────┬────────────────────────────────────┘
                             │
                   ┌─────────▼─────────┐
                   │  Which Endpoint?  │
                   └─────────┬─────────┘
                             │
         ┌───────────────────┼───────────────────┬─────────────────┐
         │                   │                   │                 │
    ┌────▼────┐         ┌────▼────┐        ┌────▼────┐        ┌──▼─────┐
    │/recap-  │         │/docket- │        │/docket- │        │/search │
    │documents │        │entries   │        │s         │        │        │
    └────┬────┘         └────┬────┘        └────┬────┘        └──┬─────┘
         │                   │                   │                 │
         │               ┌───▼───┐           ┌───▼───┐         ┌──▼────┐
         │               │  REP  │           │ DjangoModel   │V3/V4   │
         │               │Users  │           │PermissionsOr │APIOnly │
         │               │ReadOnly           │AnonReadOnly  │        │
         └───┬───┐       └───┬───┘           └───┬───┘       └──┬────┘
             │   │           │                   │              │
             │   │           │                   │              │
         ┌───▼───▼───┐  ┌────▼────┐         ┌───▼────┐       ┌─▼──┐
         │has_recap  │  │Anonymous│         │Anonymous└─────►│✓OK │
         │_api_access│  │Block V3 │         │  Allowed        └────┘
         └───┬───────┘  └────┬────┘         └────┬────┘
             │               │                   │
          ┌──▼──┐          ┌─▼──┐            ┌──▼──┐
          │ 403  │          │ 403 │           │✓ OK  │
          │DENIED           └─────┘           └─────┘
          └──────┘
```

## Alternative Access Paths to RECAP Documents

```
Goal: Get all documents for Docket ID 123456

┌─────────────────────────────────────────────────────────────────┐
│                                                                 │
│  Option A: Search API (No special permission needed)            │
│  ─────────────────────────────────────────────────────────────  │
│                                                                 │
│  /api/rest/v4/search/?q=docket_id:123456&type=r               │
│                    ↓                                             │
│  Returns dockets with nested recap_documents array              │
│  (Elasticsearch-powered)                                        │
│                    ↓                                             │
│  [✓ Works without has_recap_api_access]                        │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                                                                 │
│  Option B: Docket Entries (Requires has_recap_api_access)      │
│  ─────────────────────────────────────────────────────────────  │
│                                                                 │
│  /api/rest/v3/docket-entries/?docket__id=123456               │
│                    ↓                                             │
│  Returns entries with nested recap_documents array              │
│  (Direct database query with optimization)                      │
│                    ↓                                             │
│  [Requires: has_recap_api_access permission]                   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                                                                 │
│  Option C: Direct RECAP Documents (Requires has_recap_api_access)
│  ──────────────────────────────────────────────────────────────  │
│                                                                 │
│  /api/rest/v3/recap-documents/?docket_entry__docket__id=123456│
│                    ↓                                             │
│  Returns individual documents (paginated)                       │
│                    ↓                                             │
│  [Requires: has_recap_api_access permission] [403 ERROR]      │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

## Permission Classes Comparison

```
┌──────────────────────────────────────────────────────────────────┐
│ RECAPUsersReadOnly (extends DjangoModelPermissions)              │
├──────────────────────────────────────────────────────────────────┤
│ GET/OPTIONS/HEAD → Requires: search.has_recap_api_access         │
│ POST/PUT/PATCH   → Requires: add_/change_ permissions            │
│ DELETE           → Requires: delete_ permission                  │
└──────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────┐
│ DjangoModelPermissions                                           │
├──────────────────────────────────────────────────────────────────┤
│ GET/OPTIONS/HEAD → Requires: view_ permission (or anonymous)     │
│ POST/PUT/PATCH   → Requires: add_/change_ permissions            │
│ DELETE           → Requires: delete_ permission                  │
└──────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────┐
│ V3APIPermission (Additional layer for V3 API only)              │
├──────────────────────────────────────────────────────────────────┤
│ Anonymous users  → BLOCKED (403) for V3                          │
│ New users (to V3) → BLOCKED randomly (1 in 50 requests)         │
│ V4 API requests  → ALLOWED (bypassed)                            │
│                                                                  │
│ Resolution: Use V4 API or request to be added to v3-users-list  │
└──────────────────────────────────────────────────────────────────┘
```

## Endpoint Permission Matrix

```
┌─────────────────────┬──────────────────────┬─────────────────┬──────────┐
│ Endpoint            │ Permission Classes   │ Nested Docs?    │ API Ver  │
├─────────────────────┼──────────────────────┼─────────────────┼──────────┤
│ /recap-documents/   │ RECAPUsersReadOnly   │ No (individual) │ v3/v4    │
│                     │ + V3APIPermission    │ items           │          │
├─────────────────────┼──────────────────────┼─────────────────┼──────────┤
│ /docket-entries/    │ RECAPUsersReadOnly   │ Yes (nested in  │ v3/v4    │
│                     │ + V3APIPermission    │ recap_documents)│          │
├─────────────────────┼──────────────────────┼─────────────────┼──────────┤
│ /dockets/           │ DjangoModelPermissions│ No (no nesting) │ v3/v4    │
│                     │ + V3APIPermission    │                 │          │
├─────────────────────┼──────────────────────┼─────────────────┼──────────┤
│ /search/            │ AllowAny + V3API Perm│ Yes (ES results)│ v3 only  │
│                     │                      │ with metadata   │          │
├─────────────────────┼──────────────────────┼─────────────────┼──────────┤
│ /search/ (v4)       │ AllowAny             │ Yes (ES results)│ v4 only  │
│                     │                      │ with metadata   │          │
└─────────────────────┴──────────────────────┴─────────────────┴──────────┘
```

## Decision Tree: Which Endpoint Should You Use?

```
                    START: Need RECAP Documents?
                              │
                    ┌─────────┴─────────┐
                    │                   │
               Do you have        Do you NOT have
           has_recap_api_access?  permission?
                    │                   │
                   YES                  NO
                    │                   │
         ┌──────────▼──────────┐   ┌───▼──────────┐
         │ Which is preferred? │   │ Use Search   │
         └──────────┬──────────┘   │ API (type=r  │
                    │              │ or type=rd)  │
         ┌──────────┴─────────┐    │              │
         │                    │    └───┬──────────┘
         │                    │        │
    Nested docs        Individual docs │
    (with entries)?    (paged)?        │
         │                    │        │
         │                    │        │
    ┌────▼──┐        ┌─────────▼──┐   │
    │Use    │        │Use /recap- │   │
    │/docket        │documents/  │   │
    │-entries/      └────────┬───┘   │
    │                        │       │
    └────┬──┐          ┌──────▼─┐   │
         │  │          │Query   │   │
         │  │          │with    │   │
         │  └────┬─────┤filter: │   │
         │       │     │docket_ │   │
         │  ┌────▼─────┤entry__ │   │
         │  │           │docket__id  │
         │  │           └────┬───┘   │
         │  │                │       │
    ┌────▼──▼──┐    ┌────────▼──┐  │
    │Result ✓  │    │Result ✓   │  │
    │Docket    │    │Documents  │  │
    │Entries   │    │List       │  │
    │with Docs │    └───────┬───┘  │
    └──────────┘            │      │
                            │      │
                   ┌────────▼──────┘
                   │
              ┌────▼──────┐
              │Final      │
              │Result ✓   │
              │Documents! │
              └───────────┘
```

## Quick Reference: API Calls

```bash
# =============================================================================
# NO PERMISSION REQUIRED - Public Search API
# =============================================================================

# Search for documents by keyword
curl "https://api.courtlistener.com/api/rest/v4/search/?q=patent&type=rd"

# Search by docket ID
curl "https://api.courtlistener.com/api/rest/v4/search/?q=docket_id:123456&type=r"

# With date filtering
curl "https://api.courtlistener.com/api/rest/v4/search/?q=test&type=rd&filed_after=2020-01-01"


# =============================================================================
# REQUIRES: has_recap_api_access Permission
# =============================================================================

# Get docket entries (with nested documents)
TOKEN="your_api_token_here"
curl -H "Authorization: Token $TOKEN" \
  "https://api.courtlistener.com/api/rest/v3/docket-entries/?docket__id=123456"

# Get documents directly
curl -H "Authorization: Token $TOKEN" \
  "https://api.courtlistener.com/api/rest/v3/recap-documents/?docket_entry__docket__id=123456"

# Filter documents by tag
curl -H "Authorization: Token $TOKEN" \
  "https://api.courtlistener.com/api/rest/v3/recap-documents/?tags=1"

# Filter by PACER document ID
curl -H "Authorization: Token $TOKEN" \
  "https://api.courtlistener.com/api/rest/v3/recap-documents/?pacer_doc_id=123456789"
```

