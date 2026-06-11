#!/usr/bin/env python3
"""
tidyprot/test_connection.py — Check internet and API reachability
"""

import socket
import urllib.error
import urllib.request


def check_internet(host: str = "8.8.8.8", port: int = 53, timeout: int = 3) -> bool:
    """Return True if we can open a TCP connection to a known external host."""
    try:
        socket.setdefaulttimeout(timeout)
        socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((host, port))
        return True
    except OSError:
        return False


def test_ncbi(timeout: int = 10) -> bool:
    """Return True if NCBI eutils responds with HTTP 200."""
    url = (
        "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
        "?db=protein&term=1&retmax=1&retmode=text"
    )
    try:
        with urllib.request.urlopen(url, timeout=timeout) as r:
            return r.status == 200
    except (urllib.error.URLError, urllib.error.HTTPError):
        return False


def test_uniprot(timeout: int = 10) -> bool:
    """Return True if UniProt REST API responds with HTTP 200."""
    url = (
        "https://rest.uniprot.org/uniprotkb/search"
        "?query=accession:P12345&format=json&size=1"
    )
    try:
        req = urllib.request.Request(url, headers={"Accept": "application/json"})
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.status == 200
    except (urllib.error.URLError, urllib.error.HTTPError):
        return False

