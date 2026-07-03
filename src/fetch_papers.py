"""Query PubMed E-utilities for recent articles in configured journals."""
import xml.etree.ElementTree as ET

import requests

ESEARCH_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
EFETCH_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"


def search_journal(journal, days_back, max_results):
    """Return a list of PMIDs published in `journal` within the last `days_back` days."""
    term = f'"{journal}"[Journal]'
    params = {
        "db": "pubmed",
        "term": term,
        "retmax": max_results,
        "datetype": "pdat",
        "reldate": days_back,
        "retmode": "json",
        "sort": "most recent",
    }
    resp = requests.get(ESEARCH_URL, params=params, timeout=30)
    resp.raise_for_status()
    return resp.json().get("esearchresult", {}).get("idlist", [])


def fetch_details(pmids):
    """Fetch title/abstract/authors/doi/link for a list of PMIDs."""
    if not pmids:
        return []

    params = {
        "db": "pubmed",
        "id": ",".join(pmids),
        "rettype": "abstract",
        "retmode": "xml",
    }
    resp = requests.get(EFETCH_URL, params=params, timeout=30)
    resp.raise_for_status()

    root = ET.fromstring(resp.content)
    articles = []
    for article in root.findall(".//PubmedArticle"):
        pmid_el = article.find(".//PMID")
        pmid = pmid_el.text if pmid_el is not None else None

        title_el = article.find(".//ArticleTitle")
        title = "".join(title_el.itertext()).strip() if title_el is not None else "(no title)"

        abstract_parts = [
            "".join(node.itertext()).strip()
            for node in article.findall(".//Abstract/AbstractText")
        ]
        abstract = "\n".join(p for p in abstract_parts if p) or "(no abstract available)"

        authors = []
        for author in article.findall(".//AuthorList/Author"):
            last = author.findtext("LastName")
            fore = author.findtext("ForeName")
            if last and fore:
                authors.append(f"{fore} {last}")
            elif last:
                authors.append(last)

        journal_title = article.findtext(".//Journal/Title") or ""

        doi = None
        for id_el in article.findall(".//ArticleIdList/ArticleId"):
            if id_el.get("IdType") == "doi":
                doi = id_el.text
                break

        link = f"https://doi.org/{doi}" if doi else f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/"

        articles.append(
            {
                "pmid": pmid,
                "title": title,
                "abstract": abstract,
                "authors": authors,
                "journal": journal_title,
                "link": link,
            }
        )
    return articles


def fetch_recent_articles(journals, days_back, max_results):
    """Search each journal and return de-duplicated article details keyed by PMID."""
    all_pmids = []
    seen = set()
    for journal in journals:
        for pmid in search_journal(journal, days_back, max_results):
            if pmid not in seen:
                seen.add(pmid)
                all_pmids.append(pmid)

    return fetch_details(all_pmids)
