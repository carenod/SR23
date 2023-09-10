from scholarly import scholarly
import json
import pandas as pd
from src.add_one_author import *

# This script makes a database of authors starting by one author, 
# and then moving to his/her co-authors,
# and then to the co-authors of the co-authors and so on and so forth 

# Also it retrieves de publication titles of each author

# The final result is a table with authors name, author google scholar id, and its coauthors
# and for each author a file with all its publications. Each publication file contains
# the title, year and journal

df_authors = pd.DataFrame()

# Add one author
author_name = 'Marcelo J. Yanovsky'

add_one_author(author_name, df_authors)

dict['coauthors']

dict['coauthors'][0]['scholar_id']
dict['coauthors'][0]['name']

json_object = json.dumps(dict, indent=4)

with open("author.json", "w") as outfile:
    outfile.write(json_object)