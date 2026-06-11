import urllib.parse
import urllib.request
import re


class IDsNCBI:
    def __init__(self, ids: list):
        self.ids = ids
        self.count = len(ids)


class URLQueryIDs:
    def __init__(self, query: str):
        self.query = query
        self.url = self._build_url()
    
    def _build_url(self) -> str:
        q = urllib.parse.quote(self.query.strip(), safe="")
        return (
            "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
            f"?db=protein&term={q}&retmax=10000&retmode=text&tool=tidyprot"
        )
    
    def get_ids(self):
        with urllib.request.urlopen(self.url, timeout=60) as r:
            text = r.read().decode("utf-8")
        ids = re.findall(r"<Id>(\d+)</Id>", text)
        return IDsNCBI(ids)

