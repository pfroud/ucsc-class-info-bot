import pickle

from build_database import Department, Course, CourseDatabase

with open(r'C:\Users\Peter Froud\Documents\reddit ucsc bot\pickle_file', 'rb') as file:
    db = pickle.load(file)
file.close()

print(db)
