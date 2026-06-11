import urllib.parse
import urllib.request
import time


class DataNCBIUrlList:
    def __init__(self, urls: list):
        self.urls = urls
        self.count = len(urls)


class DataUniProtKBUrlList:
    def __init__(self, urls: list):
        self.urls = urls
        self.count = len(urls)




def build_data_urls_uniprotkb(ids_uniprot, fields: list, verbose: bool = False) -> DataUniProtKBUrlList:
    ids = ids_uniprot.ids
    if not ids:
        return DataUniProtKBUrlList([])
    fields_str = ",".join(fields)
    max_url_len = 7500
    base = "https://rest.uniprot.org/uniprotkb/stream?format=tsv&fields=" + fields_str + "&query="
    base_len = len(base)
    urls = []
    current_batch = []
    for acc in ids:
        acc_query = f"accession:{acc}+OR+"
        if base_len + len(acc_query) + sum(len(f"accession:{a}+OR+") for a in current_batch) > max_url_len:
            query = "+OR+".join(f"accession:{a}" for a in current_batch)
            urls.append(base + urllib.parse.quote(query, safe="+"))
            current_batch = [acc]
        else:
            current_batch.append(acc)
    if current_batch:
        query = "+OR+".join(f"accession:{a}" for a in current_batch)
        urls.append(base + urllib.parse.quote(query, safe="+"))
    return DataUniProtKBUrlList(urls)




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

