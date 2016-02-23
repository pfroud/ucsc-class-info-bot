# /r/UCSC class info bot

Looks through the [/r/UCSC](https://www.reddit.com/r/ucsc) subreddit for mentions of classes and comments with information from the course catalog.

Will go on [/u/ucsc-class-info-bot](https://www.reddit.com/user/ucsc-class-info-bot).


## Inception
In September 2015 I threw this in a text doc and forgot about it:

>idea - bot that gives class info when someone mentions it in a comment  

>------------------------------------------------------------------------

>So you look for a string that matches a department code followed by /[0-9]+[A-Za-z]?/ or something

>You can get the codes from the \<option\>s on the Subject dropdown [here](https://pisa.ucsc.edu/cs9/prd/sr9_2013/index.php), which is the iframe inside the Student Center on my.ucsc.edu

>And you magically look up the class name and description, either through a class search, or on each department's website.

>It's so easy!

Two months later, I came across the file with the idea and decided to bring it to life.

To the surprise of absolutely nobody, it was not *'so easy'*, although I am still using that regex.


##Terminology
A course *mention* is a string of a department code followed immediately by a course number. All recognized department codes are in [this list](https://github.com/pfroud/ucsc-class-info-bot/blob/183e434a0a4f2894f4e52b12300185a1c1ba2e81/build_database.py#L15-L20). A course number is one or more digits fillowed by an optional letter, specified by the regular expression `/[0-9]+[A-Za-z]?/`. For example, "CMPS 12B".

Note - I pulled the list of department codes from the source of the [class search](https://pisa.ucsc.edu/class_search/) page (`<select id="subject"`), but the raw list can't be used.

A course *object* is an instance of the [`Course`](https://github.com/pfroud/ucsc-class-info-bot/blob/183e434a0a4f2894f4e52b12300185a1c1ba2e81/build_database.py#L103-L115) class from `build_databse.py`. A `Course` instance knows its department, number, name, and description. For example, the name CMPS 12B is "Introduction to Data Structures" and the description starts with "Teaches students to implement common data structures and the algorithms..."

##The course database
The course database lets us input a course *mention* and get a Course *object*. In other words, the database looks up a course's name and description from its department and number.

mention [Beautiful Soup](http://www.crummy.com/software/BeautifulSoup/) somewhere.

###Implementation attempts

####First attempt - class search

My first attempt was by sending POST requests to the [class search](https://pisa.ucsc.edu/class_search/) page. This was kind of a pain in the ass because you had to deal with sending the request *and* parsing the HTML page it returns, which calls for grotesque element selection. The class search only lists courses offered that quarter, so I couldn't use it to build my database.

You can see the file that did this in [misc/get_course_info_old.py](misc/get_course_info_old.py).

####Second attempt - department websites

My second attempt was to scrape course info from departments' websites. There were multiple problems with this.

First, departments didn't use a consistent enough URL. Many departments list their courses at `http://department.ucsc.edu/courses/course-catalog.php`, but not all. For example, the linguistics department has theirs at `course-catalog-view.php`, anthropology has theirs at `course_catalog.php`, and history at `catalog-view.php`.

Second, some departments(?) were inside another department. For example, mentions for languages like CHIN (Chinese), FREN (French), and GERM (German) all must go to `language.ucsc.edu`.

Third, some departments used their own custom style to list course info. For example, compare [history's catalog](http://history.ucsc.edu/courses/catalog-view.php), which uses the standard layout, to the custom layout used by the [art department](http://art.ucsc.edu/courses/2015-16) or the [school of engineering](https://courses.soe.ucsc.edu/).

####Third, successful, attempt - registrar

My third attempt was successful. I should've done this from the beginning, but had to look harder to find it. The registrar has listings of every course in every department, listed in a beautifully consistent format: `http://registrar.ucsc.edu/catalog/programs-courses/course-descriptions/department.html"`. And yet, of course, there are some special cases and weirdness.

First, some courses are indented. See [psychology](http://registrar.ucsc.edu/catalog/programs-courses/course-descriptions/psyc.html) 118A-D. In the [literate](http://registrar.ucsc.edu/catalog/programs-courses/course-descriptions/lit.html) department, courses that use different codes are all listed under literature. For example, the single page about literature has info about LTCR (creative writing) and LTIN (Latin Literature). The mapping of name to code is in [this dict](https://github.com/pfroud/ucsc-class-info-bot/blob/183e434a0a4f2894f4e52b12300185a1c1ba2e81/build_database.py#L24-L35).

Second, some departments have a little different HTML format. For almost every department, I scrape by looking through `<strong>` tags for the target course number. In well-behaved departments, the header for a course looks like this:

```
<strong>110.</strong>
<strong>Computational Biology Tools.</strong>
<strong>F,W</strong>
```
(The "F,W" indicates general education codes.) However, *one single department doesn't do this*. [College Eight](http://registrar.ucsc.edu/catalog/programs-courses/course-descriptions/clei.html) puts the entire header in one `<strong>` tag:
```
<strong>81C. Designing a Sustainable Future. S</strong>
```
So, there's one [stupid special case](https://github.com/pfroud/ucsc-class-info-bot/blob/183e434a0a4f2894f4e52b12300185a1c1ba2e81/build_database.py#L318).

Third, two departments miss the first strong tag. The first courses on the [German](http://registrar.ucsc.edu/catalog/programs-courses/course-descriptions/germ.html) and [economics](http://registrar.ucsc.edu/catalog/programs-courses/course-descriptions/econ.html) pages look like this:
```
1.
<strong>First-Year German.</strong>
<strong>F</strong>
```
That means if I'm looking for course number one, I won't find it because I only look in `<strong>` tags. So, that's another [stupid special case](https://github.com/pfroud/ucsc-class-info-bot/blob/183e434a0a4f2894f4e52b12300185a1c1ba2e81/build_database.py#L323).

###Result
You can see what it looked like as it was being built at [misc/db build log.txt](misc/db build log.txt). You can see what it looks like when you print it at [misc/db print.txt](misc/db print.txt).


##Finding course mentions

##Posting comments



## Known bugs

* In the comment, classes are sorted by department name. This might not actually be true.
Ideally they would be sorted by the order in which they're mentioned.
