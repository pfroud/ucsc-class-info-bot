"""
Given a string of a department and course number, pulls information about the course from
https://pisa.ucsc.edu/cs9/prd/sr9_2013/index.php.
"""

import requests  # html requests
from bs4 import BeautifulSoup  # html parser

# Taken from chrome inspector. Go to Network tab before clicking Search on class search form.
# Click Search, then click on index.php in the Network tab.
# In the Headers tab, scroll down to Form Data. This is the HTML POST data.
payload = {
    'action': 'results',
    'binds[:term]': '2160',
    'binds[:reg_status]': 'all',
    'binds[:subject]': 'CMPS',
    'binds[:catalog_nbr_op]': '=',
    'binds[:catalog_nbr]': '5j',
    'binds[:title]': '',
    'binds[:instr_name_op]': '=',
    'binds[:instructor]': '',
    'binds[:ge]': '',
    'binds[:crse_units_op]': '=',
    'binds[:crse_units_from]': '',
    'binds[:crse_units_to]': '',
    'binds[:crse_units_exact]': '',
    'binds[:days]': '',
    'binds[:times]': '',
    'binds[:acad_career]': ''}

# do the request. you get a page of class search results.
r = requests.post('https://pisa.ucsc.edu/class_search/', data=payload)

# feed search results page to parser
soup = BeautifulSoup(r.text, 'html.parser')

# Grotesque element selection. we want class_data for a link to a class.
# Get the <a> element which is the Class Title link in the first row of results.
# Get the only element in the resulting array. Get the href string, then split by '=' and get second element.
encoded_course = soup.select('tbody td:nth-of-type(3) a')[0]['href'].split('=')[2]

# stick class_data to the end of this thing. you'll get a page with course information.
result_url = 'https://pisa.ucsc.edu/class_search/index.php?action=detail&class_data=' + encoded_course
print(result_url)

# feed course info page to parser
soup = BeautifulSoup(result_url, 'html.parser')

# this doesn't work yet
# course_name = soup.select("table.PALEVEL0SECONDARY tr:nth-of-type(2) td")
course_name = soup.select("table.PALEVEL0SECONDARY")
print("course_name is", course_name)

course_description = soup.select("table.detail_table")
print("course_description is", course_description)
