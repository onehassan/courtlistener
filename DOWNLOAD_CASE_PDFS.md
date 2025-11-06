# Downloading All PDF Files from a CourtListener Case

## Overview

This guide shows how to download all PDF files associated with a specific case on CourtListener, given a URL like:

```
https://www.courtlistener.com/docket/68563855/icharts-llc-v-tableau-software-llc/
```

## Important: API Endpoint Access

⚠️ **The `/recap-documents/` endpoint requires special permissions** and returns 403 Forbidden for most users.

✅ **Solution: Use the Search API instead** - Works without special permissions!

## Quick Start

### Step 1: Extract Docket ID from URL

From the URL `https://www.courtlistener.com/docket/68563855/icharts-llc-v-tableau-software-llc/`:
- **Docket ID**: `68563855`

The docket ID is always the numeric value after `/docket/` in the URL.

### Step 2: Use the Search API to Get All Documents

**No authentication required!**

```bash
curl -X GET \
  "https://www.courtlistener.com/api/rest/v4/search/?q=docket_id:68563855&type=r"
```

**Alternative with authentication (for higher rate limits):**

```bash
curl -X GET \
  "https://www.courtlistener.com/api/rest/v4/search/?q=docket_id:68563855&type=r" \
  -H "Authorization: Token YOUR_API_TOKEN"
```

### Step 3: Download Each PDF

Documents are nested under `recap_documents` in the response. Each document has a `filepath_local` field. Construct the download URL:

```
https://storage.courtlistener.com/{filepath_local}
```

---

## Why This Guide Uses the Search API

**The Problem:** The `/recap-documents/` endpoint requires a special permission (`has_recap_api_access`) that most users don't have. Attempting to use it results in a **403 Forbidden** error.

**The Solution:** The Search API (`/search/?type=r`) provides access to the same documents without requiring special permissions. It's powered by Elasticsearch and works for both authenticated and anonymous users.

**For detailed information about the 403 error and alternative solutions, see:**
- **[RECAP_DOCS_README.md](RECAP_DOCS_README.md)** - Quick overview
- **[RECAP_403_INVESTIGATION.md](RECAP_403_INVESTIGATION.md)** - In-depth analysis
- **[RECAP_SOLUTIONS_GUIDE.md](RECAP_SOLUTIONS_GUIDE.md)** - All available solutions

---

## Complete Python Script: Download All PDFs from a Case URL

```python
#!/usr/bin/env python3
"""
Download all available PDF files from a CourtListener docket.

Usage:
    python download_case_pdfs.py <docket_url> <api_token> [output_dir]

Example:
    python download_case_pdfs.py \
        "https://www.courtlistener.com/docket/68563855/icharts-llc-v-tableau-software-llc/" \
        "your_api_token" \
        "./case_pdfs"
"""

import requests
import os
import sys
import re
from pathlib import Path
from urllib.parse import urlparse
import time

def extract_docket_id(url):
    """
    Extract docket ID from CourtListener URL.

    Examples:
        https://www.courtlistener.com/docket/68563855/icharts-llc-v-tableau-software-llc/
        -> 68563855
    """
    match = re.search(r'/docket/(\d+)/', url)
    if match:
        return match.group(1)

    # Try parsing just the number if provided directly
    if url.isdigit():
        return url

    raise ValueError(f"Could not extract docket ID from URL: {url}")


def fetch_all_documents(docket_id, api_token=None):
    """
    Fetch all available RECAP documents for a docket using the Search API.

    This method works WITHOUT special permissions, unlike the direct
    /recap-documents/ endpoint which requires has_recap_api_access permission.

    Args:
        docket_id: The CourtListener docket ID
        api_token: Optional API authentication token (for higher rate limits)

    Returns:
        List of document dictionaries
    """
    BASE_URL = "https://www.courtlistener.com/api/rest/v4"
    headers = {"Authorization": f"Token {api_token}"} if api_token else {}

    all_documents = []
    cursor = None

    print(f"Fetching documents for docket {docket_id} using Search API...")

    while True:
        params = {
            "q": f"docket_id:{docket_id}",
            "type": "r",  # Returns dockets with nested documents
        }

        if cursor:
            params["cursor"] = cursor

        response = requests.get(
            f"{BASE_URL}/search/",
            headers=headers,
            params=params
        )

        if response.status_code != 200:
            print(f"Error: {response.status_code} - {response.text}")
            break

        data = response.json()
        results = data.get('results', [])

        if not results:
            break

        # Extract nested documents from search results
        for result in results:
            recap_docs = result.get('recap_documents', [])
            # Filter for available documents only
            available_docs = [doc for doc in recap_docs if doc.get('is_available')]
            all_documents.extend(available_docs)

        print(f"  Fetched {len(results)} docket(s), {len(all_documents)} documents total...")

        # Check for next page
        next_url = data.get('next')
        if not next_url:
            break

        # Extract cursor from next URL
        if 'cursor=' in next_url:
            cursor = next_url.split('cursor=')[-1].split('&')[0]
        else:
            break

    return all_documents


def download_pdf(doc, output_dir, headers=None):
    """
    Download a single PDF document.

    Args:
        doc: Document dictionary from API
        output_dir: Directory to save PDF
        headers: Optional HTTP headers for authentication

    Returns:
        Tuple of (success: bool, filepath: str)
    """
    if not doc.get('is_available') or not doc.get('filepath_local'):
        return (False, None)

    # Construct PDF URL
    pdf_url = f"https://storage.courtlistener.com/{doc['filepath_local']}"

    # Create filename from document number and description
    doc_num = doc.get('document_number', 'unknown')
    attach_num = doc.get('attachment_number') or 0
    description = doc.get('description', 'document')

    # Sanitize description for filename
    safe_description = re.sub(r'[^\w\s-]', '', description)[:50]
    safe_description = re.sub(r'[-\s]+', '_', safe_description)

    filename = f"doc_{doc_num:03d}"
    if attach_num > 0:
        filename += f"_attach_{attach_num}"
    filename += f"_{safe_description}.pdf"

    filepath = os.path.join(output_dir, filename)

    # Download PDF
    try:
        pdf_response = requests.get(pdf_url, headers=headers, timeout=60)

        if pdf_response.status_code == 200:
            with open(filepath, 'wb') as f:
                f.write(pdf_response.content)
            return (True, filepath)
        else:
            print(f"    Failed to download (HTTP {pdf_response.status_code}): {filename}")
            return (False, None)

    except Exception as e:
        print(f"    Error downloading {filename}: {e}")
        return (False, None)


def download_all_case_pdfs(docket_url, api_token, output_dir="./case_pdfs"):
    """
    Main function to download all PDFs from a case.

    Args:
        docket_url: CourtListener docket URL or docket ID
        api_token: API authentication token
        output_dir: Directory to save PDFs (default: ./case_pdfs)

    Returns:
        Number of PDFs successfully downloaded
    """
    # Extract docket ID
    try:
        docket_id = extract_docket_id(docket_url)
    except ValueError as e:
        print(f"Error: {e}")
        return 0

    print(f"\n{'='*80}")
    print(f"Downloading PDFs for Docket ID: {docket_id}")
    print(f"Output Directory: {output_dir}")
    print(f"{'='*80}\n")

    # Create output directory
    Path(output_dir).mkdir(parents=True, exist_ok=True)

    # Fetch all documents
    documents = fetch_all_documents(docket_id, api_token)

    if not documents:
        print("\nNo available documents found.")
        return 0

    print(f"\nFound {len(documents)} available documents. Starting download...\n")

    # Download each PDF
    headers = {"Authorization": f"Token {api_token}"}
    successful_downloads = 0

    for i, doc in enumerate(documents, 1):
        print(f"[{i}/{len(documents)}] Downloading doc #{doc.get('document_number', '?')}: "
              f"{doc.get('description', 'N/A')[:60]}...")

        success, filepath = download_pdf(doc, output_dir, headers)

        if success:
            file_size = os.path.getsize(filepath) / 1024  # KB
            print(f"    ✅ Saved: {os.path.basename(filepath)} ({file_size:.1f} KB)")
            successful_downloads += 1

        # Rate limiting: be gentle with the API
        if i % 10 == 0:
            time.sleep(1)

    print(f"\n{'='*80}")
    print(f"Download Complete!")
    print(f"Successfully downloaded: {successful_downloads}/{len(documents)} PDFs")
    print(f"Saved to: {os.path.abspath(output_dir)}")
    print(f"{'='*80}\n")

    return successful_downloads


def main():
    """Command-line interface"""
    if len(sys.argv) < 3:
        print(__doc__)
        print("\nError: Missing required arguments")
        print("\nUsage:")
        print("  python download_case_pdfs.py <docket_url> <api_token> [output_dir]")
        print("\nExample:")
        print('  python download_case_pdfs.py \\')
        print('    "https://www.courtlistener.com/docket/68563855/icharts-llc-v-tableau-software-llc/" \\')
        print('    "your_api_token_here" \\')
        print('    "./case_pdfs"')
        sys.exit(1)

    docket_url = sys.argv[1]
    api_token = sys.argv[2]
    output_dir = sys.argv[3] if len(sys.argv) > 3 else "./case_pdfs"

    download_all_case_pdfs(docket_url, api_token, output_dir)


if __name__ == "__main__":
    main()
```

### Save and Run

1. **Save the script:**
   ```bash
   # Save as download_case_pdfs.py
   ```

2. **Make it executable:**
   ```bash
   chmod +x download_case_pdfs.py
   ```

3. **Run it:**
   ```bash
   python download_case_pdfs.py \
     "https://www.courtlistener.com/docket/68563855/icharts-llc-v-tableau-software-llc/" \
     "your_api_token_here" \
     "./icharts_pdfs"
   ```

---

## Manual Step-by-Step Method

### Step 1: Get Documents Using Search API

```bash
DOCKET_ID=68563855
API_TOKEN="your_api_token"  # Optional - can work without token

# Get documents via Search API (no special permissions required)
curl -X GET \
  "https://www.courtlistener.com/api/rest/v4/search/?q=docket_id:${DOCKET_ID}&type=r" \
  -H "Authorization: Token ${API_TOKEN}" \
  > docket_search.json
```

**Response contains:**
```json
{
  "results": [
    {
      "docket_id": 68563855,
      "caseName": "iCharts LLC v. Tableau Software LLC",
      "recap_documents": [
        {
          "id": 123,
          "document_number": "1",
          "description": "Complaint",
          "is_available": true,
          "filepath_local": "recap/gov.uscourts.cand.123/doc.1.0.pdf"
        },
        ...
      ]
    }
  ]
}
```

### Step 2: Extract and Download PDFs

```bash
# Extract nested documents and download PDFs
jq -r '.results[].recap_documents[] | select(.is_available == true) | .filepath_local' docket_search.json | while read filepath; do
  if [ ! -z "$filepath" ]; then
    filename=$(basename "$filepath")
    echo "Downloading: $filename"
    curl -o "$filename" "https://storage.courtlistener.com/$filepath"
  fi
done
```

---

## Bash Script Version

```bash
#!/bin/bash
# download_case_pdfs.sh
# Usage: ./download_case_pdfs.sh <docket_url> [api_token] [output_dir]
# Note: API token is optional - works without authentication

set -e

# Parse arguments
DOCKET_URL="$1"
API_TOKEN="${2:-}"
OUTPUT_DIR="${3:-./case_pdfs}"

if [ -z "$DOCKET_URL" ]; then
    echo "Usage: $0 <docket_url> [api_token] [output_dir]"
    echo ""
    echo "Example:"
    echo "  $0 'https://www.courtlistener.com/docket/68563855/...' 'your_token' './pdfs'"
    echo "  $0 'https://www.courtlistener.com/docket/68563855/...'  # Works without token"
    exit 1
fi

# Extract docket ID from URL
DOCKET_ID=$(echo "$DOCKET_URL" | grep -oP '/docket/\K\d+')

if [ -z "$DOCKET_ID" ]; then
    echo "Error: Could not extract docket ID from URL: $DOCKET_URL"
    exit 1
fi

echo "========================================="
echo "Downloading PDFs for Docket: $DOCKET_ID"
echo "Output Directory: $OUTPUT_DIR"
echo "Method: Search API (no special permissions)"
echo "========================================="

# Create output directory
mkdir -p "$OUTPUT_DIR"

# Prepare auth header if token provided
AUTH_HEADER=""
if [ ! -z "$API_TOKEN" ]; then
    AUTH_HEADER="-H \"Authorization: Token ${API_TOKEN}\""
fi

TOTAL_DOWNLOADED=0

echo ""
echo "Fetching documents via Search API..."

# Fetch documents using Search API (no special permissions required)
RESPONSE=$(curl -s -X GET \
    "https://www.courtlistener.com/api/rest/v4/search/?q=docket_id:${DOCKET_ID}&type=r" \
    ${AUTH_HEADER})

# Check if we have results
RESULTS_COUNT=$(echo "$RESPONSE" | jq -r '.results | length')

if [ "$RESULTS_COUNT" -eq 0 ]; then
    echo "No dockets found with ID: $DOCKET_ID"
    exit 1
fi

echo "Found docket with documents"

# Download each PDF from nested recap_documents
echo "$RESPONSE" | jq -r '.results[].recap_documents[] | select(.is_available == true) | "\(.document_number)|\(.attachment_number // 0)|\(.description)|\(.filepath_local)"' | while IFS='|' read -r doc_num attach_num description filepath; do
    if [ ! -z "$filepath" ]; then
        # Create safe filename
        safe_desc=$(echo "$description" | tr -dc '[:alnum:] -' | tr ' ' '_' | cut -c1-50)
        filename=$(printf "doc_%03d" "$doc_num")

        if [ "$attach_num" -gt 0 ]; then
            filename="${filename}_attach_${attach_num}"
        fi

        filename="${filename}_${safe_desc}.pdf"

        echo "  Downloading: $filename"
        curl -s -o "${OUTPUT_DIR}/${filename}" "https://storage.courtlistener.com/${filepath}"

        if [ $? -eq 0 ]; then
            TOTAL_DOWNLOADED=$((TOTAL_DOWNLOADED + 1))
            file_size=$(du -h "${OUTPUT_DIR}/${filename}" | cut -f1)
            echo "    ✅ Saved ($file_size)"
        else
            echo "    ❌ Failed"
        fi
    fi
done

echo ""
echo "========================================="
echo "Download Complete!"
echo "Total PDFs downloaded: $TOTAL_DOWNLOADED"
echo "Saved to: $(pwd)/$OUTPUT_DIR"
echo "========================================="
```

### Run Bash Script:

```bash
chmod +x download_case_pdfs.sh

./download_case_pdfs.sh \
  "https://www.courtlistener.com/docket/68563855/icharts-llc-v-tableau-software-llc/" \
  "your_api_token" \
  "./icharts_pdfs"
```

---

## Advanced: Using Cursor Pagination (For Large Dockets)

For dockets with many documents (>10,000), use cursor-based pagination:

```python
def fetch_all_documents_cursor(docket_id, api_token):
    """
    Fetch all documents using cursor pagination (recommended for large datasets)
    """
    BASE_URL = "https://www.courtlistener.com/api/rest/v4"
    headers = {"Authorization": f"Token {api_token}"}

    all_documents = []
    cursor = None
    page_num = 0

    while True:
        params = {
            "docket_entry__docket": docket_id,
            "is_available": "true",
            "order_by": "id",  # Required for cursor pagination
            "page_size": 100
        }

        if cursor:
            params["cursor"] = cursor

        response = requests.get(
            f"{BASE_URL}/recap-documents/",
            headers=headers,
            params=params
        )

        if response.status_code != 200:
            print(f"Error: {response.status_code}")
            break

        data = response.json()
        documents = data.get('results', [])

        if not documents:
            break

        all_documents.extend(documents)
        page_num += 1
        print(f"  Fetched batch {page_num}: {len(documents)} documents ({len(all_documents)} total)")

        # Get next cursor
        next_url = data.get('next')
        if not next_url:
            break

        # Extract cursor from next URL
        cursor = next_url.split('cursor=')[-1].split('&')[0] if 'cursor=' in next_url else None

        if not cursor:
            break

    return all_documents
```

---

## Response Structure Example

When you query the API, each document looks like this:

```json
{
  "id": 123456789,
  "resource_uri": "https://www.courtlistener.com/api/rest/v4/recap-documents/123456789/",
  "docket_entry": 987654,
  "document_type": 1,
  "document_number": "1",
  "attachment_number": null,
  "pacer_doc_id": "12340001",
  "is_available": true,
  "is_free_on_pacer": false,
  "filepath_local": "recap/gov.uscourts.cand.123456/gov.uscourts.cand.123456.1.0.pdf",
  "filepath_ia": "https://archive.org/download/gov.uscourts.cand.123456/gov.uscourts.cand.123456.1.0.pdf",
  "description": "Complaint",
  "plain_text": "",
  "ocr_status": 1,
  "date_upload": "2024-01-15T10:30:00Z",
  "date_created": "2024-01-15T10:30:00Z",
  "date_modified": "2024-01-15T10:30:00Z",
  "sha1": "abc123def456...",
  "page_count": 25,
  "file_size": 1048576,
  "absolute_url": "/docket/68563855/1/icharts-llc-v-tableau-software-llc/"
}
```

**Key fields for downloading:**
- `is_available`: Must be `true` to download
- `filepath_local`: S3 path to the PDF
- `document_number`: Document number in the docket
- `attachment_number`: Attachment number (if applicable)
- `description`: Document description

**Construct PDF URL:**
```
https://storage.courtlistener.com/{filepath_local}
```

---

## Filter Options

When fetching documents, you can use these filters:

| Filter | Example | Description |
|--------|---------|-------------|
| `docket_entry__docket` | `68563855` | Filter by docket ID (required) |
| `is_available` | `true` | Only available PDFs |
| `is_free_on_pacer` | `true` | Only free documents on PACER |
| `document_type` | `1` | 1=PACER Document, 2=Attachment |
| `document_number` | `5` | Specific document number |
| `document_number__gte` | `10` | Document number >= 10 |
| `date_upload__gte` | `2020-01-01` | Uploaded after date |
| `ocr_status` | `1` | 1=OCR complete, 2=unnecessary, 3=failed, 4=needed |

**Example with filters:**
```bash
curl -X GET \
  "https://www.courtlistener.com/api/rest/v4/recap-documents/?docket_entry__docket=68563855&is_available=true&document_type=1&date_upload__gte=2023-01-01" \
  -H "Authorization: Token YOUR_API_TOKEN"
```

---

## Tips and Best Practices

### 1. **Check Document Count First**

Before downloading, check how many documents are available:

```python
response = requests.get(
    f"{BASE_URL}/recap-documents/",
    headers=headers,
    params={
        "docket_entry__docket": docket_id,
        "is_available": "true",
        "count": "on"
    }
)
count = response.json()['count']
print(f"Total documents to download: {count}")
```

### 2. **Handle Rate Limits**

- Authenticated users: 5,000 requests/hour
- Add delays between downloads:
  ```python
  time.sleep(0.5)  # 500ms delay
  ```

### 3. **Resume Partial Downloads**

Track which files you've already downloaded:

```python
# Skip already downloaded files
if os.path.exists(filepath):
    print(f"  Skipping (already exists): {filename}")
    continue
```

### 4. **Error Handling**

Wrap downloads in try-except blocks:

```python
try:
    pdf_response = requests.get(pdf_url, timeout=60)
    pdf_response.raise_for_status()
    # Save file...
except requests.exceptions.Timeout:
    print("  Error: Download timed out")
except requests.exceptions.HTTPError as e:
    print(f"  Error: HTTP {e.response.status_code}")
except Exception as e:
    print(f"  Error: {e}")
```

### 5. **Organize by Document Type**

Create subdirectories for different document types:

```python
doc_type = doc.get('document_type')
if doc_type == 1:
    subdir = "documents"
elif doc_type == 2:
    subdir = "attachments"

output_path = os.path.join(output_dir, subdir)
Path(output_path).mkdir(parents=True, exist_ok=True)
```

---

## Alternative: Bulk Download via RECAP Archive

For very large dockets, you can also download bulk archives from the Internet Archive:

```python
def get_archive_url(docket_id, api_token):
    """Get Internet Archive bulk download URL if available"""
    BASE_URL = "https://www.courtlistener.com/api/rest/v4"
    headers = {"Authorization": f"Token {api_token}"}

    # Get docket info
    response = requests.get(
        f"{BASE_URL}/dockets/{docket_id}/",
        headers=headers
    )

    docket = response.json()
    pacer_case_id = docket.get('pacer_case_id')
    court = docket.get('court')

    if pacer_case_id and court:
        # Construct IA identifier
        ia_identifier = f"gov.uscourts.{court}.{pacer_case_id}"
        ia_url = f"https://archive.org/download/{ia_identifier}"
        print(f"Internet Archive: {ia_url}")
        return ia_url

    return None
```

---

## Troubleshooting

### Issue: "403 Forbidden when accessing /recap-documents/"

**Solution:**
This is expected! The `/recap-documents/` endpoint requires special permissions. **This guide has been updated to use the Search API instead**, which doesn't require special permissions.

**See detailed documentation:**
- [RECAP_DOCS_README.md](RECAP_DOCS_README.md) - Quick overview
- [RECAP_403_INVESTIGATION.md](RECAP_403_INVESTIGATION.md) - Root cause analysis
- [RECAP_SOLUTIONS_GUIDE.md](RECAP_SOLUTIONS_GUIDE.md) - Alternative solutions

### Issue: "No documents found"

**Solution:**
- Verify the docket ID is correct
- Check if the case has any documents available
- Try the URL in a browser to verify the docket exists

### Issue: "401 Unauthorized"

**Solution:**
- If using authentication, verify your API token is correct
- Note: The Search API works WITHOUT authentication (but has lower rate limits)
- Make sure token is included in the Authorization header

### Issue: "PDFs won't download"

**Solution:**
- Check `filepath_local` is not null/empty in the response
- Verify the constructed URL is correct: `https://storage.courtlistener.com/{filepath_local}`
- Some documents may be sealed or restricted by the court

### Issue: "Download times out"

**Solution:**
- Increase timeout: `requests.get(url, timeout=120)`
- Retry with exponential backoff
- Check your internet connection
- Some PDFs are very large and may take time to download

---

## Source Code References

- RECAPDocument API: `/home/user/courtlistener/cl/search/api_views.py:182-206`
- Document Filters: `/home/user/courtlistener/cl/search/filters.py:212-233`
- Document Model: `/home/user/courtlistener/cl/search/models.py:1303+`
- Document Serializer: `/home/user/courtlistener/cl/search/api_serializers.py:151-168`

---

## Summary

To download all PDFs from a case URL:

1. **Extract docket ID** from the URL (number after `/docket/`)
2. **Use Search API** with `q=docket_id:{id}&type=r` (no special permissions required!)
3. **Extract nested documents** from `recap_documents` field in results
4. **Download each PDF** from `https://storage.courtlistener.com/{filepath_local}`
5. **Handle errors and rate limits** appropriately

**Key Points:**
- ✅ Search API works **without special permissions**
- ✅ Authentication is **optional** (higher rate limits with token)
- ✅ Returns dockets with **nested documents**
- ✅ Filters for `is_available=true` automatically

**Quick command:**
```bash
# Works WITHOUT authentication!
python download_case_pdfs.py \
  "https://www.courtlistener.com/docket/68563855/icharts-llc-v-tableau-software-llc/"

# Or with token for higher rate limits:
python download_case_pdfs.py \
  "https://www.courtlistener.com/docket/68563855/icharts-llc-v-tableau-software-llc/" \
  "YOUR_API_TOKEN" \
  "./output_pdfs"
```

**For more information about the 403 error and alternatives:**
- See [RECAP_DOCS_README.md](RECAP_DOCS_README.md)

---

**Last Updated:** 2025-11-06
**API Version:** V4
