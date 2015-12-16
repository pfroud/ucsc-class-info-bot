"""
Given a string of a department and course number, pulls information about the course from
https://pisa.ucsc.edu/cs9/prd/sr9_2013/index.php.
"""

import requests  # html requests
from bs4 import BeautifulSoup  # html parser


# http://www.crummy.com/software/BeautifulSoup/bs4/doc/

class Course:
    def __init__(self, name, description, dept, number, link):
        self.name = name
        self.description = description
        self.dept = dept
        self.number = number
        self.link = link

    def __str__(self):
        return self.name


def get_course_info(course_dept_number_string):
    """
    Given string of department and number, returns array of course title and description.
    :param course_dept_number_string: string "cmps 1", must be a space between department and number
    :return: a Course object
    """

    split_array = course_dept_number_string.split(' ')
    course_department = split_array[0].upper()  # server needs department to be all caps
    course_number = split_array[1]

    # print("course_department is \"" + course_department + "\" and course_number is \"" + course_number + "\"")

    # Taken from chrome inspector. Go to Network tab before clicking Search on class search form.
    # Click Search, then click on index.php in the Network tab.
    # In the Headers tab, scroll down to Form Data. This is the HTML POST data.
    payload = {
        'action': 'results',
        'binds[:term]': '2160',
        'binds[:reg_status]': 'all',
        'binds[:subject]': course_department,
        'binds[:catalog_nbr_op]': '=',
        'binds[:catalog_nbr]': course_number,
    }

    # do the request for the search results page
    request_result = requests.post('https://pisa.ucsc.edu/class_search/', data=payload)

    # error check
    status_code = request_result.status_code
    if status_code != 200:
        raise Exception("Request for search results page returned " + status_code)

    # feed search results page to parser
    soup = BeautifulSoup(request_result.text, 'html.parser')

    # Grotesque element selection. we want class_data for a link to a class.
    # Get the <a> element which is the Class Title link in the first row of results.
    # Get the only element in the resulting array. Get the href string, then split by '=' and get second element.
    encoded_course = soup.select('tbody td:nth-of-type(3) a')[0]['href'].split('=')[2]

    if encoded_course is None:
        raise Exception("Couldn't find link in search results page")

    # stick class_data to the end of this thing. you'll get a page with course information.
    result_url = 'https://pisa.ucsc.edu/class_search/index.php?action=detail&class_data=' + encoded_course

    # loads the course info page
    request_result = requests.get(result_url)

    # error check
    status_code = request_result.status_code
    if status_code != 200:
        raise Exception("Request for search results page returned " + status_code)

    # feed course info page to parser
    soup = BeautifulSoup(request_result.text, 'html.parser')

    # this does now work
    course_name = soup.select("table.PALEVEL0SECONDARY tr:nth-of-type(2) td")[0].text
    if course_name is None:
        raise Exception("Couldn't find course name")
    # http://stackoverflow.com/questions/10993612/python-removing-xa0-from-string
    course_name = course_name.replace(u'\xa0', u' ')
    course_name = course_name.replace('  ', ': ')

    course_description = soup.select("table.detail_table")[1].select("td")[0].text
    if course_description is None:
        raise Exception("Couldn't find course description")

    return Course(course_name, course_description, course_department, course_number, result_url)


thing = get_course_info('CMPS 5j')
print(thing)
