#!/usr/bin/env python3

import csv
import datetime
import re

def main():
    with open("data.csv", "r") as f:
        reader = csv.DictReader(f)
        first = True
        print("""insert into donations (donor, donee, amount, donation_date,
        donation_date_precision, donation_date_basis, cause_area, url,
        donor_cause_area_url, notes, affected_countries, affected_states,
        affected_cities, affected_regions) values""")

        for row in reader:
            amount, method = amount_and_method(row['amount'])

            notes = ("Donation date is not a single date but rather when "
                     "funding began. Rainer fellow in " +
                     row['rainer_fellow'] +
                     ". Mulago’s reasons for investing: “" +
                     row['why_invest'] + "”")

            print(("    " if first else "    ,") + "(" + ",".join([
                mysql_quote("Mulago"),  # donor
                mysql_quote(row['grantee']),  # donee
                str(amount),  # amount
                mysql_quote(row['funded_since'] + "-01-01"),  # donation_date
                mysql_quote("year"),  # donation_date_precision
                mysql_quote("donation log"),  # donation_date_basis
                mysql_quote(""),  # cause_area
                mysql_quote(row['url']),  # url
                mysql_quote(""),  # donor_cause_area_url
                mysql_quote(notes),  # notes
                mysql_quote(""),  # affected_countries
                mysql_quote(""),  # affected_states
                mysql_quote(""),  # affected_cities
                mysql_quote(""),  # affected_regions
            ]) + ")")
            first = False
        print(";")


def mysql_quote(x):
    '''
    Quote the string x using MySQL quoting rules. If x is the empty string,
    return "NULL". Probably not safe against maliciously formed strings, but
    whatever; our input is fixed and from a basically trustable source..
    '''
    if not x:
        return "NULL"
    x = x.replace("\\", "\\\\")
    x = x.replace("'", "''")
    x = x.replace("\n", "\\n")
    return "'{}'".format(x)


def amount_and_method(amount_string):
    """Separate out the amount and method from the "amount and method"
    string."""
    m = re.match(r"\$([0-9.]+)\s*(M|million|K)(.*)", amount_string)
    num = float(m.group(1))
    if m.group(2) in ["M", "million"]:
        num *= 1e6
    elif m.group(2) == "K":
        num *= 1e3
    else:
        raise ValueError("We can't understand this number format.")
    return (round(num, 2), m.group(3).strip())


if __name__ == "__main__":
    main()
