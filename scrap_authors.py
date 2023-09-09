from scholarly import scholarly
import json

# This script makes a database of authors starting by one author, 
# and then moving to his/her co-authors,
# and then to the co-authors of the co-authors and so on and so forth 

# Also it retrieves de publication titles of each author

# The final result is a table with authors name, author google scholar id, and its coauthors
# and for each author a file with all its publications. Each publication file contains
# the title, year and journal

search_query = scholarly.search_author('Marcelo J. Yanovsky')
search_query
author = next(search_query)
author
dict = scholarly.fill(author, sections=['basics', 'publications', 'coauthors'])

dict.keys()

dict['coauthors'][0]['scholar_id']
dict['coauthors'][0]['name']

json_object = json.dumps(dict, indent=4)

with open("author.json", "w") as outfile:
    outfile.write(json_object)