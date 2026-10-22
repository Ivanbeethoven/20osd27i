# LaTeX template provenance

Verified on 2026-10-22. The [OSDI 2027 author requirements](https://www.usenix.org/conference/osdi27/requirements-authors) direct authors to the [USENIX conference-paper templates page](https://www.usenix.org/conferences/author-resources/paper-templates).

## Files obtained directly from USENIX

| File | Exact source URL | Bytes | SHA-256 |
|---|---|---:|---|
| `templates/usenix2019_v3.2.tex` | https://www.usenix.org/sites/default/files/usenix2019_v3.2.tex | 10332 | `b2203c8d5adc698cc3ecf937636607041fabbfa91fc3481e18cfc4d46cc2d73e` |
| `templates/usenix2019_v3.sty` | https://www.usenix.org/sites/default/files/usenix2019_v3.sty | 3712 | `4ed9aa9d0c5daec54ce3b4188a4bf6d3bef3462c79ff65551d567511d3c45ff6` |

The files retain their original bytes and historical author/style comments. The filename's 2019 date does not mean this package silently targets OSDI 2019: the currently accessed USENIX template page links these files. These files were obtained from the official site, not from an unverified third-party mirror. The browser text extractor rejected the TeX MIME type; a normal HTTP request with a standard user agent retrieved the original files successfully.

## Use in the manuscript

Start with `\documentclass[letterpaper,twocolumn,10pt]{article}` and `\usepackage{usenix2019_v3}`. Preserve the style file instead of renaming or modifying its dimensions. The style sets the 7 × 9 inch text area and 0.33 inch column separation, and loads Times-related font and reference packages.

Adapt the example's author/title blocks in the manuscript only. The official example includes author identities, so it is not itself an anonymous submission. Set page numbering explicitly for a review/internal manuscript. Keep the working title for the internal draft; anonymization of the publicly named BrewFS project requires a separate author decision and a complete identifier audit.

Do not reuse the sample bibliography as if it were the paper's references. The original sample is supplied solely to show the official template, and has its own illustrative citations. The paper must use the separately verified BrewFS bibliography.

## Verification required for the final build

Compile with the bibliography tool; inspect warnings, unresolved citations, PDF page size, fonts, and every rendered page. Confirm that the final main content is within the chosen cycle's limit. Do not add negative spacing or change font/margin settings to force compliance. Root manuscript validation is recorded separately from this template download record.

## Policy distinction

The [2027 CFP](https://www.usenix.org/conference/osdi27/call-for-papers) limits initial content to 12 pages and permits references beyond that. It allows separate optional supplemental files; it does not permit unrestricted supplementary appendix pages inside the main manuscript. The 14-page accepted-paper allowance is a different stage. Recheck current instructions before submission.
