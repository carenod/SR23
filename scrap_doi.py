from crossref.restful import Works

works = Works()

w1 = works.query(bibliographic="Reciprocal regulation between TOC1 and LHY/CCA1 within the Arabidopsis circadian clock")

w1['DOI'][0]

len(w1)

for item in w1:
    print(item['DOI'])
    
from crossref_commons.sampling import get_sample

filter = {'funder': '10.13039/501100000038', 'type': 'journal-article'}
queries = {'query.author': 'li', 'query.affiliation': 'university'}
sample = get_sample(size=121, filter=filter, queries=queries)
