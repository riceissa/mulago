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
        for grant_url in grant_urls():
            writer.writerows(grant_info(grant_url))


def grant_info(grant_url):
    """Get info about a specific grant."""
    result = []
    soup = BeautifulSoup(requests.get(grant_url).content, "lxml")
    grantee = soup.find("h1").text

    infobox = soup.find("div", {"class": "info"}).find_all("p")

    amount = infobox[1].text.strip()
    assert amount.startswith("$")

    funded_since = infobox[2].text
    assert funded_since.startswith("Funded since")
    funded_since = funded_since[len("Funded since"):].strip()

    try:
        rainer_fellow = infobox[3].text
    except IndexError:
        # Some grantees are not Rainer Fellows, so ignore them
        rainer_fellow = ""

    if rainer_fellow:
        assert rainer_fellow.startswith("Rainer Fellow:")
        rainer_fellow = rainer_fellow[len("Rainer Fellow:"):].strip()

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
            if "/who-we-fund/" in str(link.get("href")):
                yield link.get("href")

if __name__ == "__main__":
    main()
