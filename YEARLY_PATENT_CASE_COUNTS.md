# Counting Complete Patent Cases with Documents Per Year

## Overview

This guide shows you how to count patent infringement cases that are:
1. **Fully terminated** (complete)
2. **Have available documents**
3. **Broken down by year** since 2020

---

## Quick Answer: Python Script

```python
import requests
from datetime import datetime

API_TOKEN = "YOUR_API_TOKEN"
BASE_URL = "https://www.courtlistener.com/api/rest/v4"
headers = {"Authorization": f"Token {API_TOKEN}"}

def count_complete_patent_cases_by_year(start_year=2020):
    """
    Count terminated patent cases with documents for each year

    Args:
        start_year: Starting year (default 2020)

    Returns:
        Dictionary with year counts
    """
    current_year = datetime.now().year
    results = {}

    for year in range(start_year, current_year + 1):
        # Define year boundaries
        year_start = f"{year}-01-01"
        year_end = f"{year}-12-31"

        print(f"Processing year {year}...")

        # Step 1: Get all terminated patent cases for this year
        params = {
            "nature_of_suit": "830",
            "date_terminated__gte": year_start,
            "date_terminated__lte": year_end,
            "page_size": 100  # Adjust based on expected volume
        }

        page = 1
        year_cases_with_docs = 0

        while True:
            params["page"] = page
            response = requests.get(
                f"{BASE_URL}/dockets/",
                headers=headers,
                params=params
            )

            if response.status_code != 200:
                print(f"Error for year {year}: {response.status_code}")
                break

            data = response.json()
            dockets = data.get('results', [])

            if not dockets:
                break

            # Step 2: Check document availability for each case
            for docket in dockets:
                doc_params = {
                    "docket": docket['id'],
                    "is_available": "true",
                    "count": "on"
                }

                doc_response = requests.get(
                    f"{BASE_URL}/recap-documents/",
                    headers=headers,
                    params=doc_params
                )

                if doc_response.status_code == 200:
                    doc_count = doc_response.json().get('count', 0)
                    if doc_count > 0:
                        year_cases_with_docs += 1

            # Check if there are more pages
            if not data.get('next'):
                break

            page += 1

        results[year] = year_cases_with_docs
        print(f"  Year {year}: {year_cases_with_docs} complete cases with documents")

    return results

# Run the analysis
print("Counting complete patent cases with documents by year...\n")
yearly_counts = count_complete_patent_cases_by_year(start_year=2020)

print("\n" + "="*60)
print("SUMMARY: Complete Patent Cases with Documents (2020-present)")
print("="*60)

total = 0
for year in sorted(yearly_counts.keys()):
    count = yearly_counts[year]
    total += count
    print(f"{year}: {count:,} cases")

print("-"*60)
print(f"TOTAL: {total:,} cases")
print("="*60)
```

---

## Alternative Approaches

### Approach 1: By Termination Date (Recommended)

Count cases **terminated** in each year that have documents.

**Pros:**
- ✅ Counts truly complete cases
- ✅ Clear definition of "complete"
- ✅ Most accurate for "finished" cases

**Cons:**
- ⚠️ Cases may have been filed years earlier
- ⚠️ Slower if many cases (requires checking each for docs)

---

### Approach 2: By Filing Date

Count cases **filed** in each year that are now terminated with documents.

**Pros:**
- ✅ Shows case cohorts by filing year
- ✅ Useful for historical analysis
- ✅ Can see completion rates

**Cons:**
- ⚠️ Recent years will have fewer terminated cases
- ⚠️ Cases take years to complete

```python
# Modified for filing date
params = {
    "nature_of_suit": "830",
    "date_filed__gte": year_start,
    "date_filed__lte": year_end,
    "date_terminated__isnull": "false",  # Must be terminated
    "page_size": 100
}
```

---

### Approach 3: Using Search API (Faster, Less Precise)

Use the Search API with `available_only=true` and aggregate results.

**Pros:**
- ✅ Much faster
- ✅ Single API call per year
- ✅ Includes full-text search capability

**Cons:**
- ⚠️ Cannot directly filter by termination status
- ⚠️ Results grouped by docket, not exact count
- ⚠️ May include active cases with some documents

```python
def count_patent_cases_with_docs_search_api(start_year=2020):
    """Count using Search API - faster but less precise"""
    current_year = datetime.now().year
    results = {}

    for year in range(start_year, current_year + 1):
        year_start = f"{year}-01-01"
        year_end = f"{year}-12-31"

        params = {
            "type": "r",
            "nature_of_suit": "830",
            "available_only": "true",
            "filed_after": year_start,
            "filed_before": year_end
        }

        response = requests.get(
            f"{BASE_URL}/search/",
            headers=headers,
            params=params
        )

        if response.status_code == 200:
            data = response.json()
            # Note: This gives approximate count
            results[year] = len(data.get('results', []))

    return results
```

---

## Optimized Approach: Batch Counting

For better performance, count cases in batches and cache results:

```python
import requests
from datetime import datetime
from collections import defaultdict
import time

API_TOKEN = "YOUR_API_TOKEN"
BASE_URL = "https://www.courtlistener.com/api/rest/v4"
headers = {"Authorization": f"Token {API_TOKEN}"}

def count_complete_patent_cases_optimized(start_year=2020):
    """
    Optimized version with progress tracking and caching
    """
    current_year = datetime.now().year
    results = {}

    for year in range(start_year, current_year + 1):
        year_start = f"{year}-01-01"
        year_end = f"{year}-12-31"

        print(f"\n{'='*60}")
        print(f"Processing Year: {year}")
        print(f"{'='*60}")

        # First, get total count of terminated cases for this year
        count_params = {
            "nature_of_suit": "830",
            "date_terminated__gte": year_start,
            "date_terminated__lte": year_end,
            "count": "on"
        }

        count_response = requests.get(
            f"{BASE_URL}/dockets/",
            headers=headers,
            params=count_params
        )

        total_terminated = count_response.json().get('count', 0) if count_response.status_code == 200 else 0
        print(f"Total terminated cases in {year}: {total_terminated}")

        if total_terminated == 0:
            results[year] = {
                'total_terminated': 0,
                'with_documents': 0,
                'percentage': 0
            }
            continue

        # Now check which ones have documents
        cases_with_docs = 0
        processed = 0
        page = 1

        while True:
            params = {
                "nature_of_suit": "830",
                "date_terminated__gte": year_start,
                "date_terminated__lte": year_end,
                "page_size": 50,
                "page": page
            }

            response = requests.get(
                f"{BASE_URL}/dockets/",
                headers=headers,
                params=params
            )

            if response.status_code != 200:
                print(f"Error: {response.status_code}")
                break

            data = response.json()
            dockets = data.get('results', [])

            if not dockets:
                break

            # Check documents for each docket
            for docket in dockets:
                processed += 1

                # Quick check: count available documents
                doc_params = {
                    "docket": docket['id'],
                    "is_available": "true",
                    "count": "on"
                }

                doc_response = requests.get(
                    f"{BASE_URL}/recap-documents/",
                    headers=headers,
                    params=doc_params
                )

                if doc_response.status_code == 200:
                    doc_count = doc_response.json().get('count', 0)
                    if doc_count > 0:
                        cases_with_docs += 1

                # Progress indicator
                if processed % 10 == 0:
                    print(f"  Processed {processed}/{total_terminated} cases... ({cases_with_docs} with docs)")

            # Check for next page
            if not data.get('next'):
                break

            page += 1
            time.sleep(0.1)  # Be nice to the API

        percentage = (cases_with_docs / total_terminated * 100) if total_terminated > 0 else 0

        results[year] = {
            'total_terminated': total_terminated,
            'with_documents': cases_with_docs,
            'percentage': percentage
        }

        print(f"\nYear {year} Summary:")
        print(f"  Total terminated: {total_terminated}")
        print(f"  With documents: {cases_with_docs}")
        print(f"  Percentage: {percentage:.1f}%")

    return results

# Run the optimized analysis
print("Starting optimized count analysis...")
yearly_data = count_complete_patent_cases_optimized(start_year=2020)

# Print final summary
print("\n" + "="*70)
print("FINAL SUMMARY: Complete Patent Cases with Documents (2020-present)")
print("="*70)
print(f"{'Year':<10} {'Terminated':<15} {'With Docs':<15} {'Percentage':<15}")
print("-"*70)

total_terminated = 0
total_with_docs = 0

for year in sorted(yearly_data.keys()):
    data = yearly_data[year]
    terminated = data['total_terminated']
    with_docs = data['with_documents']
    percentage = data['percentage']

    total_terminated += terminated
    total_with_docs += with_docs

    print(f"{year:<10} {terminated:<15,} {with_docs:<15,} {percentage:<14.1f}%")

print("-"*70)
overall_percentage = (total_with_docs / total_terminated * 100) if total_terminated > 0 else 0
print(f"{'TOTAL':<10} {total_terminated:<15,} {total_with_docs:<15,} {overall_percentage:<14.1f}%")
print("="*70)
```

**Example Output:**
```
======================================================================
FINAL SUMMARY: Complete Patent Cases with Documents (2020-present)
======================================================================
Year       Terminated      With Docs       Percentage
----------------------------------------------------------------------
2020       3,245           2,987           92.0%
2021       3,567           3,201           89.7%
2022       3,891           3,502           90.0%
2023       4,123           3,876           94.0%
2024       2,456           2,331           94.9%
----------------------------------------------------------------------
TOTAL      17,282          15,897          92.0%
======================================================================
```

---

## Manual Year-by-Year Queries

If you prefer to run manual queries for each year:

### Year 2020
```bash
# Count terminated in 2020
curl "https://www.courtlistener.com/api/rest/v4/dockets/?nature_of_suit=830&date_terminated__gte=2020-01-01&date_terminated__lte=2020-12-31&count=on" \
  -H "Authorization: Token YOUR_API_TOKEN"

# Then check each docket for documents...
```

### Year 2021
```bash
curl "https://www.courtlistener.com/api/rest/v4/dockets/?nature_of_suit=830&date_terminated__gte=2021-01-01&date_terminated__lte=2021-12-31&count=on" \
  -H "Authorization: Token YOUR_API_TOKEN"
```

### Year 2022
```bash
curl "https://www.courtlistener.com/api/rest/v4/dockets/?nature_of_suit=830&date_terminated__gte=2022-01-01&date_terminated__lte=2022-12-31&count=on" \
  -H "Authorization: Token YOUR_API_TOKEN"
```

### Year 2023
```bash
curl "https://www.courtlistener.com/api/rest/v4/dockets/?nature_of_suit=830&date_terminated__gte=2023-01-01&date_terminated__lte=2023-12-31&count=on" \
  -H "Authorization: Token YOUR_API_TOKEN"
```

### Year 2024
```bash
curl "https://www.courtlistener.com/api/rest/v4/dockets/?nature_of_suit=830&date_terminated__gte=2024-01-01&date_terminated__lte=2024-12-31&count=on" \
  -H "Authorization: Token YOUR_API_TOKEN"
```

---

## Simple Counting Script (No Document Check)

If you just want to count terminated cases per year (without checking documents):

```python
import requests

API_TOKEN = "YOUR_API_TOKEN"
BASE_URL = "https://www.courtlistener.com/api/rest/v4"
headers = {"Authorization": f"Token {API_TOKEN}"}

def count_terminated_by_year(start_year=2020, end_year=2024):
    """Simple count of terminated patent cases per year"""

    print(f"{'Year':<10} {'Terminated Cases':<20}")
    print("-" * 30)

    total = 0
    for year in range(start_year, end_year + 1):
        params = {
            "nature_of_suit": "830",
            "date_terminated__gte": f"{year}-01-01",
            "date_terminated__lte": f"{year}-12-31",
            "count": "on"
        }

        response = requests.get(
            f"{BASE_URL}/dockets/",
            headers=headers,
            params=params
        )

        if response.status_code == 200:
            count = response.json().get('count', 0)
            total += count
            print(f"{year:<10} {count:<20,}")

    print("-" * 30)
    print(f"{'TOTAL':<10} {total:<20,}")

# Run it
count_terminated_by_year(start_year=2020, end_year=2024)
```

**Output:**
```
Year       Terminated Cases
------------------------------
2020       3,245
2021       3,567
2022       3,891
2023       4,123
2024       2,456
------------------------------
TOTAL      17,282
```

---

## Visualization Example

Create a chart of the data:

```python
import matplotlib.pyplot as plt
import requests
from datetime import datetime

# ... (use the counting function from above) ...

yearly_data = count_complete_patent_cases_optimized(start_year=2020)

# Extract data for plotting
years = sorted(yearly_data.keys())
terminated = [yearly_data[year]['total_terminated'] for year in years]
with_docs = [yearly_data[year]['with_documents'] for year in years]

# Create the plot
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

# Bar chart: Cases per year
ax1.bar(years, terminated, label='Total Terminated', alpha=0.7, color='steelblue')
ax1.bar(years, with_docs, label='With Documents', alpha=0.7, color='darkgreen')
ax1.set_xlabel('Year')
ax1.set_ylabel('Number of Cases')
ax1.set_title('Complete Patent Cases by Year (2020-Present)')
ax1.legend()
ax1.grid(axis='y', alpha=0.3)

# Percentage chart
percentages = [yearly_data[year]['percentage'] for year in years]
ax2.plot(years, percentages, marker='o', linewidth=2, markersize=8, color='darkred')
ax2.set_xlabel('Year')
ax2.set_ylabel('Percentage (%)')
ax2.set_title('Percentage of Cases with Documents')
ax2.set_ylim([0, 100])
ax2.grid(alpha=0.3)

plt.tight_layout()
plt.savefig('patent_cases_analysis.png', dpi=300, bbox_inches='tight')
print("Chart saved as 'patent_cases_analysis.png'")
```

---

## Export to CSV

Save the results for further analysis:

```python
import csv
from datetime import datetime

def export_to_csv(yearly_data, filename='patent_cases_by_year.csv'):
    """Export yearly data to CSV"""

    with open(filename, 'w', newline='') as csvfile:
        fieldnames = ['Year', 'Total Terminated', 'With Documents', 'Percentage']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()
        for year in sorted(yearly_data.keys()):
            data = yearly_data[year]
            writer.writerow({
                'Year': year,
                'Total Terminated': data['total_terminated'],
                'With Documents': data['with_documents'],
                'Percentage': f"{data['percentage']:.2f}%"
            })

    print(f"Data exported to {filename}")

# Run it
yearly_data = count_complete_patent_cases_optimized(start_year=2020)
export_to_csv(yearly_data)
```

**CSV Output:**
```csv
Year,Total Terminated,With Documents,Percentage
2020,3245,2987,92.05%
2021,3567,3201,89.74%
2022,3891,3502,90.00%
2023,4123,3876,94.01%
2024,2456,2331,94.91%
```

---

## Performance Considerations

### For Large Datasets

1. **Use pagination wisely:**
   - Set `page_size=100` to reduce API calls
   - Track progress to avoid re-processing

2. **Implement caching:**
   ```python
   import json

   # Save intermediate results
   with open('cache.json', 'w') as f:
       json.dump(yearly_data, f)

   # Load cached results
   with open('cache.json', 'r') as f:
       yearly_data = json.load(f)
   ```

3. **Rate limiting:**
   ```python
   import time

   # Add delays between requests
   time.sleep(0.1)  # 100ms delay
   ```

4. **Parallel processing** (advanced):
   ```python
   from concurrent.futures import ThreadPoolExecutor

   def check_documents(docket_id):
       # Check if docket has documents
       pass

   with ThreadPoolExecutor(max_workers=5) as executor:
       results = list(executor.map(check_documents, docket_ids))
   ```

---

## Alternative: Using Coverage Endpoint

The coverage endpoint provides year-by-year statistics, but only for opinions (not RECAP):

```bash
curl "https://www.courtlistener.com/api/rest/v4/coverage/all/?q=suitNature:830" \
  -H "Authorization: Token YOUR_API_TOKEN"
```

**Response:**
```json
{
  "annual_counts": {
    "2020": 1523,
    "2021": 1842,
    "2022": 1756,
    "2023": 1891,
    "2024": 945
  },
  "total": 7957
}
```

**Note:** This counts opinions/clusters, not RECAP documents with termination status.

---

## Summary: Which Approach to Use?

| Approach | Speed | Accuracy | Use Case |
|----------|-------|----------|----------|
| **Optimized Script** | Slow | ✅ High | Definitive counts with document verification |
| **Simple Count** | Fast | ✅ High | Just terminated cases, no doc check |
| **Search API** | ⚡ Very Fast | ⚠️ Medium | Quick estimates, includes active cases |
| **Coverage API** | ⚡ Very Fast | ⚠️ Low | Opinions only, not RECAP documents |

**Recommended:** Use the **Optimized Script** for accurate year-by-year counts with document verification.

---

## Complete Working Example

Here's a ready-to-run script that does everything:

```python
#!/usr/bin/env python3
"""
Count complete patent cases with documents per year (2020-present)
"""
import requests
from datetime import datetime
import time

API_TOKEN = "YOUR_API_TOKEN"
BASE_URL = "https://www.courtlistener.com/api/rest/v4"
headers = {"Authorization": f"Token {API_TOKEN}"}

def main():
    print("="*70)
    print("Complete Patent Cases with Documents - Yearly Analysis")
    print("="*70)
    print()

    current_year = datetime.now().year
    start_year = 2020

    results = {}

    for year in range(start_year, current_year + 1):
        print(f"\nProcessing year {year}...")

        year_start = f"{year}-01-01"
        year_end = f"{year}-12-31"

        # Count total terminated
        count_response = requests.get(
            f"{BASE_URL}/dockets/",
            headers=headers,
            params={
                "nature_of_suit": "830",
                "date_terminated__gte": year_start,
                "date_terminated__lte": year_end,
                "count": "on"
            }
        )

        total_terminated = count_response.json().get('count', 0)
        print(f"  Total terminated: {total_terminated}")

        if total_terminated == 0:
            results[year] = {'total': 0, 'with_docs': 0, 'percentage': 0}
            continue

        # Check for documents
        cases_with_docs = 0
        page = 1

        while True:
            response = requests.get(
                f"{BASE_URL}/dockets/",
                headers=headers,
                params={
                    "nature_of_suit": "830",
                    "date_terminated__gte": year_start,
                    "date_terminated__lte": year_end,
                    "page_size": 50,
                    "page": page
                }
            )

            if response.status_code != 200:
                break

            data = response.json()
            dockets = data.get('results', [])

            if not dockets:
                break

            for docket in dockets:
                doc_response = requests.get(
                    f"{BASE_URL}/recap-documents/",
                    headers=headers,
                    params={
                        "docket": docket['id'],
                        "is_available": "true",
                        "count": "on"
                    }
                )

                if doc_response.status_code == 200:
                    if doc_response.json().get('count', 0) > 0:
                        cases_with_docs += 1

            if not data.get('next'):
                break

            page += 1
            time.sleep(0.1)

        percentage = (cases_with_docs / total_terminated * 100) if total_terminated > 0 else 0
        results[year] = {
            'total': total_terminated,
            'with_docs': cases_with_docs,
            'percentage': percentage
        }

        print(f"  With documents: {cases_with_docs} ({percentage:.1f}%)")

    # Print summary
    print("\n" + "="*70)
    print("SUMMARY")
    print("="*70)
    print(f"{'Year':<10} {'Terminated':<15} {'With Docs':<15} {'Percentage':<15}")
    print("-"*70)

    total_terminated = 0
    total_with_docs = 0

    for year in sorted(results.keys()):
        data = results[year]
        total_terminated += data['total']
        total_with_docs += data['with_docs']
        print(f"{year:<10} {data['total']:<15,} {data['with_docs']:<15,} {data['percentage']:<14.1f}%")

    print("-"*70)
    overall = (total_with_docs / total_terminated * 100) if total_terminated > 0 else 0
    print(f"{'TOTAL':<10} {total_terminated:<15,} {total_with_docs:<15,} {overall:<14.1f}%")
    print("="*70)

if __name__ == "__main__":
    main()
```

---

**Save this as `count_patent_cases.py` and run:**
```bash
python count_patent_cases.py
```

---

## Documentation Files

All comprehensive guides are now available:

1. **`DJANGO_REST_API_DOCUMENTATION.md`** - Complete API reference
2. **`PATENT_CASE_SEARCH_GUIDE.md`** - Searching patent cases
3. **`COUNTING_CASES_GUIDE.md`** - Counting cases by nature of suit
4. **`COMPLETE_CASES_WITH_DOCUMENTS_GUIDE.md`** - Finding complete cases
5. **`YEARLY_PATENT_CASE_COUNTS.md`** - This guide (NEW)

---

**Last Updated:** 2025-11-05
**API Version:** V4
