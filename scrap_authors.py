from scholarly import scholarly
import json

# This script makes a database of authors starting by one author, 
# and then moving to his/her co-authors,
# and then to the co-authors of the co-authors and so on and so forth 

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