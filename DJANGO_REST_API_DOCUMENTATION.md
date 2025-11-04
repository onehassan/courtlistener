# CourtListener Django REST API Documentation

## Table of Contents

1. [Overview](#overview)
2. [Authentication](#authentication)
3. [Base URL and Versioning](#base-url-and-versioning)
4. [Rate Limiting](#rate-limiting)
5. [Pagination](#pagination)
6. [Filtering and Ordering](#filtering-and-ordering)
7. [Response Formats](#response-formats)
8. [Available Endpoints](#available-endpoints)
   - [Search & Case Law](#search--case-law)
   - [People & Entities](#people--entities)
   - [Audio (Oral Arguments)](#audio-oral-arguments)
   - [Alerts](#alerts)
   - [Financial Disclosures](#financial-disclosures)
   - [RECAP/PACER](#recappacer)
   - [Tags and Favorites](#tags-and-favorites)
   - [Visualizations](#visualizations)
   - [Citations](#citations)
   - [Webhooks](#webhooks)
9. [Error Handling](#error-handling)
10. [Examples](#examples)

---

## Overview

The CourtListener Django REST API provides programmatic access to a comprehensive database of legal information including:
- Court opinions and case law
- Federal court dockets (PACER/RECAP data)
- Oral argument audio recordings
- Judicial biographical information
- Financial disclosure data
- Citation lookups and relationships

The API is built using Django REST Framework and supports both JSON and XML response formats.

### API Title
**CourtListener Legal Data API**

### Key Features
- RESTful architecture
- Multiple authentication methods
- Advanced filtering and search capabilities
- Elasticsearch-powered full-text search
- Cursor and page-based pagination
- Rate limiting with user-specific overrides
- Real-time webhooks for data updates
- Comprehensive coverage of U.S. federal and state courts

---

## Authentication

The API supports three authentication methods:

### 1. Token Authentication (Recommended)
Use an API token in the Authorization header:
```http
Authorization: Token YOUR_API_TOKEN
```

To obtain a token, create an account on CourtListener and navigate to your profile settings.

### 2. Basic Authentication
Use HTTP Basic Authentication with your username and password:
```http
Authorization: Basic base64(username:password)
```

### 3. Session Authentication
Use Django session authentication (primarily for browsable API).

### Anonymous Access
Unauthenticated requests are allowed but with significantly lower rate limits (read-only access for most endpoints).

---

## Base URL and Versioning

### Base URL Structure
```
https://www.courtlistener.com/api/rest/{version}/
```

### Supported Versions

#### V4 (Current - Recommended)
```
https://www.courtlistener.com/api/rest/v4/
```
- Enhanced search capabilities with Elasticsearch
- Cursor pagination support for efficient large dataset access
- Improved performance
- All V3 endpoints plus SearchV4

#### V3 (Legacy - Being Deprecated)
```
https://www.courtlistener.com/api/rest/v3/
```
- Maintained for backward compatibility
- New users are blocked from V3 access (set via `BLOCK_NEW_V3_USERS` configuration)
- Uses legacy search implementation

### Version Migration
When V3 is fully deprecated:
- Only `SearchViewSet` needs removal
- V4 becomes the default version
- See migration guide at: `/help/api/rest/v4/migration-guide/`

---

## Rate Limiting

### Default Throttle Rates

| User Type | Rate Limit | Notes |
|-----------|------------|-------|
| **Anonymous** | 100 requests/day | 10,000/day in development mode |
| **Authenticated** | 5,000 requests/hour | Standard authenticated users |
| **Citation Lookup** | 60 requests/minute | Special endpoint throttling |

### Throttle Classes
- `AnonRateThrottle` - Anonymous user throttling
- `ExceptionalUserRateThrottle` - Custom per-user throttling
- `CitationCountRateThrottle` - Citation lookup specific throttling

### User-Specific Overrides
The API supports custom rate limits for specific users (see `OVERRIDE_THROTTLE_RATES` in configuration).

Examples of elevated limits:
- Research institutions: Up to 430,000 requests/day
- High-volume litigation monitoring: Up to 500,000 requests/hour
- Benchmark testing: Up to 1,000,000 requests/hour

### Throttle Headers
Rate limit information is included in response headers:
```http
X-RateLimit-Limit: 5000
X-RateLimit-Remaining: 4995
X-RateLimit-Reset: 1635789600
```

---

## Pagination

The API supports two pagination strategies based on version and use case.

### Page Number Pagination (V3 and V4)

**Default Settings:**
- Default page size: 20 items
- Maximum pagination depth: 100 pages
- Configurable via `page_size` query parameter

**Query Parameters:**
```
?page=2                  # Page number
?page_size=50           # Items per page
```

**Response Format:**
```json
{
  "count": 1000,
  "next": "https://www.courtlistener.com/api/rest/v4/dockets/?page=3",
  "previous": "https://www.courtlistener.com/api/rest/v4/dockets/?page=1",
  "results": [...]
}
```

**Pagination Classes:**
- `VersionBasedPagination` - Main hybrid paginator (default)
- `TinyAdjustablePagination` - 5 items/page, adjustable up to 20
- `MediumAdjustablePagination` - 50 items/page
- `BigPagination` - 300 items/page

**Pagination Depth Limit:**
Deep pagination (beyond page 100) is blocked to prevent expensive database queries.

### Cursor Pagination (V4 Only)

**When Available:**
Cursor pagination is used automatically in V4 when sorting by:
- `id` or `-id`
- `date_created` or `-date_created`
- `date_modified` or `-date_modified`
- `date_completed` or `-date_completed`

**Benefits:**
- More efficient for large datasets
- Consistent results even with data changes
- No pagination depth limits
- Better performance

**Query Parameters:**
```
?cursor=cD0yMDIx...    # Base64-encoded cursor token
?order_by=id           # Must use cursor-compatible sorting
```

**Response Format:**
```json
{
  "count": "https://www.courtlistener.com/api/rest/v4/dockets/?count=on",
  "next": "https://www.courtlistener.com/api/rest/v4/dockets/?cursor=cD0yMDIx...",
  "previous": "https://www.courtlistener.com/api/rest/v4/dockets/?cursor=cj0xMjM0...",
  "results": [...]
}
```

**Count Request:**
To get total count without results:
```
?count=on
```

Response:
```json
{
  "count": 1000
}
```

### Elasticsearch Cursor Pagination

Used for full-text search endpoints with special handling:
- Base64-encoded cursor with search_after parameters
- Supports forward and backward pagination
- Includes approximate count for large result sets
- Caches results for consistent pagination

---

## Filtering and Ordering

### Filtering

All list endpoints support extensive filtering via query parameters.

**Filter Syntax:**
```
?field=value                    # Exact match
?field__iexact=value           # Case-insensitive exact match
?field__contains=value         # Contains substring
?field__icontains=value        # Case-insensitive contains
?field__startswith=value       # Starts with
?field__endswith=value         # Ends with
?field__gt=value               # Greater than
?field__gte=value              # Greater than or equal
?field__lt=value               # Less than
?field__lte=value              # Less than or equal
?field__range=min,max          # Range (inclusive)
```

**Date Filtering:**
```
?date_filed__gte=2020-01-01
?date_filed__lt=2021-01-01
?date_filed__year=2020
?date_filed__month=12
?date_filed__day=25
```

**Relationship Filtering:**
```
?docket__court=ca9             # Filter by related court
?cluster__judges=123           # Filter by judge ID
```

**Multiple Values (OR):**
```
?court=ca9&court=ca2           # Court is ca9 OR ca2
```

### Ordering

**Query Parameter:**
```
?order_by=field_name           # Ascending
?order_by=-field_name          # Descending
```

**Multiple Fields:**
```
?order_by=date_filed,-id       # Sort by date_filed, then by id descending
```

**Common Sortable Fields:**
- `id`, `date_created`, `date_modified`
- `date_filed`, `date_argued`, `date_reargued`, `date_reargument_denied`
- `name`, `docket_number`, `case_name`

### Field Selection

Reduce payload size by selecting specific fields:
```
?fields=id,case_name,date_filed
```

---

## Response Formats

### Supported Formats

1. **JSON (Default)**
   - Content-Type: `application/json`
   - Append `?format=json` or use `Accept: application/json` header

2. **XML**
   - Content-Type: `application/xml`
   - Append `?format=xml` or use `Accept: application/xml` header
   - Uses SafeXMLRenderer to handle malformed data

3. **Browsable API**
   - Interactive HTML interface for exploring the API
   - Available when accessing endpoints in a web browser

### Content Negotiation

Via query parameter:
```
https://www.courtlistener.com/api/rest/v4/dockets/?format=json
```

Via Accept header:
```http
Accept: application/json
Accept: application/xml
```

---

## Available Endpoints

### Search & Case Law

All endpoints prefixed with `/api/rest/v4/`

| Endpoint | ViewSet | Methods | Description |
|----------|---------|---------|-------------|
| `/courts/` | `CourtViewSet` | GET, OPTIONS | List of courts and jurisdictions |
| `/dockets/` | `DocketViewSet` | GET, POST, PUT, PATCH, DELETE | Case dockets and metadata |
| `/docket-entries/` | `DocketEntryViewSet` | GET, POST, PUT, PATCH, DELETE | Individual docket entries/filings |
| `/recap-documents/` | `RECAPDocumentViewSet` | GET, POST, PUT, PATCH, DELETE | PACER documents from RECAP |
| `/originating-court-information/` | `OriginatingCourtInformationViewSet` | GET, POST, PUT, PATCH, DELETE | Original jurisdiction information |
| `/clusters/` | `OpinionClusterViewSet` | GET, POST, PUT, PATCH, DELETE | Opinion clusters (grouped opinions) |
| `/opinions/` | `OpinionViewSet` | GET, POST, PUT, PATCH, DELETE | Individual court opinions |
| `/opinions-cited/` | `OpinionsCitedViewSet` | GET, POST, PUT, PATCH, DELETE | Citation relationships between opinions |
| `/tag/` | `TagViewSet` | GET, POST, PUT, PATCH, DELETE | Tags for RECAP documents |
| `/search/` | `SearchV4ViewSet` (V4) | GET | Full-text search with Elasticsearch |
| `/search/` | `SearchViewSet` (V3) | GET | Legacy full-text search |

#### Court Model Fields
- `id` - Court identifier (e.g., "scotus", "ca9")
- `full_name` - Full court name
- `short_name` - Abbreviated name
- `jurisdiction` - Federal/State/Bankruptcy, etc.
- `position` - Hierarchical position
- `citation_string` - Citation abbreviation
- `in_use` - Whether court is currently active

#### Docket Model Key Fields
- `id` - Unique identifier
- `source` - Data source (RECAP, scraper, etc.)
- `court` - Related court ID
- `date_filed` - Filing date
- `date_last_filing` - Most recent filing
- `docket_number` - Court docket number
- `case_name` - Full case name
- `case_name_short` - Abbreviated case name
- `slug` - URL-friendly identifier
- `nature_of_suit` - Case type/category
- `cause` - Legal cause of action
- `jury_demand` - Jury demand information
- `pacer_case_id` - PACER identifier

#### Opinion Model Key Fields
- `id` - Unique identifier
- `cluster` - Related opinion cluster
- `type` - Opinion type (Lead, Concurrence, Dissent, etc.)
- `author` - Judge author
- `joined_by` - Joining judges
- `plain_text` - Full text content
- `html` - HTML formatted text
- `html_with_citations` - HTML with citation links
- `extracted_by_ocr` - OCR flag
- `per_curiam` - Per curiam opinion flag
- `download_url` - Source document URL

---

### People & Entities

| Endpoint | ViewSet | Methods | Description |
|----------|---------|---------|-------------|
| `/people/` | `PersonViewSet` | GET, POST, PUT, PATCH, DELETE | Judges and attorneys |
| `/positions/` | `PositionViewSet` | GET, POST, PUT, PATCH, DELETE | Judicial and attorney positions |
| `/retention-events/` | `RetentionEventViewSet` | GET, POST, PUT, PATCH, DELETE | Judicial retention events |
| `/educations/` | `EducationViewSet` | GET, POST, PUT, PATCH, DELETE | Educational background |
| `/schools/` | `SchoolViewSet` | GET, POST, PUT, PATCH, DELETE | Educational institutions |
| `/political-affiliations/` | `PoliticalAffiliationViewSet` | GET, POST, PUT, PATCH, DELETE | Political party affiliations |
| `/sources/` | `SourceViewSet` | GET, POST, PUT, PATCH, DELETE | Data sources |
| `/aba-ratings/` | `ABARatingViewSet` | GET, POST, PUT, PATCH, DELETE | American Bar Association ratings |
| `/parties/` | `PartyViewSet` | GET, POST, PUT, PATCH, DELETE | Litigation parties |
| `/attorneys/` | `AttorneyViewSet` | GET, POST, PUT, PATCH, DELETE | Attorney information |
| `/disclosure-typeahead/` | `PersonDisclosureViewSet` | GET | Quick lookup for disclosure subjects |

#### Person Model Key Fields
- `id` - Unique identifier
- `name_first`, `name_middle`, `name_last`, `name_suffix` - Name components
- `date_dob` - Date of birth
- `date_dod` - Date of death
- `gender` - Gender
- `religion` - Religion
- `ftm_total_received` - Follow The Money total contributions
- `has_photo` - Photo availability flag

#### Position Model Key Fields
- `id` - Unique identifier
- `person` - Related person ID
- `court` - Related court ID
- `position_type` - Judge, Attorney, etc.
- `appointer` - Appointing authority
- `date_nominated`, `date_elected`, `date_recess_appointment` - Appointment dates
- `date_start`, `date_termination`, `date_retirement` - Service dates
- `termination_reason` - Reason for leaving position
- `how_selected` - Selection method (Appointment, Election, etc.)

---

### Audio (Oral Arguments)

| Endpoint | ViewSet | Methods | Description |
|----------|---------|---------|-------------|
| `/audio/` | `AudioViewSet` | GET, POST, PUT, PATCH, DELETE | Oral argument audio recordings |

#### Audio Model Key Fields
- `id` - Unique identifier
- `docket` - Related docket
- `source` - Audio source
- `case_name` - Case name
- `case_name_short` - Short case name
- `judges` - Judges present
- `date_created`, `date_modified` - Timestamps
- `sha1` - File hash
- `download_url` - Audio file URL
- `local_path_mp3` - MP3 file path
- `local_path_original_file` - Original file path
- `duration` - Audio duration in seconds
- `processing_complete` - Processing status

---

### Alerts

| Endpoint | ViewSet | Methods | Description |
|----------|---------|---------|-------------|
| `/alerts/` | `SearchAlertViewSet` | GET, POST, PUT, PATCH, DELETE | User-created search alerts |
| `/docket-alerts/` | `DocketAlertViewSet` | GET, POST, PUT, PATCH, DELETE | Case activity alerts |

#### Search Alert Key Fields
- `id` - Unique identifier
- `user` - Alert owner
- `name` - Alert name
- `query` - Search query string
- `rate` - Notification frequency (Real-time, Daily, Weekly, Monthly)
- `alert_type` - Type of content (Search, Citation)

#### Docket Alert Key Fields
- `id` - Unique identifier
- `user` - Alert owner
- `docket` - Monitored docket
- `date_created`, `date_modified` - Timestamps
- `alert_type` - Type of alert (Subscription, Unsubscription)

**Permissions:** Users can only access and modify their own alerts.

---

### Financial Disclosures

| Endpoint | ViewSet | Methods | Description |
|----------|---------|---------|-------------|
| `/financial-disclosures/` | `FinancialDisclosureViewSet` | GET, POST, PUT, PATCH, DELETE | Judge financial disclosures |
| `/agreements/` | `AgreementViewSet` | GET, POST, PUT, PATCH, DELETE | Agreements from filings |
| `/debts/` | `DebtViewSet` | GET, POST, PUT, PATCH, DELETE | Reported debts |
| `/gifts/` | `GiftViewSet` | GET, POST, PUT, PATCH, DELETE | Gifts received |
| `/investments/` | `InvestmentViewSet` | GET, POST, PUT, PATCH, DELETE | Investment holdings |
| `/non-investment-incomes/` | `NonInvestmentIncomeViewSet` | GET, POST, PUT, PATCH, DELETE | Other income sources |
| `/reimbursements/` | `ReimbursementViewSet` | GET, POST, PUT, PATCH, DELETE | Travel reimbursements |
| `/spouse-incomes/` | `SpouseIncomeViewSet` | GET, POST, PUT, PATCH, DELETE | Spouse income |
| `/disclosure-positions/` | `PositionViewSet` | GET, POST, PUT, PATCH, DELETE | Positions from disclosures |

#### Financial Disclosure Key Fields
- `id` - Unique identifier
- `person` - Related person/judge
- `year` - Reporting year
- `download_filepath` - PDF file path
- `filepath` - Processed file path
- `thumbnail` - Thumbnail image
- `page_count` - Number of pages
- `sha1` - File hash
- `report_type` - Type of disclosure report
- `is_amended` - Amendment flag
- `addendum_content_raw` - Raw addendum text
- `addendum_redacted` - Redaction flag

---

### RECAP/PACER

| Endpoint | ViewSet | Methods | Description |
|----------|---------|---------|-------------|
| `/recap/` | `PacerProcessingQueueViewSet` | POST | Upload PACER documents |
| `/recap-email/` | `EmailProcessingQueueViewSet` | POST | Email-based PACER submissions |
| `/recap-fetch/` | `PacerFetchRequestViewSet` | GET, POST | Request PACER document fetches |
| `/recap-query/` | `PacerDocIdLookupViewSet` | GET | Fast RECAP document lookup |
| `/fjc-integrated-database/` | `FjcIntegratedDatabaseViewSet` | GET | Federal Judicial Center data |

#### RECAP Processing Queue
Upload PACER documents for processing and integration into CourtListener.

**Required Fields:**
- `court` - Court identifier
- `upload_type` - Type of upload (PDF, docket, etc.)
- `document` - File upload

**Permissions:** Special RECAP user permissions required for some operations.

#### PACER Fetch Request
Request fetching of documents from PACER.

**Key Fields:**
- `court` - Target court
- `pacer_case_id` - PACER case identifier
- `docket_number` - Docket number
- `request_type` - Type of fetch request

---

### Tags and Favorites

| Endpoint | ViewSet | Methods | Description |
|----------|---------|---------|-------------|
| `/tags/` | `UserTagViewSet` | GET, POST, PUT, PATCH, DELETE | User-created custom tags |
| `/docket-tags/` | `DocketTagViewSet` | GET, POST, PUT, PATCH, DELETE | Tags applied to dockets |
| `/prayers/` | `PrayerViewSet` | GET, POST, PUT, PATCH, DELETE | Saved case alerts/prayers (legacy) |
| `/increment-event/` | `EventCounterViewset` | POST | Track usage events |

#### User Tag Key Fields
- `id` - Unique identifier
- `user` - Tag owner
- `name` - Tag name
- `title` - Display title
- `description` - Tag description
- `published` - Public visibility flag

#### Docket Tag Key Fields
- `id` - Unique identifier
- `docket` - Tagged docket
- `tag` - Applied tag

**Permissions:** Users can only access and modify their own tags (`IsTagOwner` permission).

---

### Visualizations

| Endpoint | ViewSet | Methods | Description |
|----------|---------|---------|-------------|
| `/visualizations/` | `VisualizationViewSet` | GET, POST, PUT, PATCH, DELETE | SCOTUS citation network visualizations |
| `/visualizations/json/` | `JSONViewSet` | GET | JSON versions of visualizations |

#### Visualization Key Fields
- `id` - Unique identifier
- `user` - Visualization owner
- `cluster_start` - Starting opinion cluster
- `cluster_end` - Ending opinion cluster (optional)
- `title` - Visualization title
- `notes` - Description/notes
- `published` - Public visibility flag
- `deleted` - Soft delete flag
- `date_created`, `date_modified` - Timestamps

**Permissions:** Users can modify only their own visualizations (`IsOwner` permission).

---

### Citations

| Endpoint | ViewSet | Methods | Description |
|----------|---------|---------|-------------|
| `/citation-lookup/` | `CitationLookupViewSet` | POST | Parse and lookup legal citations |

#### Citation Lookup Request
Parse legal citations and retrieve matching case information.

**Request Body:**
```json
{
  "text": "410 U.S. 113"
}
```

**Response:**
```json
{
  "results": [
    {
      "citation": "410 U.S. 113",
      "cluster": {
        "id": 12345,
        "case_name": "Roe v. Wade",
        "date_filed": "1973-01-22",
        "absolute_url": "/opinion/12345/roe-v-wade/",
        ...
      }
    }
  ]
}
```

**Rate Limit:** 60 requests/minute (can be overridden per user)

---

### Webhooks

| Endpoint | ViewSet | Methods | Description |
|----------|---------|---------|-------------|
| `/memberships/` | `MembershipWebhookViewSet` | POST | Neon CRM membership webhooks |

#### Webhook Documentation
- Getting started: `/help/api/webhooks/getting-started/`
- Full documentation: `/help/api/webhooks/`

#### Webhook Management
Webhooks can be configured to receive real-time updates when data changes.

**Supported Event Types:**
- Docket updates
- Opinion cluster updates
- Audio file additions
- Financial disclosure updates

**Webhook Configuration:**
Managed through user account settings (see User API endpoints).

---

## Error Handling

### HTTP Status Codes

| Status Code | Meaning |
|-------------|---------|
| 200 OK | Request successful |
| 201 Created | Resource created successfully |
| 204 No Content | Successful deletion |
| 400 Bad Request | Invalid request parameters |
| 401 Unauthorized | Authentication required |
| 403 Forbidden | Permission denied |
| 404 Not Found | Resource not found |
| 405 Method Not Allowed | HTTP method not supported |
| 429 Too Many Requests | Rate limit exceeded |
| 500 Internal Server Error | Server error |
| 503 Service Unavailable | Temporary unavailability |

### Error Response Format

```json
{
  "detail": "Error message description"
}
```

### Common Error Scenarios

#### Invalid Cursor
```json
{
  "detail": "Invalid cursor"
}
```
**Solution:** The cursor token is malformed or expired. Start from the first page without a cursor parameter.

#### Deep Pagination
```json
{
  "detail": "Invalid page: Deep API pagination is not allowed. Please review API documentation."
}
```
**Solution:** Use cursor pagination (V4 only) or limit your page number to 100 or less.

#### Rate Limit Exceeded
```json
{
  "detail": "Request was throttled. Expected available in 3600 seconds."
}
```
**Solution:** Wait for the specified time or upgrade your account for higher limits.

#### V3 Access Denied
```json
{
  "detail": "As a new user, you don't have permission to access V3 of the API. Please use V4 instead."
}
```
**Solution:** Use V4 endpoints instead of V3.

#### Permission Denied
```json
{
  "detail": "You do not have permission to perform this action."
}
```
**Solution:** Ensure you're authenticated and have the necessary permissions for the resource.

---

## Examples

### Example 1: List Courts
```bash
curl -X GET \
  "https://www.courtlistener.com/api/rest/v4/courts/" \
  -H "Authorization: Token YOUR_API_TOKEN"
```

**Response:**
```json
{
  "count": 400,
  "next": "https://www.courtlistener.com/api/rest/v4/courts/?page=2",
  "previous": null,
  "results": [
    {
      "id": "scotus",
      "resource_uri": "https://www.courtlistener.com/api/rest/v4/courts/scotus/",
      "full_name": "Supreme Court of the United States",
      "short_name": "Supreme Court",
      "jurisdiction": "F",
      "position": 1.0,
      "citation_string": "U.S.",
      "in_use": true,
      "has_opinion_scraper": true,
      "has_oral_argument_scraper": true
    },
    ...
  ]
}
```

---

### Example 2: Search for Dockets by Court and Date
```bash
curl -X GET \
  "https://www.courtlistener.com/api/rest/v4/dockets/?court=scotus&date_filed__gte=2020-01-01&date_filed__lt=2021-01-01" \
  -H "Authorization: Token YOUR_API_TOKEN"
```

---

### Example 3: Get Specific Opinion
```bash
curl -X GET \
  "https://www.courtlistener.com/api/rest/v4/opinions/12345/" \
  -H "Authorization: Token YOUR_API_TOKEN"
```

**Response:**
```json
{
  "id": 12345,
  "resource_uri": "https://www.courtlistener.com/api/rest/v4/opinions/12345/",
  "cluster": "https://www.courtlistener.com/api/rest/v4/clusters/5678/",
  "type": "010combined",
  "author": 789,
  "plain_text": "Full opinion text...",
  "html": "<article>...</article>",
  "html_with_citations": "<article>...</article>",
  "per_curiam": false,
  "date_created": "2020-05-15T10:30:00Z",
  "date_modified": "2020-05-15T10:30:00Z"
}
```

---

### Example 4: Full-Text Search (V4)
```bash
curl -X GET \
  "https://www.courtlistener.com/api/rest/v4/search/?q=fourth+amendment&type=o" \
  -H "Authorization: Token YOUR_API_TOKEN"
```

Query Parameters:
- `q` - Search query
- `type` - Search type: `o` (opinions), `r` (RECAP), `oa` (oral arguments), `p` (people)

---

### Example 5: Create a Search Alert
```bash
curl -X POST \
  "https://www.courtlistener.com/api/rest/v4/alerts/" \
  -H "Authorization: Token YOUR_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Fourth Amendment Cases",
    "query": "q=fourth+amendment&type=o",
    "rate": "dly",
    "alert_type": "search"
  }'
```

---

### Example 6: Using Cursor Pagination
```bash
# First page
curl -X GET \
  "https://www.courtlistener.com/api/rest/v4/dockets/?order_by=id" \
  -H "Authorization: Token YOUR_API_TOKEN"

# Next page (using cursor from previous response)
curl -X GET \
  "https://www.courtlistener.com/api/rest/v4/dockets/?order_by=id&cursor=cD0yMDIxLTA..." \
  -H "Authorization: Token YOUR_API_TOKEN"
```

---

### Example 7: Filter Opinions by Multiple Criteria
```bash
curl -X GET \
  "https://www.courtlistener.com/api/rest/v4/opinions/?cluster__court=ca9&cluster__date_filed__year=2020&type=010combined&fields=id,cluster,plain_text" \
  -H "Authorization: Token YOUR_API_TOKEN"
```

Filters applied:
- Court: Ninth Circuit (ca9)
- Year filed: 2020
- Type: Combined opinion
- Return only specific fields

---

### Example 8: Citation Lookup
```bash
curl -X POST \
  "https://www.courtlistener.com/api/rest/v4/citation-lookup/" \
  -H "Authorization: Token YOUR_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "410 U.S. 113"
  }'
```

---

### Example 9: Get Judge Information with Positions
```bash
curl -X GET \
  "https://www.courtlistener.com/api/rest/v4/people/789/?fields=id,name_full,positions" \
  -H "Authorization: Token YOUR_API_TOKEN"
```

---

### Example 10: Upload RECAP Document
```bash
curl -X POST \
  "https://www.courtlistener.com/api/rest/v4/recap/" \
  -H "Authorization: Token YOUR_API_TOKEN" \
  -F "court=cand" \
  -F "upload_type=1" \
  -F "document=@/path/to/document.pdf"
```

---

## Additional Resources

### API Documentation Pages
- API Index: `/help/api/`
- REST API Docs: `/help/api/rest/`
- Case Law API: `/help/api/rest/case-law/`
- PACER/RECAP API: `/help/api/rest/pacer/`
- Judges API: `/help/api/rest/judges/`
- Oral Arguments API: `/help/api/rest/oral-arguments/`
- Financial Disclosures API: `/help/api/rest/financial-disclosures/`
- Search API: `/help/api/rest/search/`
- Alerts API: `/help/api/rest/alerts/`
- Webhooks: `/help/api/webhooks/`
- Field Reference: `/help/api/rest/fields/`
- Change Log: `/help/api/rest/changes/`
- V4 Migration Guide: `/help/api/rest/v4/migration-guide/`

### Bulk Data Access
- Bulk Data Index: `/help/api/bulk-data/`
- Replication Documentation: `/help/api/replication/`

### Coverage Data
- Opinion Coverage: `/api/rest/v4/coverage/opinions/`
- Court Coverage: `/api/rest/v4/coverage/{court}/`

### Browsable API
Access any endpoint in a web browser to use the interactive browsable API with form-based queries and authentication.

---

## Support

For additional help or to report issues:
- GitHub Issues: https://github.com/freelawproject/courtlistener
- Free Law Project: https://www.freelawproject.org/
- Contact: info@free.law

---

**Last Updated:** 2025-11-04
**API Version:** V4 (Current)
**Documentation Version:** 1.0
