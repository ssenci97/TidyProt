import urllib.parse
import urllib.request


class IDsUniProtKB:
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
            "https://rest.uniprot.org/uniprotkb/stream"
            f"?query={q}&format=tsv&fields=accession"
        )
    
    def get_ids(self):
        with urllib.request.urlopen(self.url, timeout=60) as r:
            text = r.read().decode("utf-8")
        lines = text.strip().split("\n")
        ids = [line for line in lines[1:] if line]
        return IDsUniProtKB(ids)

