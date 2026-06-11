import urllib.parse
import urllib.request
import time


class DataNCBIUrlList:
    def __init__(self, urls: list):
        self.urls = urls
        self.count = len(urls)


def _epost_batch(ids: list, api_key: str = None) -> tuple:
    url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/epost.fcgi"
    id_str = ",".join(ids)
    data = f"db=protein&id={id_str}&tool=tidyprot".encode("utf-8")
    if api_key:
        data += f"&api_key={api_key}".encode("utf-8")
    req = urllib.request.Request(url, data=data, method="POST")
    with urllib.request.urlopen(req, timeout=60) as r:
        text = r.read().decode("utf-8")
    import re
    webenv = re.search(r"<WebEnv>([^<]+)</WebEnv>", text)
    query_key = re.search(r"<QueryKey>(\d+)</QueryKey>", text)
    if not webenv or not query_key:
        raise RuntimeError("EPost failed: no WebEnv/QueryKey in response")
    return webenv.group(1), int(query_key.group(1))


def build_data_urls_ncbi(ids_ncbi, batch_size: int = 500, api_key: str = None, verbose: bool = False) -> DataNCBIUrlList:
    ids = ids_ncbi.ids
    urls = []
    for i in range(0, len(ids), batch_size):
        batch = ids[i:i + batch_size]
        if verbose:
            print(f"  EPost batch {i//batch_size + 1}: {len(batch)} IDs", file=__import__("sys").stderr)
        webenv, query_key = _epost_batch(batch, api_key)
        url = (
            "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"
            f"?db=protein&WebEnv={urllib.parse.quote(webenv)}"
            f"&query_key={query_key}&rettype=gp&retmode=text&tool=tidyprot"
        )
        if api_key:
            url += f"&api_key={api_key}"
        urls.append(url)
        if i + batch_size < len(ids):
            time.sleep(0.35 if not api_key else 0.11)
    return DataNCBIUrlList(urls)

