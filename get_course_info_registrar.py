"""
Given a string of a department and course number, pulls information about the course from the registrar.
"""

import requests
from bs4 import BeautifulSoup
from pprint import pprint

dept = 'artg'

url = "http://registrar.ucsc.edu/catalog/programs-courses/course-descriptions/" + dept + ".html"

request_result = requests.get(url)

status_code = request_result.status_code
if status_code != 200:
    raise Exception("Request for search results page returned " + status_code)

soup = BeautifulSoup(request_result.text, 'html.parser')

h2s = soup.select("h2")

# a division is lower-division, upper-division, or graduate
division_p_tags = [h2.next_sibling.next_sibling for h2 in h2s]

every_strong_tag = [p.select("strong") for p in division_p_tags]

# see http://stackoverflow.com/a/406296
every_strong_flattened = [s for inner in every_strong_tag for s in inner]

# get every 3rd element
numbers_in_strongs = [every_strong_flattened[x] for x in range(len(every_strong_flattened)) if x % 3 == 0]

# the [:-1] slice takes off the period from the end
numbers_only = [e.text[:-1] for e in numbers_in_strongs]

print(numbers_only)

n = '80g'.upper()

if n not in numbers_only:
    print("course", n, "not found")
    exit(1)

index = numbers_only.index(n)

title_tag = numbers_in_strongs[index].next_sibling.next_sibling
title_text = title_tag.text[:-1]
description_tag = title_tag.next_sibling.next_sibling.next_sibling.next_sibling
description_text = description_tag[2:]
print("\"" + title_text + "\"")
print("----")
print("\"" + description_text + "\"")
