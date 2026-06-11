import urllib.parse
import urllib.request


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


