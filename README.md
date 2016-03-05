# /r/UCSC class info bot

Finds posts on the [/r/UCSC](https://www.reddit.com/r/ucsc) mentioning classes and comments with information about those classes.

Lives on [/u/ucsc-class-info-bot](https://www.reddit.com/user/ucsc-class-info-bot).

## Inception
In September 2015, I threw this in a file called `ucsc reddit bot idea.txt` and forgot about it:

>idea - bot that gives class info when someone mentions it in a comment  

>------------------------------------------------------------------------

>So you look for a string that matches a department code followed by /[0-9]+[A-Za-z]?/ or something

>You can get the codes from the \<option\>s on the Subject dropdown [here](https://pisa.ucsc.edu/cs9/prd/sr9_2013/index.php), which is the iframe inside the Student Center on my.ucsc.edu

>And you magically look up the class name and description, either through a class search, or on each department's website.

>It's so easy!

Two months later, I ran into the file again and decided to bring it to life.

To the surprise of absolutely nobody, it was not *'so easy'*, although I am still using that regex to find mentions.


##Terminology

From here on I use 'course' instead of 'class' because `class` is a reserved Python keyword.

A course *mention* is a case-insensitive string of a department code followed immediately by a course number. For example, "CMPS 12B" and "econ 105" are mentions. All recognized department codes are in [this list](https://github.com/pfroud/ucsc-class-info-bot/blob/183e434a0a4f2894f4e52b12300185a1c1ba2e81/build_database.py#L15-L20). A course number is one or more digit(s) followed by an optional letter, specified by the regular expression `/[0-9]+[A-Za-z]?/`. 

A course *object* is an instance of the [`Course`](https://github.com/pfroud/ucsc-class-info-bot/blob/183e434a0a4f2894f4e52b12300185a1c1ba2e81/build_database.py#L103-L115) class from `build_databse.py`. Such an instance knows its department, number, name, and description. For example, the course object with department "CMPS" and number "12B" has the title "Introduction to Data Structures" and the description starts with "Teaches students to implement common data structures and the algorithms..."


##The course database 
The course database lets us input a course *mention* and get a Course *object*. In other words, the database looks up a course's name and description using its department and number. The file `build_database.py` is where the action happens.

###Database structure
The database stores an instance of `CourseDatabase`, which has a `dict<string, Department>`. A `Department` instance has a `dict<string, Course>`, and a `Course` instance has dept, number, name, description.

You can see what it looked like as it was being built at [misc/db build log.txt](misc/db build log.txt). You can see what it looks like when you print it at [misc/db print.txt](misc/db print.txt).

###Implementation attempts

All the HTML parsing is done by [Beautiful Soup](http://www.crummy.com/software/BeautifulSoup/).

####First attempt - class search page

My original idea for scraping course info was through the [class search](https://pisa.ucsc.edu/class_search/) page. It works but is a pain in the ass because I need to send a POST request *and* parse the returned HTML page. The real problem is that the class search page only lists courses offered that quarter, so I can't use it to build my database.

The implementation is preserved in [misc/get_course_info_old.py](misc/get_course_info_old.py) for your viewing pleasure.

####Second attempt - department websites

My second attempt was to scrape course info from the website of each academic department. There were multiple problems.

First, departments don't use a consistent enough URL. Comparison of these URLs is left as an exercise to the reader(!): [Chemistry](http://chemistry.ucsc.edu/academics/courses/course-catalog.php), [History](http://history.ucsc.edu/courses/catalog-view.php), [Mathematics](http://www.math.ucsc.edu/courses/course-catalog.php), [Linguistics](http://linguistics.ucsc.edu/courses/course-catalog-view.php), [Anthropology](http://anthro.ucsc.edu/courses/course_catalog.php).

Second, some courses are inside another department. For example, classes in Chinese (CHIN), French (FREN), and German (GERM) are all listed at [`language.ucsc.edu`](http://language.ucsc.edu/courses/course-catalog.php).

Third, some departments use their own custom style to list course info. For example, compare the standard layout used by the [History department](http://history.ucsc.edu/courses/catalog-view.php) to the custom layouts used by the [Art department](http://art.ucsc.edu/courses/2015-16) and the [School of Engineering](https://courses.soe.ucsc.edu/).

####Third, successful, attempt - registrar website

The third version works.  The registrar lists every course in every department with a beautifully consistent URL: `http://registrar.ucsc.edu/catalog/programs-courses/course-descriptions/department.html"`. This option is clearly the best. I didn't use it from the beginning because the link tree to find it isn't obvious: Quick Start Guide > Catalog > Fields of Study > Programs and Courses > Course Descriptions.

There are, of course, some special cases and weirdness.

First, some courses with the same number bit different letters are indented. For example, [Psychology](http://registrar.ucsc.edu/catalog/programs-courses/course-descriptions/psyc.html) 118A-D are all indented under the header for 118. The functions [`_is_next_p_indented()`](https://github.com/pfroud/ucsc-class-info-bot/blob/91cfc3cc31ffb70f6ea51ffdac6665bbd17ed1cd/build_database.py#L142-L161) and [`_in_indented_paragraph()`](https://github.com/pfroud/ucsc-class-info-bot/blob/91cfc3cc31ffb70f6ea51ffdac6665bbd17ed1cd/build_database.py#L164-L172) check for this case.

Second, the [Literature](http://registrar.ucsc.edu/catalog/programs-courses/course-descriptions/lit.html) department contains courses that use different department codes. For example, Creative Writing (LTCR) and and Latin Literature (LTIN) classes are both under `lit.html`. Consequently the lit page is scraped by its own function, [`_get_lit_depts()`](https://github.com/pfroud/ucsc-class-info-bot/blob/91cfc3cc31ffb70f6ea51ffdac6665bbd17ed1cd/build_database.py#L347-L375), with help from the function [`_get_real_lit_dept()`](https://github.com/pfroud/ucsc-class-info-bot/blob/91cfc3cc31ffb70f6ea51ffdac6665bbd17ed1cd/build_database.py#L330-L344). The page uses subdepartment *names* but we care about subdepartment *codes*, so the dict [`lit_department_codes`](https://github.com/pfroud/ucsc-class-info-bot/blob/91cfc3cc31ffb70f6ea51ffdac6665bbd17ed1cd/build_database.py#L23-L34) maps names to codes. For example, "﻿Modern Literary Studies" maps to "LTMO" and "﻿Greek Literature" maps to "LTGR".

Third, some departments deviate from the standard HTML layout. For almost every department, I scrape by looking through `<strong>` tags for the target course number. In well-behaved departments, the header for a course is in three tags. Here's an example from [Biomolecular Engineering (BME)](http://registrar.ucsc.edu/catalog/programs-courses/course-descriptions/bme.html):

```
<strong>110.</strong>
<strong>Computational Biology Tools.</strong>
<strong>F,W</strong>
```
The "F,W" indicates which general education requirements are satisfied by that course. In this example, if I'm looking for BME 110, I look for a `<strong>` tag on this page with contents equal to `"110."`.

However, *one single department doesn't do this*. [College Eight (CLEI)](http://registrar.ucsc.edu/catalog/programs-courses/course-descriptions/clei.html) puts the entire header in one `<strong>` tag:
```
<strong>81C. Designing a Sustainable Future. S</strong>
```
So, there's one [stupid special case](https://github.com/pfroud/ucsc-class-info-bot/blob/183e434a0a4f2894f4e52b12300185a1c1ba2e81/build_database.py#L318).

Furthermore, two departments miss the first `<strong>` tag. The first courses on the [German](http://registrar.ucsc.edu/catalog/programs-courses/course-descriptions/germ.html) and [Economics](http://registrar.ucsc.edu/catalog/programs-courses/course-descriptions/econ.html) pages look like this:
```
1. <strong>First-Year German.</strong>
<strong>F</strong>
```
That means if I'm looking for course number 1, I won't find it because I only look in `<strong>` tags. So, that's another [stupid special case](https://github.com/pfroud/ucsc-class-info-bot/blob/183e434a0a4f2894f4e52b12300185a1c1ba2e81/build_database.py#L323).


##Finding course mentions

In the file `find_mentions.py`, the function [`find_mentions()`](https://github.com/pfroud/ucsc-class-info-bot/blob/91cfc3cc31ffb70f6ea51ffdac6665bbd17ed1cd/find_mentions.py#L158-L185) gets new posts from /r/UCSC then calls [`_get_mentions_in_submission()`](https://github.com/pfroud/ucsc-class-info-bot/blob/91cfc3cc31ffb70f6ea51ffdac6665bbd17ed1cd/find_mentions.py#L26-L57) on each post.

To find mentions in a submission, call [`_get_mentions_in_string()`](https://github.com/pfroud/ucsc-class-info-bot/blob/91cfc3cc31ffb70f6ea51ffdac6665bbd17ed1cd/find_mentions.py#L65-L117) on its title, self text, and comments.

To find mentions in a string, iterate through a list of all available department codes. If a department code is found, use the regular expression [`_mention_regex`](https://github.com/pfroud/ucsc-class-info-bot/blob/91cfc3cc31ffb70f6ea51ffdac6665bbd17ed1cd/find_mentions.py#L11) will determine if it is followed by a course number.

I pulled the list of department codes from the source of the [class search](https://pisa.ucsc.edu/class_search/) page (`<select id="subject">`), but it includes defuct and renamed departments. For example, Arabic (ARAB) is gone and Environmental Toxicology (ETOX) is now Microbiology and Environmental Toxicology (METX).

The [`PostsWithMentions`](https://github.com/pfroud/ucsc-class-info-bot/blob/91cfc3cc31ffb70f6ea51ffdac6665bbd17ed1cd/find_mentions.py#L15-L23) class is a container which holds the ID of a submission and a list of course mentions found in that submission. I could use a `dict<string, list<string>>` but wanted to abstract as much as possible, although since Python is dynamically typed it doesn't help.

The result from running `find_mentions.py` is a list of  `PostsWithMentions` objects serialized and written to to disk.

##Posting comments

Load three data structures from disk to begin:

* posts which we've already commented on with course info, from the last run of `post_comments.py`
* posts with course mentions, from the last run of `find_mentions.py`
* the course database, generated by `build_database.py`

Look through the list of found mentions. If a post doesn't already have a one of our comments, add one. If it does already have a comment, compare the class mentions most recently found with the classes that are already in the comment. If there are new ones, update the comment.

I can only post a comment every ten minutes, so the program runs until a comment is posted or edited.


## Known bugs

* In the comment, classes are sorted by department name (I think) instead of by order mentioned

## Future work

* I don't have a rate limit anymore - make program run with single command
* Make the bot see mentions of some department names instead of department codes, e.g. "chemistry 103" instead of "chem 103"
