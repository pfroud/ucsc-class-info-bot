import praw  # python wrapper for reddit api
import re  # regular expressions

# http://praw.readthedocs.org/en/stable/pages/writing_a_bot.html
# http://praw.readthedocs.org/en/stable/pages/comment_parsing.html 

# scraped from https://pisa.ucsc.edu/cs9/prd/sr9_2013/index.php
# subjects = ["ACEN", "AMST", "ANTH", "APLX", "AMS", "ARAB", "ART", "ARTG", "ASTR", "BIOC", "BIOL", "BIOE", "BME", "CHEM",
#             "CHIN", "CLEI", "CLNI", "CLTE", "CMMU", "CMPM", "CMPE", "CMPS", "COWL", "LTCR", "CRES", "CRWN", "DANM",
#             "EART", "ECON", "EDUC", "EE", "ENGR", "LTEL", "ENVS", "ETOX", "FMST", "FILM", "FREN", "LTFR", "GAME",
#             "GERM", "LTGE", "GREE", "LTGR", "HEBR", "HNDI", "HIS", "HAVC", "HISC", "HUMN", "ISM", "ITAL", "LTIT",
#             "JAPN", "JWST", "KRSG", "LAAD", "LATN", "LALS", "LTIN", "LGST", "LING", "LIT", "MATH", "MERR", "METX",
#             "LTMO", "MUSC", "OAKS", "OCEA", "PHIL", "PHYE", "PHYS", "POLI", "PRTR", "PORT", "LTPR", "PSYC", "PUNJ",
#             "RUSS", "SCIC", "SOCD", "SOCS", "SOCY", "SPAN", "SPHS", "SPSS", "LTSP", "STEV", "TIM", "THEA", "UCDC",
#             "WMST", "LTWL", "WRIT", "YIDD", "CE", "CS"]

subjects = ["ACEN", "BME", "ABCD", "CS"]

subjects_lower = [x.lower() for x in subjects]

regex = re.compile(" ?[0-9]+[A-Za-z]?")

r = praw.Reddit('comment scraper by Peter Froud')  # the user agent?

submission = r.get_submission(submission_id='3uyc86')  # for now, directly input a submission

flat_comments = praw.helpers.flatten_tree(submission.comments)


for comment in flat_comments:  # iterate comments
    lowercase_body = comment.body.lower()
    for subj in subjects_lower:  # iterate subjects
        # print("subject is ", subj)

        start_of_next_search = 0

        while start_of_next_search < len(lowercase_body):
            # print("starting search from index", start_of_next_search)

            body_text = lowercase_body[start_of_next_search:]
            subj_start_index = body_text.find(subj)
            if subj_start_index > 0:  # if found a subject in body

                # print("    in comment \"", comment, "\" at subj_start_index", subj_start_index,
                # ": found subject", subj, "as \"", body_text[subj_start_index:subj_start_index+len(subj)], "\"")

                subj_end_index = subj_start_index + len(subj)
                subj_substr = body_text[subj_start_index: subj_end_index]
                regex_substr = body_text[subj_end_index: subj_end_index + 5]  # maximum of 5 extra letters needed

                start_of_next_search += subj_end_index
                print("updated start_of_next_search to", subj_end_index)

                result = regex.match(regex_substr)
                print("Found subject \"" + subj_substr + "\". Regexing in \"" + regex_substr + "\".")
                if result is not None:  # if found a class number
                    print("    >matched string \"" + body_text[subj_start_index: subj_end_index + result.end()] + "\".")
            else:
                break
