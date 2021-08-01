import requests
from bs4 import BeautifulSoup


def bs_setting(query_url: str):
    resp = requests.get(query_url, timeout=(3.0, 7.5))
    return BeautifulSoup(resp.text, "html.parser")
