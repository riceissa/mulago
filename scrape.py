#!/usr/bin/env python3

import pdb

import csv
import re
import requests
from bs4 import BeautifulSoup

def main():
    with open("data.csv", "w") as f:
        fieldnames = ["grantee", "url", "amount", "funded_since",
                      "rainer_fellow", "why_invest"]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for grant_url in grantee_urls():
            writer.writerow(grant_info(grant_url))


def grant_info(grant_url):
    """Get info about a specific grant."""
    soup = BeautifulSoup(requests.get(grant_url).content, "lxml")
    grantee = soup.find("h1").text

    infobox = soup.find("div", {"class": "info"}).find_all("p")
    amount = infobox[1].text
    funded_since = infobox[2].text
    assert funded_since.startswith("Funded since")
    rainer_fellow = infobox[3].text
    assert rainer_fellow.startswith("Rainer Fellow:")
    
    tag = soup.find(text=re.compile("Why we invest")).next_element
    while tag.name != "p":
        tag = tag.next_element
    why_invest = tag.text

    return {"grantee": grantee,
            "url": grant_url,
            "amount": amount,
            "funded_since": funded_since,
            "rainer_fellow": rainer_fellow,
            "why_invest": why_invest}


def grantee_urls():
    with open("who-we-fund.html", "r") as f:
        soup = BeautifulSoup(f, "lxml")
        for link in soup.find_all("a"):
            if "/who-we-fund/" in str(link.get("href")):
                yield link.get("href")

if __name__ == "__main__":
    main()
