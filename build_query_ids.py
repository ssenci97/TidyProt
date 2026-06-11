# tidyprot/build_query_ids.py
import urllib.parse
import urllib.request
import re


class URLQueryIDs:
    def __init__(self, source: str, query: str):
        self.source = source
        self.query = query
        self.url = self._build_url()
    
    def _build_url(self) -> str:
        q = urllib.parse.quote(self.query.strip(), safe="")
        
        if self.source == "NCBI":
            return (
                "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
                f"?db=protein&term={q}&retmax=10000&retmode=text&tool=tidyprot"
            )
        elif self.source == "UniProtKB":
            return (
                "https://rest.uniprot.org/uniprotkb/stream"
                f"?query={q}&format=tsv&fields=accession"
            )
        else:
            raise ValueError(f"Unknown source: {self.source}")
    
    def get_ids(self) -> list:
        with urllib.request.urlopen(self.url, timeout=60) as r:
            text = r.read().decode("utf-8")
        
        if self.source == "NCBI":
            return re.findall(r"<Id>(\d+)</Id>", text)
        elif self.source == "UniProtKB":
            lines = text.strip().split("\n")
            return [line for line in lines[1:] if line]

