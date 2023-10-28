from crossref_commons.sampling import get_sample
import json
import pandas as pd
import time
from threading import Thread

class ThreadWithReturnValue(Thread):
    def __init__(self, group=None, target=None, name=None,
                 args=(), kwargs={}, Verbose=None):
        Thread.__init__(self, group, target, name, args, kwargs)
        self._return = None
    def run(self):
        print(type(self._target))
        if self._target is not None:
            self._return = self._target(*self._args,
                                                **self._kwargs)
    def join(self, *args):
        Thread.join(self, *args)
        return self._return

def call(f, *args, timeout = 5, **kwargs):
    i = 0
    t = ThreadWithReturnValue(target=f, args=args, kwargs=kwargs)
    t.daemon = True
    t.start()
    while True:
        if not t.is_alive():
            break
        if timeout == i:
            print("timeout")
            return
        time.sleep(1)
        i += 1
    return t.join()

def read_sql(a,b,c, sql="", con=""):
    print(a, b, c, sql, con)
    t = 10
    while t > 0:
        # print("t=", t)
        time.sleep(1)
        t -= 1
    return "read_sql return value"


def get_doi_from_title(df_papers, df_authors, df_papers_file_name):

    if df_papers is None:
        df_papers = pd.DataFrame(columns = ['scholar_id', 'DOI', 'publisher', 'issue', 'short-container-title', 'type', 'score', 
                                            'references-count', 'URL', 'subject', 'published', 'author_name', 'references'])
        
    # remove authors that already have been fully retived
    # i dont use set method because I loose the order
    all_authors_id_original = df_authors['scholar_id'].to_list()
    all_authors_id = []
    for element in all_authors_id_original:
        if element not in df_papers['scholar_id'].unique().tolist()[:-1]:
            all_authors_id.append(element)
    
    for author_id in all_authors_id:
    
        print('Retriving papers from author ' + author_id)
        
        json_file_name = './data/publications/' + author_id + '.json'
            
        with open(json_file_name) as json_file:
            author_publications = json.load(json_file)    
            
        author_name = df_authors.loc[df_authors['scholar_id'] == author_id, 'name']    
          
        print(str(len(author_publications)) + ' articles will be retrived from author ' + author_name) 
            
        for i in range(len(author_publications)):
            
            # save every 10 papers
            if len(df_papers.index) % 10 == 0:
                df_papers.to_csv(df_papers_file_name, index=False)
                print('df saved, length ', len(df_papers.index))
            
            publication = author_publications[i]['bib']
            
            title = publication['title']
            print('search for: ' + title)

            # check if the publication for the author has aleady been added
            if len(df_papers.index) != 0 and ((df_papers['scholar_id'] == author_id) & (df_papers['title'] == title)).any():
                print(title + ' from ' + author_id + ' already exists')
                continue
            else:
                # if publication was not in df_paper                
                
                new_row = {}            
                new_row['scholar_id'] = author_id
                new_row['title'] = title
                new_row['author_name'] = author_name
                                
                try: # API can return connection error, such as 504
                    # search in crossref
                    queries = {'query.author': author_name, 'query.title': title}
                    #sample = get_sample(size=1, filter={'type': 'journal-article'}, queries=queries)
                    sample = call(get_sample, timeout=15, size=1, queries=queries)
            
                    # sample is a dict with the following keys
                    # ['indexed', 'reference-count', 'publisher', 'issue', 'content-domain', 'short-container-title',
                    # 'published-print', 'abstract', 'DOI', 'type', 'created', 'page', 'source', 'is-referenced-by-count', 
                    # 'title', 'prefix', 'volume', 'author', 'member', 'reference', 'container-title', 'language', 'link', 
                    # 'deposited', 'score', 'resource', 'issued', 'references-count', 'journal-issue', 'alternative-id', 'URL', 
                    # 'relation', 'ISSN', 'issn-type', 'subject', 'published']

                    new_row['publisher'] = sample[0]['publisher'] if 'publisher' in sample[0] else 'NA'
                    new_row['issue'] = sample[0]['issue']  if 'issue' in sample[0] else 'NA'
                    new_row['short-container-title'] = sample[0]['short-container-title']  if 'short-container-title' in sample[0] else 'NA'
                    new_row['DOI'] = sample[0]['DOI']  if 'DOI' in sample[0] else 'NA'
                    new_row['type'] = sample[0]['type']  if 'type' in sample[0] else 'NA'
                    new_row['score'] = sample[0]['score']  if 'score' in sample[0] else 'NA'
                    new_row['references-count'] = sample[0]['references-count']  if 'references-count' in sample[0] else 'NA'
                    new_row['URL'] = sample[0]['URL']  if 'URL' in sample[0] else 'NA'
                    new_row['subject'] = sample[0]['subject']  if 'subject' in sample[0] else 'NA'
                    new_row['published'] = sample[0]['published']  if 'published' in sample[0] else 'NA'
                                    
                    if 'reference' in sample[0]:
                        filtered_references = [d for d in sample[0]['reference'] if 'DOI' in d]
                        filtered_references_list = [ sub['DOI'] for sub in filtered_references ]
                        new_row['references'] = filtered_references_list 
                    else:
                        new_row['references'] = []
                    
                    df_new_row = pd.Series(new_row).to_frame().T
                    df_papers = pd.concat([df_papers, df_new_row], ignore_index=True) 
                    print('New paper added to table')
                    
                    json_object = json.dumps(sample[0], indent=4)
                    
                    old_doi = sample[0]['DOI']
                    new_doi = old_doi.replace("/", "_")
                    file_name = './data/metadata/' + new_doi + '.json'
                    with open(file_name, "w") as outfile:
                        outfile.write(json_object)
                    print('Publications retrived')
                
                except Exception as error:
                    print('Failed to retrive ' + title)
                    print(error)
                    pass # and then I can fill in the missing paper
                
    df_papers.to_csv(df_papers_file_name, index=False)
    print('df saved, length ', str(len(df_papers.index)))