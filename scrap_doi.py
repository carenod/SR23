from crossref_commons.sampling import get_sample


tituloyano =  "Reciprocal regulation between TOC1 and LHY/CCA1 within the Arabidopsis circadian clock"
filter = {'type': 'journal-article'}
queries = {'query.author': 'yanovsky', 'query.title': tituloyano}
sample = get_sample(size=1, filter=filter, queries=queries)
sample