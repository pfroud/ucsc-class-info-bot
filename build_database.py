"""
Given a string of a department and course number, pulls information about the course from the registrar.
"""

import requests
from bs4 import BeautifulSoup
from pprint import pprint
import sys

departments = ["acen", "amst", "anth", "aplx", "ams", "arab", "art", "artg", "astr", "bioc", "biol", "bioe", "bme",
               "chem", "chin", "clei", "clni", "clte", "cmmu", "cmpm", "cmpe", "cmps", "cowl", "ltcr", "cres", "crwn",
               "danm", "eart", "econ", "educ", "ee", "engr", "ltel", "envs", "etox", "fmst", "film", "fren", "ltfr",
               "game", "germ", "ltge", "gree", "ltgr", "hebr", "hndi", "his", "havc", "hisc", "humn", "ism", "ital",
               "ltit", "japn", "jwst", "krsg", "laad", "latn", "lals", "ltin", "lgst", "ling", "lit", "math", "merr",
               "metx", "ltmo", "musc", "oaks", "ocea", "phil", "phye", "phys", "poli", "prtr", "port", "ltpr", "psyc",
               "punj", "russ", "scic", "socd", "socs", "socy", "span", "sphs", "spss", "ltsp", "stev", "tim", "thea",
               "ucdc", "wmst", "ltwl", "writ", "yidd", "ce", "cs"]


class CourseDatabase:
    def __init__(self):
        self.depts = dict()  # set up an empty dictionary

    def add_dept(self, new_dept):
        self.depts[new_dept.name] = new_dept

    def __str__(self):
        string = ""
        for dept_num, dept_obj in sorted(self.depts.items()):
            string += dept_num + ':\n' + str(dept_obj) + '\n'
        return string


class Department:
    def __init__(self, name):
        self.courses = dict()
        self.name = name

    def add_course(self, new_course):
        self.courses[new_course.number] = new_course

    def __str__(self):
        string = ""
        for course_num, course_obj in sorted(self.courses.items()):
            string += '   ' + course_num + ': ' + str(course_obj) + '\n'
        return string


class Course:
    def __init__(self, dept, number, name, description):
        self.name = name
        self.description = description
        self.dept = dept
        self.number = number

    def __str__(self):
        return self.name


def build_department_object(dept_name_in):
    # print("running on \"" + dept_name_in + "\"")

    course_department = dept_name_in

    if course_department == 'CS':
        course_department = "CMPS"
    if course_department == 'CE':
        course_department = "CMPE"
    if course_department == 'ECON':
        sys.stderr.write('this breaks for econ because they didn\'t put 1 in bold\n')
        return

    new_dept = Department(course_department)

    url = "http://registrar.ucsc.edu/catalog/programs-courses/course-descriptions/" + course_department.lower() + ".html"

    request_result = requests.get(url)

    status_code = request_result.status_code
    if status_code != 200:
        raise Exception(url + ' returned ' + str(status_code) + '\n')

    soup = BeautifulSoup(request_result.text, 'html.parser')

    h2s = soup.select("h2")

    # a division is lower-division, upper-division, or graduate
    division_p_tags = [h2.next_sibling.next_sibling for h2 in h2s]

    # print(division_p_tags)

    every_strong_tag = [p.select("strong") for p in division_p_tags]

    # see http://stackoverflow.com/a/406296
    every_strong_flattened = [s for inner in every_strong_tag for s in inner]

    # pprint(every_strong_flattened)

    # get every 3rd element - need to do something else!!
    numbers_in_strongs = [every_strong_flattened[x] for x in range(len(every_strong_flattened)) if x % 3 == 0]

    for num_tag in numbers_in_strongs:
        number = num_tag.text[:-1]
        # print("doing", number)

        title_tag = num_tag.next_sibling.next_sibling
        name = title_tag.text[:-1]

        description_tag = title_tag.next_sibling.next_sibling.next_sibling.next_sibling
        description = description_tag[2:]

        new_dept.add_course(Course(course_department, number, name, description))

    return new_dept


def build_database():
    db = CourseDatabase()
    for current_dept in ['artg', 'hebr', 'bioc', 'punj']:
        db.add_dept(build_department_object(current_dept))
    return db


print(build_database())
