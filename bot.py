import praw #pythono wrapper for reddit api
import re #regular expressions

# http://praw.readthedocs.org/en/stable/pages/writing_a_bot.html
# http://praw.readthedocs.org/en/stable/pages/comment_parsing.html 


subjects = ["ACEN", "AMST", "ANTH", "APLX", "AMS", "ARAB", "ART", "ARTG", "ASTR", "BIOC", "BIOL", "BIOE", "BME", "CHEM", "CHIN", "CLEI", "CLNI", "CLTE", "CMMU", "CMPM", "CMPE", "CMPS", "COWL", "LTCR", "CRES", "CRWN", "DANM", "EART", "ECON", "EDUC", "EE", "ENGR", "LTEL", "ENVS", "ETOX", "FMST", "FILM", "FREN", "LTFR", "GAME", "GERM", "LTGE", "GREE", "LTGR", "HEBR", "HNDI", "HIS", "HAVC", "HISC", "HUMN", "ISM", "ITAL", "LTIT", "JAPN", "JWST", "KRSG", "LAAD", "LATN", "LALS", "LTIN", "LGST", "LING", "LIT", "MATH", "MERR", "METX", "LTMO", "MUSC", "OAKS", "OCEA", "PHIL", "PHYE", "PHYS", "POLI", "PRTR", "PORT", "LTPR", "PSYC", "PUNJ", "RUSS", "SCIC", "SOCD", "SOCS", "SOCY", "SPAN", "SPHS", "SPSS", "LTSP", "STEV", "TIM", "THEA", "UCDC", "WMST", "LTWL", "WRIT", "YIDD", "CE", "CS"]

subjects_lower = [x.lower() for x in subjects]

regex = re.compile(' ?[0-9]+[A-Za-z]?')

r = praw.Reddit('comment scraper by Peter Froud')

submission = r.get_submission(submission_id='3vm05w') #for now, directly input a submission

flat_comments = praw.helpers.flatten_tree(submission.comments)

for comment in flat_comments: #iterate comments
	for subj in subjects_lower: #iterate subjects
		#print("subject is ", subj)
		body_text = comment.body.lower()
		subj_start = body_text.find(subj)
		if subj_start > 0: # if found a subject in body
		
			#print("    in comment \"", comment, "\" at subj_start", subj_start, ": found subject", subj, "as \"", body_text[subj_start:subj_start+len(subj)], "\"")

			subj_end = subj_start+len(subj)
			subj_substr = body_text[subj_start:subj_end]
			regex_substr = body_text[subj_end:subj_end+5]
			
			result = regex.match(regex_substr)
			print("Found subject \""+subj_substr+"\". Regexing in \""+regex_substr+"\".")
			if result != None: #if found a class number
				print("    >matched string \""+body_text[subj_start:subj_end+result.end()]+"\".")
				
				
			
			
			
			
			
