"""Refresh the site's PubMed practice-guideline feed."""
import datetime
import json
import urllib.parse
import urllib.request

BASE = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"
HEADERS = {"User-Agent": "BahmanDaneshWebsite/1.0 (public educational website)"}


def get_json(url):
    request = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(request, timeout=30) as response:
        return json.load(response)


def main():
    query = {
        "db": "pubmed",
        "term": "practice guideline[pt] AND english[la] AND hasabstract",
        "sort": "pub date",
        "retmax": 8,
        "retmode": "json",
    }
    search = get_json(BASE + "esearch.fcgi?" + urllib.parse.urlencode(query))
    ids = search.get("esearchresult", {}).get("idlist", [])
    items = []

    if ids:
        summary = get_json(BASE + "esummary.fcgi?" + urllib.parse.urlencode({
            "db": "pubmed", "id": ",".join(ids), "retmode": "json"
        })).get("result", {})
        for pmid in ids:
            record = summary.get(pmid)
            if not record:
                continue
            items.append({
                "src": "PubMed · " + record.get("pubdate", ""),
                "t": record.get("title", "").rstrip("."),
                "d": "",
                "u": f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/",
            })

    with open("feed.json", "w", encoding="utf-8") as output:
        json.dump({
            "updated": datetime.date.today().isoformat(),
            "items": items,
        }, output, ensure_ascii=False, indent=2)
        output.write("\n")


if __name__ == "__main__":
    main()
