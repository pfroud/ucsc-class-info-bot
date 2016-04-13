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

A course *mention* occurs when a redditor names one or more courses in a post or comment. See section [mention types](#mention-types).


A course *object* is an instance of the [`Course`](https://github.com/pfroud/ucsc-class-info-bot/blob/4dae0bb220513ce29fb889410570b1397c3efbde/db_core.py#L87-L99) class from `db_core.py`. Such an instance knows its department, number, name, and description. The course number is actually a string because courses can have a letter after the numeric part.

For example, the course object with department "CMPS" and number "12B" has the title "Introduction to Data Structures" and the description starts with "Teaches students to implement common data structures and the algorithms..."


##The course database 
The course database looks up a course's name and description using its department and number.  In other words, we input a course *mention* and get a Course *object*. The files `db_core.py`  and `db_extra.py` do everything.

###Database structure
The database stores a [Pickled](https://docs.python.org/3/library/pickle.html)  instance of `CourseDatabase`, which has a `dict<string, Department>`. A `Department` instance has a `dict<string, Course>`, and a `Course` instance has department, number, name, description.

You can see the log from building it at [misc/db build log.txt](misc/db build log.txt). You can see what it looks like when you print it at [misc/db print.txt](misc/db print.txt).

###Implementation attempts

I tried a few ways to make the database work. All the HTML parsing is done by [Beautiful Soup](http://www.crummy.com/software/BeautifulSoup/).

####First attempt - class search page

My original idea for scraping course info was through the [class search](https://pisa.ucsc.edu/class_search/) page. The script works but is a pain in the ass because I need to send a POST request *and* parse the returned HTML page. It would not work for building the database because the class search page only lists courses offered that quarter.

The implementation is preserved in [misc/get_course_info.py](misc/get_course_info.py) for your viewing pleasure.

####Second attempt - department websites

My second idea was to scrape course info from the website of each academic department. There were multiple problems.

First, departments don't use a consistent enough URL. Comparison of these URLs is left as an exercise to the reader(!): [Chemistry](http://chemistry.ucsc.edu/academics/courses/course-catalog.php), [History](http://history.ucsc.edu/courses/catalog-view.php), [Mathematics](http://www.math.ucsc.edu/courses/course-catalog.php), [Linguistics](http://linguistics.ucsc.edu/courses/course-catalog-view.php), [Anthropology](http://anthro.ucsc.edu/courses/course_catalog.php).

Second, some courses are inside another department. For example, classes in Chinese (CHIN), French (FREN), and German (GERM) are all listed on the [Language department's](http://language.ucsc.edu/courses/course-catalog.php) page.

Third, some departments use a custom layout to list course info. For example, compare the standard layout used by the [History department](http://history.ucsc.edu/courses/catalog-view.php) to the custom layouts used by the [Art department](http://art.ucsc.edu/courses/2015-16) and the [School of Engineering](https://courses.soe.ucsc.edu/).

All of these aspects would've made scraping extremely difficult.

####Third, successful, attempt - Registrar website

The third version works.  The Registrar lists every course in every department with a beautifully consistent URL: `http://registrar.ucsc.edu/catalog/programs-courses/course-descriptions/<dept_code>.html`, where `<dept_code>` is the department code. Humans can go to [`index.html`](http://registrar.ucsc.edu/catalog/programs-courses/course-descriptions/index.html) and choose a department on the left. This option is clearly the best. I didn't use it from the beginning because it's hard to find: from the [Registrar homepage](http://registrar.ucsc.edu/), go to Quick Start Guide > Catalog > Fields of Study > Programs and Courses > Course Descriptions.

The file `db_core.py` handles most departments, but `db_extra.py` is needed to handle the following special cases.

First, some courses are indented in their own paragraph. For example, [Psychology](http://registrar.ucsc.edu/catalog/programs-courses/course-descriptions/psyc.html) 118A-D are all indented under the header for 118. The functions [`is_next_p_indented()`](https://github.com/pfroud/ucsc-class-info-bot/blob/4dae0bb220513ce29fb889410570b1397c3efbde/db_extra.py#L37-L56) and [`in_indented_paragraph()`](https://github.com/pfroud/ucsc-class-info-bot/blob/4dae0bb220513ce29fb889410570b1397c3efbde/db_extra.py#L59-L67) check for this case.

Second, the [Literature](http://registrar.ucsc.edu/catalog/programs-courses/course-descriptions/lit.html) department contains courses from multiple department codes. For example, Creative Writing (LTCR) and and Latin Literature (LTIN) classes are both under `lit.html`. Consequently the lit page is scraped by its own function, [`get_lit_depts()`](https://github.com/pfroud/ucsc-class-info-bot/blob/4dae0bb220513ce29fb889410570b1397c3efbde/db_extra.py#L135-L164), with help from the function [`get_real_lit_dept()`](https://github.com/pfroud/ucsc-class-info-bot/blob/4dae0bb220513ce29fb889410570b1397c3efbde/db_extra.py#L118-L132). The page uses subdepartment *names* but we care about subdepartment *codes*, so the dict [`lit_department_codes`](https://github.com/pfroud/ucsc-class-info-bot/blob/4dae0bb220513ce29fb889410570b1397c3efbde/db_extra.py#L6-L17) maps names to codes. For example, "﻿Modern Literary Studies" maps to "LTMO" and "﻿Greek Literature" maps to "LTGR".

Third, some departments deviate from the standard HTML layout. For almost every department, key information about a course is contained in three `<strong>` tags. Here's an example from [Biomolecular Engineering (BME)](http://registrar.ucsc.edu/catalog/programs-courses/course-descriptions/bme.html):

```
<strong>110.</strong>
<strong>Computational Biology Tools.</strong>
<strong>F,W</strong>
```
The "F,W" indicates which general education requirements are satisfied by that course. To build the database, I start by finding `<strong>` tags containing numbers.

However, *one single department does this differently*. [College Eight (CLEI)](http://registrar.ucsc.edu/catalog/programs-courses/course-descriptions/clei.html) puts the entire header in one `<strong>` tag:
```
<strong>81C. Designing a Sustainable Future. S</strong>
```
So, there's one [stupid special case](https://github.com/pfroud/ucsc-class-info-bot/blob/4dae0bb220513ce29fb889410570b1397c3efbde/db_core.py#L219).

Furthermore, two departments miss the first `<strong>` tag. The first courses on the [German](http://registrar.ucsc.edu/catalog/programs-courses/course-descriptions/germ.html) and [Economics](http://registrar.ucsc.edu/catalog/programs-courses/course-descriptions/econ.html) pages look like this:
```
1. <strong>First-Year German.</strong>
<strong>F</strong>
```
Because I only look in `<strong>` tags, I won't find course 1. So, that's another [stupid special case](https://github.com/pfroud/ucsc-class-info-bot/blob/4dae0bb220513ce29fb889410570b1397c3efbde/db_core.py#L224).


The latest special cases arise from inconsistent department naming. The Registrar's page for the [Ecology and Evolutionary Biology department ](http://registrar.ucsc.edu/catalog/programs-courses/course-descriptions/eeb.html) is on `eeb.html`, but the [class search](https://pisa.ucsc.edu/class_search/) reveals that the courses use the dapertment code `BIOE`. Similarly, the  Registrar listing for  the [Molecular, Cell, and Developmental Biology department ](http://registrar.ucsc.edu/catalog/programs-courses/course-descriptions/mcdb.html) is on `mcdb.html` but the courses use the department code `BIOL`. [Two more conditionals](https://github.com/pfroud/ucsc-class-info-bot/blob/4dae0bb220513ce29fb889410570b1397c3efbde/db_core.py#L198-L206) address this issue.

##Finding course mentions

A course mention occurs when a redditor names one or more courses in a post or comment.

I pulled the list of department codes from the source of the [class search](https://pisa.ucsc.edu/class_search/) page (`<select id="subject">`), but it includes defuct and renamed departments. For example, the Arabic department (ARAB) is gone and Environmental Toxicology (ETOX) is now Microbiology and Environmental Toxicology (METX). Possible departments appear in the regex [`_pattern_depts`](https://github.com/pfroud/ucsc-class-info-bot/blob/4dae0bb220513ce29fb889410570b1397c3efbde/mention_parse.py#L10-L16).


### Mention types

The bot can see three types of mentions. All of these are case-insensitive.

A course 'number' is actually a string and may contain one optional letter at the end.

1. **Normal mention:** department code, optional space, and course number. For example, "CMPS 12B" and "econ105" are normal mentions.
	* Specified by regex [`_pattern_mention_normal`](https://github.com/pfroud/ucsc-class-info-bot/blob/4dae0bb220513ce29fb889410570b1397c3efbde/mention_parse.py#L21-L22).
1. **Letter-list mention:** shorthand for multiple courses with the same number but different letters: one department, a string of digits, then a list of letters. For example, "CE 129A/B/C" is a letter-list mention containing CE 129A, CE 129B, and CE 129C.
	* Specified by regex [`_pattern_mention_letter_list`](https://github.com/pfroud/ucsc-class-info-bot/blob/4dae0bb220513ce29fb889410570b1397c3efbde/mention_parse.py#L18-L19).
	* Function [`_parse_letter_list()`](https://github.com/pfroud/ucsc-class-info-bot/blob/4dae0bb220513ce29fb889410570b1397c3efbde/mention_parse.py#L36-L55) splits a letter-list mention into normal mentions.
1. **Multi-mention:** shorthand for multiple courses in the same department: one department and a list of course numbers. For example, "Math 21, 23b, and 100" is a multi-mention containing Math 21, Math 23, and Math 100.
	* Not specified by a single regex.
	* The function [`_parse_multi_mention()`](https://github.com/pfroud/ucsc-class-info-bot/blob/4dae0bb220513ce29fb889410570b1397c3efbde/mention_parse.py#L58-L92) splits a multi-mention into normal mentions.
	* You can have a letter-list mention in a multi-mention, like "CS 8a, 15, or 163w/x/y/z".

Simpler regular expressions are combined to form [`_pattern_final`](https://github.com/pfroud/ucsc-class-info-bot/blob/4dae0bb220513ce29fb889410570b1397c3efbde/mention_parse.py#L30-L33), which is used to search strings.

### Result

The file `mention_search_posts.py`, the function [`find_mentions()`](https://github.com/pfroud/ucsc-class-info-bot/blob/4dae0bb220513ce29fb889410570b1397c3efbde/mention_search_posts.py#L111-L150) gets new posts from /r/UCSC then parses everything using `mention_parse.py`.

If `find_mentions()` is called from `reddit_bot.py`, it returns a `PostWithMentions` instance to be immediately processed; if `mention_search_posts.py` is ran on its own from the console, it is Pickled (serialized) and saved to disk. The [`PostWithMentions`](https://github.com/pfroud/ucsc-class-info-bot/blob/91cfc3cc31ffb70f6ea51ffdac6665bbd17ed1cd/find_mentions.py#L15-L23) class is a container which holds the ID of a submission and a list of course mentions found in that submission.


##Posting comments

Load two data structures from disk to begin:

* posts which we've already commented on with course info, from the last run of `post_comments.py`
* the course database, generated by `build_database.py`

If `post_comments.py` is ran on its own from the console, it loads mentions found from the last run of `mention_search_posts.py`. If the function `post_comments()` is called from `reddit_bot.py`, data about found mentions is passed directly as a parameter to the function.

Look through the list of found mentions. If a post doesn't already have a one of our comments, add one. If it does already have a comment, compare the class mentions most recently found with the classes that are already in the comment. If there are new ones, update the comment.


## Known bugs

* In the comment, classes are sorted by department name (I think) instead of by order mentioned.

## Future work

* Make the bot see mentions of some department names instead of department codes, e.g. "chemistry 103" instead of "chem 103".
