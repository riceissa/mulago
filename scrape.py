#!/usr/bin/env python3

import pdb

import sys
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
        for grant_url in grant_urls():
            writer.writerows(grant_info(grant_url))


def grant_info(grant_url):
    """Get info about a specific grant."""
    result = []
    print("Downloading %s" % grant_url, file=sys.stderr)
    soup = BeautifulSoup(requests.get(grant_url).content, "lxml")
    grantee = soup.find("h1").text

    infobox = soup.find("div", {"class": "info"}).find_all("p")

    amount = infobox[1].text.strip()
    assert amount.startswith("$")

    funded_since = ""
    rainer_fellow = ""
    for item in infobox:
        text = item.text.strip()
        if text.startswith("Funded since"):
            funded_since = text[len("Funded since"):].strip()
        elif text.startswith("Rainer Fellow:"):
            rainer_fellow = text[len("Rainer Fellow:"):].strip()

    tag = soup.find(text=re.compile("Why we invest")).next_element
    while tag.name != "p":
        tag = tag.next_element
    why_invest = tag.text.strip()

    grant_template = {"grantee": grantee,
            "url": grant_url,
            # "amount": amount,
            "funded_since": funded_since,
            "rainer_fellow": rainer_fellow,
            "why_invest": why_invest}

    # Some grantees have two payment methods listed, and we want to record them
    # as separate donations.
    if "; " in amount:
        methods = amount.split("; ")
        for method in methods:
            grant = grant_template.copy()
            grant.update({"amount": method})
            result.append(grant)
    elif ", " in amount:
        methods = amount.split(", ")
        for method in methods:
            grant = grant_template.copy()
            grant.update({"amount": method})
            result.append(grant)
    else:
        grant = grant_template.copy()
        grant.update({"amount": amount})
        result.append(grant)

    return result


def grant_urls():
    with open("who-we-fund.html", "r") as f:
        soup = BeautifulSoup(f, "lxml")
        for link in soup.find_all("a"):
            if "/Portfolio/" in str(link.get("href")):
                yield link.get("href")

if __name__ == "__main__":
    main()
