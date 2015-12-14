"""
Given a string of a department and course number, pulls information about the course from
https://pisa.ucsc.edu/cs9/prd/sr9_2013/index.php.
"""
from pprint import pprint

import requests
from bs4 import BeautifulSoup

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

r = requests.post('https://pisa.ucsc.edu/class_search/', data=payload)

soup = BeautifulSoup(r.text, 'html.parser')

encoded_course = soup.select('tbody td:nth-of-type(3) a')[0]['href'].split('=')[2]

result_url = 'https://pisa.ucsc.edu/class_search/index.php?action=detail&class_data=' + encoded_course

print(result_url)
