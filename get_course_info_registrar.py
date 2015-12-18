"""
Given a string of a department and course number, pulls information about the course from the registrar.
"""

import requests
from bs4 import BeautifulSoup
from pprint import pprint
import sys


class Course:
    def __init__(self, name, description, dept, number):
        self.name = name
        self.description = description
        self.dept = dept
        self.number = number

    # cmps 1: intro to things
    def __str__(self):
        return self.dept + " " + self.number + ": " + self.name


def get_course_object(mention_string):
    print("running on \"" + mention_string + "\"")

    split_array = mention_string.split(' ')
    course_department = split_array[0].upper()  # server needs department to be all caps
    course_number = split_array[1].upper()

    if course_department == 'CS':
        course_department = "CMPS"
    if course_department == 'CE':
        course_department = "CMPE"
    if course_department == 'ECON':
        sys.stderr.write('this breaks for econ because they didn\'t put 1 in bold\n')
        return

    url = "http://registrar.ucsc.edu/catalog/programs-courses/course-descriptions/" + course_department.lower() + ".html"

    print('going to get page')
    request_result = requests.get(url)
    print('got page')

    status_code = request_result.status_code
    if status_code != 200:
        sys.stderr.write(url + ' returned ' + str(status_code) + '\n')
        return

    soup = BeautifulSoup(request_result.text, 'html.parser')

    h2s = soup.select("h2")

    # a division is lower-division, upper-division, or graduate
    division_p_tags = [h2.next_sibling.next_sibling for h2 in h2s]

    # print(division_p_tags)

    every_strong_tag = [p.select("strong") for p in division_p_tags]

    # see http://stackoverflow.com/a/406296
    every_strong_flattened = [s for inner in every_strong_tag for s in inner]

    pprint(every_strong_flattened)

    # get every 3rd element - need to do something else!!
    numbers_in_strongs = [every_strong_flattened[x] for x in range(len(every_strong_flattened)) if x % 3 == 0]

    # the [:-1] slice takes off the period from the end
    numbers_only = [e.text[:-1] for e in numbers_in_strongs]

    # print(numbers_only)

    if course_number not in numbers_only:
        sys.stderr.write("course " + course_number + " not found\n")
        return

    index = numbers_only.index(course_number)

    title_tag = numbers_in_strongs[index].next_sibling.next_sibling
    title_text = title_tag.text[:-1]
    description_tag = title_tag.next_sibling.next_sibling.next_sibling.next_sibling
    description_text = description_tag[2:]

    return Course(title_text, description_text, course_department, course_number)


print('> thing returns', get_course_object('anth 81a'))
