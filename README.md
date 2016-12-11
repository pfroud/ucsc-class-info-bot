# /r/UCSC class info bot

Searches for class mentions on the [/r/UCSC](https://www.reddit.com/r/ucsc) subreddit, then looks up and posts class information. 

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

A *course mention* occurs when a redditor names one or more courses in a post or comment. See section [mention types](#mention-types).

A *course object* is an instance of the [`Course`](https://github.com/pfroud/ucsc-class-info-bot/blob/4dae0bb220513ce29fb889410570b1397c3efbde/db_core.py#L87-L99) class from [`db_core.py`](https://github.com/pfroud/ucsc-class-info-bot/blob/master/db_core.py). A course object contains a course's department, number, name, and description.

A *department code* is a string of between two and four (inclusive) letters that is an abbreviation of a department's name. For example, `CMPS` is the department code for Computer Science.

A *course number* is a string, not an integer, because a course number might have a letter at the end. For example, `112`  and  `12A` are both course numbers. 

##The course database 
The course database uses a course's department and number to look up that course's name and description. In other words, we input a course *mention* and get a Course *object*. The files [`db_core.py`](https://github.com/pfroud/ucsc-class-info-bot/blob/master/db_core.py)  and [`db_extra.py`](https://github.com/pfroud/ucsc-class-info-bot/blob/master/db_extra.py) create the database.

###Database structure
The database stores a [Pickled](https://docs.python.org/3/library/pickle.html)  instance of `CourseDatabase`, which has a dict mapping a department code string to a `Department` instance. A `Department` instance has a dict mapping a course number to a `Course` instance. A `Course` instance has department, number, name, description. The relationship between these structures is illustrated below.

![Database structure diagram](img/database_structure_diagram.png?raw=true)

You can see the log from building the database at [misc/db build log.txt](misc/db build log.txt). You can see the database's contents at [misc/db print.txt](misc/db print.txt).

###Implementation attempts

I had to try a few ways to make the database work. HTML parsing in each attempt is done by [Beautiful Soup](http://www.crummy.com/software/BeautifulSoup/).

####First attempt - class search page

My original idea for scraping course info was through the [class search](https://pisa.ucsc.edu/class_search/) page. The script works but is a pain in the ass because I need to send a POST request *and* parse the returned HTML page. It is not suitable for building the database because the class search page only lists courses offered in the current quarter.

The implementation is preserved in [misc/get_course_info.py](misc/get_course_info.py) for your viewing pleasure.

####Second attempt - department websites

My second idea was to scrape course info from the website of each academic department. There were multiple problems.

First, different departments put their course catalogs on inconsistent URLs. Each of these departments use a slightly different URL pattern: [Chemistry](http://chemistry.ucsc.edu/academics/courses/course-catalog.php), [History](http://history.ucsc.edu/courses/catalog-view.php), [Mathematics](http://www.math.ucsc.edu/courses/course-catalog.php), [Linguistics](http://linguistics.ucsc.edu/courses/course-catalog-view.php), [Anthropology](http://anthro.ucsc.edu/courses/course_catalog.php).

Second, some courses appear in a department that doesn't match their department code. For example, classes in Chinese (CHIN), French (FREN), and German (GERM) are all listed on the [Language department's](http://language.ucsc.edu/courses/course-catalog.php) page.

Third, some departments use a custom layout to list course info. For example, compare the standard layout used by the [History department](http://history.ucsc.edu/courses/catalog-view.php) to the custom layouts used by the [Art department](http://art.ucsc.edu/courses/2015-16) and the [School of Engineering](https://courses.soe.ucsc.edu/).

All of these aspects would've made scraping extremely difficult.

####Third, successful, attempt - Registrar website

The third version works.  The Registrar lists every course in every department with a beautifully consistent URL: `http://registrar.ucsc.edu/catalog/programs-courses/course-descriptions/<DEPARTMENT_CODE>.html`. Humans can go to [`index.html`](http://registrar.ucsc.edu/catalog/programs-courses/course-descriptions/index.html) and choose a department on the left (scroll down).

This option is clearly the best. I didn't use it from the beginning because it was hard to find: from the [Registrar homepage](http://registrar.ucsc.edu/), follow Quick Start Guide > Catalog > Programs and Courses > Course Descriptions.

Even on the Registrar's well-organized pages, some things are broken. Read more in the next section.

### Special cases for building the database

The file [`db_core.py`](https://github.com/pfroud/ucsc-class-info-bot/blob/master/db_core.py) handles almost every department when scraping the Registrar's site, but [`db_extra.py`](https://github.com/pfroud/ucsc-class-info-bot/blob/master/db_extra.py) is needed to handle the following four special cases.

Some 

#### Indentation

First, some courses are indented in their own paragraph. For example, [Psychology](http://registrar.ucsc.edu/catalog/programs-courses/course-descriptions/psyc.html) 118A-D are all indented under the header for 118.

The functions [`is_next_p_indented()`](https://github.com/pfroud/ucsc-class-info-bot/blob/4dae0bb220513ce29fb889410570b1397c3efbde/db_extra.py#L37-L56) and [`in_indented_paragraph()`](https://github.com/pfroud/ucsc-class-info-bot/blob/4dae0bb220513ce29fb889410570b1397c3efbde/db_extra.py#L59-L67) check for this case and additional logic compensates.

####  Literature department

&rarr; The Registrar changed this. It seems all sub-departments have been combined into the Literature department. You can see what the Literature page used to look like [here](http://web.archive.org/web/20160521192216/http://registrar.ucsc.edu/catalog/programs-courses/course-descriptions/lit.html).

~~Second, the [Literature](http://registrar.ucsc.edu/catalog/programs-courses/course-descriptions/lit.html) department contains courses from multiple department codes. For example, Creative Writing (LTCR) and and Latin Literature (LTIN) classes are both under [`lit.html`](http://registrar.ucsc.edu/catalog/programs-courses/course-descriptions/lit.html).~~

~~The page uses subdepartment *names* but we care about subdepartment *codes*, so the dict [`lit_department_codes`](https://github.com/pfroud/ucsc-class-info-bot/blob/4dae0bb220513ce29fb889410570b1397c3efbde/db_extra.py#L6-L17) maps names to codes. For example, "Modern Literary Studies" maps to "LTMO" and "Greek Literature" maps to "LTGR".~~

~~Consequently the lit page is scraped by its own function, [`get_lit_depts()`](https://github.com/pfroud/ucsc-class-info-bot/blob/4dae0bb220513ce29fb889410570b1397c3efbde/db_extra.py#L135-L164), with help from the function [`get_real_lit_dept()`](https://github.com/pfroud/ucsc-class-info-bot/blob/4dae0bb220513ce29fb889410570b1397c3efbde/db_extra.py#L118-L132).~~


#### Inconsistent HTML layout

&rarr; The Registrar fixed this.

~~Third, some departments deviate from the standard HTML layout.~~

~~For almost every department, key information about a course is contained in three `<strong>` tags. Here's an example from [Biomolecular Engineering (BME)](http://registrar.ucsc.edu/catalog/programs-courses/course-descriptions/bme.html):~~

```
<strong>110.</strong>
<strong>Computational Biology Tools.</strong>
<strong>F,W</strong>
```
~~To build the database, I being by looking for `<strong>` tags containing a course number followed by a period.  (The "F,W" indicates which general education requirements are satisfied by that course.)~~

 ~~~However, *one single department does this differently*. [College Eight (CLEI)](http://registrar.ucsc.edu/catalog/programs-courses/course-descriptions/clei.html) puts the entire header in one `<strong>` tag:~~~
```
<strong>81C. Designing a Sustainable Future. S</strong>
```
&rarr; You can see what the College Eight page used to look like [here](http://web.archive.org/web/20160429201042/http://registrar.ucsc.edu/catalog/programs-courses/course-descriptions/clei.html).**

~~So, there's one [stupid special case](https://github.com/pfroud/ucsc-class-info-bot/blob/4dae0bb220513ce29fb889410570b1397c3efbde/db_core.py#L219-L220).~~

~~Furthermore, two departments miss the first `<strong>` tag. The first courses on the [German](http://registrar.ucsc.edu/catalog/programs-courses/course-descriptions/germ.html) and [Economics](http://registrar.ucsc.edu/catalog/programs-courses/course-descriptions/econ.html) pages look like this:~~
```
1. <strong>First-Year German.</strong>
<strong>F</strong>
```
~~I only look for course numbers inside of `<strong>` tags, so course 1 gets left out. There's another [stupid special case](https://github.com/pfroud/ucsc-class-info-bot/blob/4dae0bb220513ce29fb889410570b1397c3efbde/db_core.py#L224-L225).~~

&rarr; You can see what the German page used to look like [here](http://web.archive.org/web/20160429201246/http://registrar.ucsc.edu/catalog/programs-courses/course-descriptions/germ.html). You can see what the Economics page used to look like [here](http://web.archive.org/web/20160429201150/http://registrar.ucsc.edu/catalog/programs-courses/course-descriptions/econ.html). 

#### Inconsistent department naming

Fourth, the latest special cases arise from inconsistent department naming.

The Registrar's page for the [Ecology and Evolutionary Biology department ](http://registrar.ucsc.edu/catalog/programs-courses/course-descriptions/eeb.html) is on `eeb.html`, but the [class search](https://pisa.ucsc.edu/class_search/) reveals that those courses use the dapertment code `BIOE`.

Similarly, the  Registrar listing for  the [Molecular, Cell, and Developmental Biology department ](http://registrar.ucsc.edu/catalog/programs-courses/course-descriptions/mcdb.html) is on `mcdb.html`, but the courses use the department code `BIOL`.

[Two more conditionals](https://github.com/pfroud/ucsc-class-info-bot/blob/4dae0bb220513ce29fb889410570b1397c3efbde/db_core.py#L198-L206) address this issue.

##Finding course mentions

A course mention occurs when a redditor names one or more courses in a post or comment.

I pulled the list of department codes from the source of the [class search](https://pisa.ucsc.edu/class_search/) page (`<select id="subject">`), but it includes defuct and renamed departments. For example, the Arabic department (ARAB) is gone and Environmental Toxicology (ETOX) is now [Microbiology and Environmental Toxicology (METX)](http://www.metx.ucsc.edu/). All possible departments appear in the regex [`_pattern_depts`](https://github.com/pfroud/ucsc-class-info-bot/blob/4dae0bb220513ce29fb889410570b1397c3efbde/mention_parse.py#L10-L16).


### Mention types

The bot can see these three types of mention, all case-insensitive. Recall that a *course number* is actually a string and may contain one optional letter at the end.

1. **Normal mention:** department code, optional space, and course number.
For example, "CMPS 12B" and "econ105" are normal mentions.
	* Specified by regex [`_pattern_mention_normal`](https://github.com/pfroud/ucsc-class-info-bot/blob/4dae0bb220513ce29fb889410570b1397c3efbde/mention_parse.py#L21-L22).
1. **Multi-mention:** shorthand for multiple courses in the same department with different course numbers.
For example, "Math 21, 23b, and 100" is a multi-mention containing Math 21, Math 23, and Math 100.
	* Not specified by a single regex.
	* The function [`_parse_multi_mention()`](https://github.com/pfroud/ucsc-class-info-bot/blob/4dae0bb220513ce29fb889410570b1397c3efbde/mention_parse.py#L58-L92) splits a multi-mention into normal mentions.
1. **Letter-list mention:** shorthand for multiple courses in the same department, where the department code has the same numeric part but different letters.  
For example, "CE 129A/B/C" is a letter-list mention containing CE 129A, CE 129B, and CE 129C.
	* Specified by regex [`_pattern_mention_letter_list`](https://github.com/pfroud/ucsc-class-info-bot/blob/4dae0bb220513ce29fb889410570b1397c3efbde/mention_parse.py#L18-L19).
	* Function [`_parse_letter_list()`](https://github.com/pfroud/ucsc-class-info-bot/blob/4dae0bb220513ce29fb889410570b1397c3efbde/mention_parse.py#L36-L55) splits a letter-list mention into normal mentions.
	* You can have a letter-list mention in a multi-mention, like "CS 8a, 15, or 163w/x/y/z".

Five regular expressions are combined to form [`_pattern_final`](https://github.com/pfroud/ucsc-class-info-bot/blob/4dae0bb220513ce29fb889410570b1397c3efbde/mention_parse.py#L30-L33), which is used to search strings.

### Result

In the file [`mention_search_posts.py`](https://github.com/pfroud/ucsc-class-info-bot/blob/master/mention_search_posts.py), the function [`find_mentions()`](https://github.com/pfroud/ucsc-class-info-bot/blob/4dae0bb220513ce29fb889410570b1397c3efbde/mention_search_posts.py#L111-L150) gets new posts from /r/UCSC then parses everything using [`mention_parse.py`](https://github.com/pfroud/ucsc-class-info-bot/blob/master/mention_parse.py).

If `find_mentions()` is called from [`reddit_bot.py`](https://github.com/pfroud/ucsc-class-info-bot/blob/master/reddit_bot.py), it returns a [`PostWithMentions`](https://github.com/pfroud/ucsc-class-info-bot/blob/master/mention_search_posts.py#L12-L20) instance to be immediately processed; if `mention_search_posts.py` is ran on its own from the console, it is Pickled (serialized) and saved to disk. The `PostWithMentions`class is a container which holds the ID of a submission and a list of course mentions found in that submission.


##Posting comments

If [`post_comments.py`](https://github.com/pfroud/ucsc-class-info-bot/blob/master/post_comments.py) is ran on its own from the console, it loads mentions found from the last run of `mention_search_posts.py`. If the function `post_comments()` is called from `reddit_bot.py`, data about found mentions is passed directly as a parameter to the function. [Those function names are outdated]

If a post doesn't already have a a comment by /u/ucsc-class-info-bot, add one. If it does already have a comment, compare the mentions most recently found with the mentions that are already in the comment. If there are new ones, update the comment.


## Known bugs & future work

* In the comment, classes are sorted by department name (I think) instead of by order mentioned.
* I might make the bot see mentions of some department names instead of department codes, e.g. "chemistry 103" instead of "chem 103".
