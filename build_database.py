"""
Given a string of a department and course number, pulls information about the course from the registrar.
"""

import requests
import re
from bs4 import BeautifulSoup
from pprint import pprint

works = [
    "acen", "aplx", "ams", "art", "artg", "astr", "bioc", "mcdb", "eeb", "bme",
    "chem", "chin", "clni", "clte", "cmmu", "cmpm", "cmpe", "cmps", "cowl", "cres", "crwn",
    "danm", "eart", "educ", "ee", "envs", "fmst", "film", "fren", "game", "gree", "hebr", "his", "hisc",
    "ital", "japn", "jwst", "krsg", "laad", "latn", "lals", "lgst", "ling", "math", "merr",
    "metx", "musc", "oaks", "ocea", "phil", "phye", "phys", "poli", "port", "punj", "russ", "scic", "socd",
    "socy", "span", "sphs", "stev", "tim", "thea", "ucdc", "writ", "yidd", 'prtr', 'anth', 'psyc']

not_work = []


# taken out psyc bc some stuff is indented
# taken out clei because everything in one strong tag. also havc 152 is one strong tag.
# subsets of lit page: ltcr (creative writing), ltel (English-Language Literatures), ltfr (French Literature),
#    ltge (German Literature), ltgr (Greek Literature), ltin (latin literature), ltpr (Pre & Early Modern Literature),
#    ltmo (Modern Literary Studies), ltsp (Spanish/Latin Amer/Latino Lit), ltwl (World Lit & Cultural Studies), ltit
# taken out econ and germ because the 1 doesn't start bold


class CourseDatabase:
    def __init__(self):
        self.depts = dict()  # set up an empty dictionary

    def add_dept(self, new_dept):
        self.depts[new_dept.name] = new_dept

    def __str__(self):
        string = 'Database with ' + str(len(self.depts)) + ' departments.\n'
        for dept_num, dept_obj in sorted(self.depts.items()):
            string += '\n' + dept_num + ': ' + str(dept_obj)
        return string


class Department:
    def __init__(self, name):
        self.courses = dict()
        self.name = name

    def add_course(self, new_course):
        self.courses[new_course.number] = new_course

    def __str__(self):
        string = 'Department with ' + str(len(self.courses)) + " courses.\n"
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
        return '\"' + self.name + "\""


regex = re.compile("[0-9]+[A-Za-z]?\.")


def has_course_number(num_string):
    return regex.match(num_string) is not None


def is_last_course_in_p(strong_tag):
    # print('-----------------------')
    # print('strong_tag is', strong_tag)
    parent_p = strong_tag.parent
    strongs_in_p = parent_p.find_all('strong')
    # print('length of that array is', len(strongs_in_p))
    # pprint(strongs_in_p)
    index = strongs_in_p.index(strong_tag)
    distance_to_end = len(strongs_in_p) - index
    # print('   distance_to_end is', distance_to_end)
    return distance_to_end <= 4
    # print('index is', index)
    # print('distance to end is', len(strongs_in_p)-index)
    # print('-----------------------')


# psyc "118. Special Topics in Developmental Psychology. F,W,S": distance to end is 3
# anth "130. Enthographic Area Studies.": distance to end is 2
# prtr "20. Dance/Theater Practicum.": distance to end is 2

# prediction - prtr "22. Art Practicum (2 credits). *" should have dist to end is 4


def is_next_p_indented(num_tag):
    return num_tag.parent.next_sibling.next_sibling.get('style') == 'margin-left: 30px;'


def in_indented_paragraph(num_tag):
    return num_tag.parent.get('style') == 'margin-left: 30px;'


def build_department_object(dept_name_in):
    print("running on \"" + dept_name_in + "\"")

    course_department = dept_name_in

    if course_department == 'CS':
        course_department = "CMPS"
    if course_department == 'CE':
        course_department = "CMPE"

    new_dept = Department(course_department)

    url = "http://registrar.ucsc.edu/catalog/programs-courses/course-descriptions/" + course_department + ".html"

    request_result = requests.get(url)

    status_code = request_result.status_code
    if status_code != 200:
        raise Exception(url + ' returned ' + str(status_code) + '\n')

    soup = BeautifulSoup(request_result.text, 'html.parser')

    every_strong_tag = soup.select("div.main-content strong")

    numbers_in_strongs = []

    for tag in every_strong_tag:
        if has_course_number(tag.text):
            numbers_in_strongs.append(tag)

    for num_tag in numbers_in_strongs:

        number = num_tag.text[:-1]
        print("doing", number)

        if is_last_course_in_p(num_tag) and is_next_p_indented(num_tag) and not in_indented_paragraph(num_tag):
            print('   SKIPPING num_tag \"' + num_tag.text + "\"<<<<<<<<<<<<<<<<<<<<<")
            continue

        title_tag = num_tag.next_sibling.next_sibling
        name = title_tag.text[:-1]

        description_tag = title_tag.next_sibling.next_sibling

        while description_tag.name == 'strong' or description_tag.name == 'br' or description_tag.name == 'h2':
            description_tag = description_tag.next_sibling.next_sibling

        if description_tag.name == 'p':
            description_tag = description_tag.next_sibling

        description = description_tag[2:]

        new_dept.add_course(Course(course_department, number, name, description))

    return new_dept


def build_database():
    db = CourseDatabase()
    for current_dept in not_work:
        db.add_dept(build_department_object(current_dept))
    return db


build_database()
