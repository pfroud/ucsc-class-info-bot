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

### Known bugs

* Won't recognize CS as CMPS or CMPE as CMPE
* In the comment, classes are sorted by department name.
Ideally they would be sorted by the order in which they're mentioned.
