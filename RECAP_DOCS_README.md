# RECAP 403 Error Investigation - Complete Documentation

This directory contains comprehensive documentation for understanding and resolving the 403 Forbidden error when accessing the `/recap-documents/` API endpoint on CourtListener.

## Documents Included

### 1. [RECAP_403_INVESTIGATION.md](RECAP_403_INVESTIGATION.md) - **START HERE**
**The comprehensive investigation report**

- **Root cause analysis** of the 403 error
- **Permission requirements** explained
- **All available alternative endpoints** with detailed comparisons
- **Filter options** for each endpoint
- **V3/V4 API differences** 
- **Throttling and rate limiting** information
- **Test examples** from the codebase

**Size:** 404 lines | **Best for:** Understanding the problem deeply

### 2. [RECAP_ACCESS_FLOW.md](RECAP_ACCESS_FLOW.md) - **VISUAL REFERENCE**
**Visual diagrams and decision trees**

- **Permission hierarchy diagram** showing how requests are evaluated
- **Alternative access paths** (3 different options)
- **Permission class comparison matrix**
- **Endpoint permission matrix** table
- **Decision tree** for choosing the right approach
- **Quick reference curl commands**

**Size:** 230 lines | **Best for:** Quick visual understanding

### 3. [RECAP_SOLUTIONS_GUIDE.md](RECAP_SOLUTIONS_GUIDE.md) - **IMPLEMENTATION**
**Practical code examples and solutions**

- **3 complete solutions** with pros/cons
- **Working Python code examples** for each approach
- **Troubleshooting guide** with error solutions
- **Performance comparisons**
- **Complete bulk document retrieval example** class
- **API reference summary**

**Size:** 648 lines | **Best for:** Implementing a solution

---

## Quick Start Guide

### If You Don't Have Special Permissions (Most Users)

**Use the Search API** - No authentication required:

```bash
curl "https://api.courtlistener.com/api/rest/v4/search/?q=docket_id:123456&type=r"
```

**Why:** Works without any special permission, fast Elasticsearch-powered, returns dockets with nested documents.

**See:** [RECAP_SOLUTIONS_GUIDE.md - Solution 1](RECAP_SOLUTIONS_GUIDE.md#solution-1-search-api-recommended-for-public-access)

---

### If You Have Special Permissions

**Use the Docket Entries Endpoint:**

```bash
curl -H "Authorization: Token YOUR_TOKEN" \
  "https://api.courtlistener.com/api/rest/v3/docket-entries/?docket__id=123456"
```

**Why:** Returns documents nested within docket entries, optimized queries, same permission as direct endpoint.

**See:** [RECAP_SOLUTIONS_GUIDE.md - Solution 3](RECAP_SOLUTIONS_GUIDE.md#solution-3-docket-entries-endpoint)

---

### If You're an Administrator

**Grant the has_recap_api_access Permission:**

```python
from django.contrib.auth.models import User, Permission
user = User.objects.get(username='your_username')
permission = Permission.objects.get(codename='has_recap_api_access')
user.user_permissions.add(permission)
```

**See:** [RECAP_SOLUTIONS_GUIDE.md - Solution 2](RECAP_SOLUTIONS_GUIDE.md#solution-2-grant-has_recap_api_access-permission-admin-only)

---

## The Problem in 30 Seconds

The `/recap-documents/` endpoint has a **permission gate**:

```
GET /api/rest/v3/recap-documents/ 
    ↓
Check: Does user have "has_recap_api_access" permission?
    ↓
NO → 403 FORBIDDEN
YES → 200 OK with documents
```

This is **intentional** - the RECAP API is restricted to users with special access.

---

## The Solutions at a Glance

| Solution | Code | Permission | Best For | Speed |
|----------|------|-----------|----------|-------|
| Search API | `type=r` or `type=rd` | None | Public access, searches | Very Fast (ES) |
| Docket Entries | `/docket-entries/` | has_recap_api_access | Nested documents | Medium (DB) |
| Direct Endpoint | `/recap-documents/` | has_recap_api_access | Individual items | Medium (DB) |

---

## File Reference for Developers

### Key Files Referenced in Investigation

**Permission Classes:**
- `/home/user/courtlistener/cl/api/utils.py` - `RECAPUsersReadOnly` class (line 747)
- `/home/user/courtlistener/cl/api/api_permissions.py` - `V3APIPermission` class (line 22)

**ViewSets:**
- `/home/user/courtlistener/cl/search/api_views.py` - `RECAPDocumentViewSet` (line 182)
- `/home/user/courtlistener/cl/search/api_views.py` - `DocketEntryViewSet` (line 144)
- `/home/user/courtlistener/cl/search/api_views.py` - `SearchV4ViewSet` (line 415)

**Serializers:**
- `/home/user/courtlistener/cl/search/api_serializers.py` - `RECAPDocumentSerializer` (line 151)
- `/home/user/courtlistener/cl/search/api_serializers.py` - `DocketEntrySerializer` (line 171)

**Filters:**
- `/home/user/courtlistener/cl/search/filters.py` - `RECAPDocumentFilter` (line 212)

**Tests:**
- `/home/user/courtlistener/cl/api/tests.py` - API tests showing permission setup

**URL Routes:**
- `/home/user/courtlistener/cl/api/urls.py` - Endpoint configuration

---

## Reading Order Recommendation

### For Quick Solution (5 min)
1. Read this README
2. Look at the relevant solution in [RECAP_SOLUTIONS_GUIDE.md](RECAP_SOLUTIONS_GUIDE.md)
3. Copy the code example
4. Done!

### For Understanding (15 min)
1. Read [RECAP_403_INVESTIGATION.md](RECAP_403_INVESTIGATION.md) - Executive Summary section
2. Look at [RECAP_ACCESS_FLOW.md](RECAP_ACCESS_FLOW.md) - Decision Tree
3. Choose your approach from [RECAP_SOLUTIONS_GUIDE.md](RECAP_SOLUTIONS_GUIDE.md)

### For Deep Dive (30+ min)
1. Read [RECAP_403_INVESTIGATION.md](RECAP_403_INVESTIGATION.md) - All sections
2. Review [RECAP_ACCESS_FLOW.md](RECAP_ACCESS_FLOW.md) - All diagrams
3. Study [RECAP_SOLUTIONS_GUIDE.md](RECAP_SOLUTIONS_GUIDE.md) - All solutions
4. Review the referenced source files

---

## Key Findings Summary

**Root Cause:** 
The RECAPDocumentViewSet uses `RECAPUsersReadOnly` permission class which requires the `search.has_recap_api_access` permission for GET requests.

**Best Workaround:** 
Use the Search API (`/api/rest/v4/search/?type=r` or `?type=rd`) which requires no special permissions.

**Alternative Approaches:**
1. Grant the permission via Django admin (requires admin access)
2. Use the Docket Entries endpoint instead (same permission requirement)
3. Use the public Search API (no permissions needed)

**No Rate Limiting:** The 403 is purely permission-based, not rate limiting.

---

## Common Questions

**Q: Why is the endpoint restricted?**
A: To manage API load and provide better service to authorized users.

**Q: Can I get the permission?**
A: Contact the CourtListener administrators to request `has_recap_api_access` permission.

**Q: Do I need the permission?**
A: No - you can use the public Search API to access documents without special permissions.

**Q: Which approach is fastest?**
A: Search API (Elasticsearch) is fastest but less precise. Direct endpoint is slower but more accurate.

**Q: Does it have throttling?**
A: No, the 403 is permission-based. Throttling may apply separately to all API requests.

---

## Related Resources

- CourtListener API Documentation: https://api.courtlistener.com/help/api/
- GitHub Repository: https://github.com/freelawproject/courtlistener/
- API Terms of Use: https://www.courtlistener.com/api/

---

## Document Statistics

| Document | Size | Lines | Topics |
|----------|------|-------|--------|
| RECAP_403_INVESTIGATION.md | 13 KB | 404 | In-depth analysis |
| RECAP_ACCESS_FLOW.md | 17 KB | 230 | Visual diagrams |
| RECAP_SOLUTIONS_GUIDE.md | 17 KB | 648 | Code examples |
| **Total** | **47 KB** | **1,282** | Complete guide |

---

## Version Info

- **Created:** 2025-11-06
- **Branch:** claude/document-django-rest-api
- **Investigation Scope:** Very thorough
- **Code Coverage:** Permissions, ViewSets, Serializers, Filters, Tests

---

## Feedback

These documents were generated through thorough investigation of the CourtListener codebase. For questions or corrections, refer to the source files listed in each document.

