# Semiconductor Patent Fee Petition Research

## Overview

This folder contains comprehensive research tools for finding semiconductor patent infringement cases (2022-2025) with attorney fee petitions, lodestar calculations, and expert witness billing rates.

**Target Criteria:**
- Patent infringement cases involving semiconductor technology
- Filed 2022-2025 in N.D. California, W.D. Texas, or D. Delaware
- Cases with fee petitions containing lodestar calculations
- Expert witness hourly rates and technical consultant billing
- Focus: memory chips, logic processors, manufacturing processes

---

## Quick Start Guide

### ⭐ NEW: Ready-to-Use Case Database

**FASTEST START:** Open `semiconductor_patent_cases.json` or `CASE_SUMMARY.md`
- **25 semiconductor patent cases** with direct CourtListener URLs
- **Complete docket information** (docket IDs, case numbers, courts, years)
- **Confirmed fee petitions** identified and flagged
- **Top 4 priority cases** with highest likelihood of fee petitions
- **Organized by technology:** Memory (DRAM), GPU, processors, fabrication, EDA tools

---

### For Comprehensive Searches:

**Step 1:** Review `CASE_SUMMARY.md` ⭐⭐⭐
- **Top 4 priority cases** with confirmed/likely fee petitions
- Case summaries with technology descriptions
- Direct links to all 25 cases
- Search strategies for finding fee documents

**Step 2:** Open `semiconductor_patent_cases.json`
- Machine-readable database of all cases
- Filter by category, court, year, or company
- Copy URLs directly into browser

**Step 3:** Use `quick_search_links.md` for broader searches
- 15+ CourtListener search URLs for discovering more cases
- Organized by priority, district court, and technology type

**Step 4:** Consult `example_cases.md` and `semiconductor_patent_search_guide.md`
- Detailed case descriptions and search strategies
- Expected billing rates (2022-2025)
- Step-by-step document identification instructions

---

## File Descriptions

### 1. `CASE_SUMMARY.md` ⭐⭐⭐ START HERE (NEW)
**Purpose:** Executive summary of found cases with top priorities
**Contains:**
- Top 4 priority cases (confirmed/likely fee petitions)
- Quick links to all 25 cases
- Technology category breakdowns
- Court and company summaries
- Recommended search order

**Best For:** Getting directly to relevant cases with fee petitions

---

### 2. `semiconductor_patent_cases.json` (NEW)
**Purpose:** Machine-readable database of all cases
**Contains:**
- 25 semiconductor patent cases (2014-2024)
- Complete docket information (IDs, URLs, case numbers)
- Party names, courts, years filed
- Technology descriptions
- Fee petition status (where confirmed)
- Organized by category: Memory, GPU, Processors, Fabrication, EDA

**Best For:** Programmatic access, filtering, direct URL copying

---

### 3. `quick_search_links.md`
**Purpose:** Direct access to CourtListener searches
**Contains:**
- 15+ clickable search URLs
- Company-specific searches (Samsung, Intel, Micron, NVIDIA)
- Technology-specific searches (DRAM, GPU, lithography)
- District court filters (Delaware, N.D. Cal, W.D. Texas)

**Best For:** Quick results, browsing cases

---

### 4. `example_cases.md`
**Purpose:** Known high-profile semiconductor patent cases
**Contains:**
- 19 specific cases likely to have fee petitions
- Case names, parties, technology areas
- Tier 1/2/3 priority rankings
- Targeted search queries for each case

**Highlighted Cases:**
- **VLSI v. Intel** (processor patents, $2B+ damages)
- **Samsung v. Netlist** (DRAM memory technology)
- **Qualcomm 5G disputes** (mobile processors)
- **GlobalFoundries** (FinFET manufacturing)

**Best For:** Targeted searches for known cases

---

### 5. `semiconductor_patent_search_guide.md`
**Purpose:** Comprehensive methodology and reference
**Contains:**
- Search strategy explanations
- Key terms glossary
- Expected billing rates by role
- Document identification tips
- Tips for searching within dockets
- Court code reference

**Best For:** Understanding search methodology, troubleshooting

---

## Recommended Workflow

### Phase 1: Quick Searches (15-30 minutes)
1. Open `quick_search_links.md`
2. Click "Priority Search #1" (Lodestar + Semiconductor)
3. Click "Priority Search #2" (Delaware cases)
4. Review results, identify 5-10 promising cases

### Phase 2: Targeted Case Search (30-45 minutes)
1. Open `example_cases.md`
2. Search for Tier 1 cases (VLSI v. Intel, Samsung v. Netlist)
3. Click into case dockets on CourtListener
4. Search dockets for "fees", "costs", "lodestar"
5. Identify document numbers for fee petitions

### Phase 3: Document Review (1-2 hours)
1. Download PDF fee petition documents
2. Search within PDFs for:
   - "lodestar" (calculation tables)
   - "hourly rate" (attorney/expert billing)
   - "expert witness" (technical consultant costs)
3. Extract relevant billing information
4. Compile findings

### Expected Time to Find 3-4 Qualifying Cases:
**Total:** 2-3 hours (including document review)

---

## What You're Looking For

### In Docket Entries:
- ✅ "Motion for Attorney Fees and Costs"
- ✅ "Prevailing Party Fee Petition"
- ✅ "Declaration in Support of Fee Application"
- ✅ "Lodestar Calculation" (often in exhibits)
- ✅ "Expert Witness Declaration"

### In Fee Petition Documents:
- ✅ Lodestar tables (hours × rates)
- ✅ Attorney hourly rates ($500-$1,500/hr)
- ✅ Expert witness rates ($400-$800/hr)
- ✅ Technical consultant billing ($300-$600/hr)
- ✅ Breakdown by task (discovery, motion practice, trial)

### Case Characteristics:
- ✅ Major semiconductor companies (Samsung, Intel, Micron, NVIDIA, Qualcomm)
- ✅ Foundries, fabless designers, or EDA tool companies
- ✅ Technology: DRAM, GPU, FinFET, lithography, chip packaging
- ✅ District courts: D. Delaware, N.D. California, W.D. Texas
- ✅ Filed 2022-2025

---

## Key Search Terms

### Technology Keywords:
- semiconductor, integrated circuit, chip design
- FinFET, process node, GAA, CMOS
- DRAM, NAND, flash memory, GPU
- lithography, EUV, DUV, foundry
- chip packaging, chiplet, 3D stacking

### Legal/Fee Keywords:
- attorney fees, fee petition, bill of costs
- lodestar, hourly rate, billing rate
- expert witness, technical consultant
- prevailing party, exceptional case
- 35 U.S.C. § 285 (patent fee statute)

### Company Names:
- Samsung, SK Hynix, Micron (memory)
- Intel, AMD, Qualcomm, NVIDIA (processors/GPU)
- TSMC, GlobalFoundries (foundries)
- Synopsys, Cadence (EDA tools)

---

## CourtListener Tips

### Account Setup:
- Free account recommended for bulk downloads
- Allows saving searches and setting alerts

### Search Features:
- Advanced search: Use Boolean operators (AND, OR, NOT)
- Date filters: `filed_after=01/01/2022`
- Court filters: `&court=ded` (Delaware), `&court=cand` (N.D. Cal), `&court=txwd` (W.D. Texas)
- Nature of suit: `&nature_of_suit="830 Patent Infringement"`

### Docket Navigation:
- Docket entries numbered sequentially (ECF No. 1, 2, 3...)
- Fee petitions typically filed after judgment (ECF #100-200)
- Use browser search (Ctrl+F) to find "fees" in docket
- Download PDFs by clicking document numbers

### Document Access:
- Most documents free on CourtListener
- Some sealed or redacted (especially billing details)
- If document unavailable, may need PACER access

---

## Expected Billing Rates (2022-2025 Reference)

### Attorneys:
| Role | Hourly Rate Range |
|------|-------------------|
| Senior Partners | $1,000 - $1,500 |
| Partners | $800 - $1,200 |
| Senior Associates | $500 - $800 |
| Associates | $300 - $600 |
| Paralegals | $150 - $300 |

### Expert Witnesses:
| Type | Hourly Rate Range |
|------|-------------------|
| Semiconductor Engineers | $400 - $800 |
| Chip Design Experts | $500 - $900 |
| Manufacturing Process Experts | $400 - $700 |
| Damages Economists | $600 - $1,200 |
| EDA Tool Specialists | $350 - $650 |

### Technical Consultants:
| Role | Hourly Rate Range |
|------|-------------------|
| Technical Advisors | $300 - $600 |
| Litigation Support | $250 - $500 |
| Trial Consultants | $400 - $700 |

*Rates vary by geography, experience, and case complexity*

---

## Court Reference

### Primary Venues:
| Court | Code | Location | Notes |
|-------|------|----------|-------|
| D. Delaware | `ded` | Wilmington | Major patent venue, many semiconductor cases |
| N.D. California | `cand` | San Jose/San Francisco | Silicon Valley, tech company HQ |
| W.D. Texas | `txwd` | Austin/Waco | Emerging patent venue, semiconductor hub (Austin) |

### Alternative Venues:
- C.D. California (`cacd`) - Los Angeles area
- E.D. Texas (`txed`) - Historically major patent venue
- S.D. California (`casd`) - San Diego (Qualcomm HQ)

---

## Success Metrics

### Good Result:
- ✅ Find 3-4 cases meeting all criteria
- ✅ Each case has downloadable fee petition
- ✅ Fee petitions contain lodestar calculations
- ✅ Expert witness rates clearly stated
- ✅ Billing breakdown by task/timekeeper

### Excellent Result:
- ✅ All of above, plus:
- ✅ Multiple years of data (2022-2025)
- ✅ Different technology areas (memory, GPU, foundry)
- ✅ Different district courts represented
- ✅ Mix of plaintiff/defendant fee petitions
- ✅ Detailed expert witness declarations with hourly rates

---

## Troubleshooting

### Problem: No search results
**Solutions:**
- Remove some search terms (less restrictive)
- Try broader date range
- Search company names only, then filter
- Try different district court

### Problem: Too many results
**Solutions:**
- Add "lodestar" requirement
- Narrow to single district
- Add specific technology term
- Filter by company name

### Problem: Can't find fee petitions in docket
**Solutions:**
- Search for "285" (fee statute)
- Look 30-90 days after final judgment
- Check for "prevailing party" motions
- Try "bill of costs" instead

### Problem: Documents are sealed
**Solutions:**
- Look for public version or redacted version
- Check for opposition brief (may quote rates)
- Look for court order on fees (may state rates)
- Try related cases by same parties

---

## Next Steps After Finding Cases

1. **Download Documents:**
   - Fee petition motion (main document)
   - Supporting declarations
   - Exhibits (lodestar tables, billing records)
   - Court order on fees

2. **Extract Data:**
   - Create spreadsheet with:
     - Case name, number, court
     - Attorney hourly rates by level
     - Expert witness rates by specialty
     - Total hours and fees
     - Technology area

3. **Analyze:**
   - Compare rates across cases
   - Identify trends by district, year, technology
   - Calculate average rates by role
   - Note successful vs. unsuccessful fee requests

4. **Document:**
   - Save case citations
   - Note document numbers (ECF/Docket Entry)
   - Screenshot or excerpt key rate information
   - Track any useful case law on fee awards

---

## Additional Resources

### CourtListener Documentation:
- https://www.courtlistener.com/help/
- Advanced search syntax
- API access (for bulk research)

### PACER (if needed):
- https://pacer.uscourts.gov/
- Federal court document access
- $0.10 per page (up to $3 per document)

### Patent Fee Law:
- 35 U.S.C. § 285 (exceptional cases)
- Octane Fitness v. ICON Health & Fitness (2014) - lowered standard for fees
- Patent cases frequently involve fee petitions

---

## Contact & Support

This research was compiled on 2025-11-19.

For questions about:
- **CourtListener:** support@courtlistener.com
- **PACER Access:** PACER Service Center
- **This Research:** See commit history in repository

---

## Summary

**To find semiconductor patent cases with fee petitions:**

1. **Start:** `quick_search_links.md` → Priority Search #1
2. **Target:** `example_cases.md` → VLSI v. Intel, Samsung v. Netlist
3. **Reference:** `semiconductor_patent_search_guide.md` for methodology

**Time Estimate:** 2-3 hours to find 3-4 qualifying cases with fee petitions

**Good luck with your research!**
