from scholarly import scholarly
import pandas as pd

def add_one_author(author_name, df_authors):
    
    if not author_name:
        print('Please provide an author name')
        raise 
    else:
        print('Adding ', author_name, ' to table' )
           
    search_query = scholarly.search_author(author_name)
    
    try:
        author = next(search_query)
        print('Author found in Google Scholar')
    except:
        print('The author was not found in Google Scholar')
        raise 
                
    dict = scholarly.fill(author, sections=['basics', 'publications', 'coauthors'])

    if dict['scholar_id'] not in df_authors['scholar_id']:
        # I need the following keys from the dict scholar_id, name, affiliation, interests (list),
        # citedby (int),  publications (dict), coauthors (dict)
        new_row = {}
        new_row['name'] = dict['name']
        new_row['scholar_id'] = dict['scholar_id']
        new_row['affiliation'] = dict['affiliation']
        new_row['interests'] = dict['interests']
        new_row['citedby'] = dict['citedby']
        new_row['num_publications'] = len(dict['publications'])
        coauthors = [ca['scholar_id'] for ca in dict['coauthors']] 
        new_row['coauthors_id']= coauthors
        df_new_row = pd.Series(new_row).to_frame().T
        df_authors_final = pd.concat([df_authors, df_new_row], ignore_index=True) 
        print('Author added to table')
    else:
        print('The author already exists in the database')
        raise 
    
    return df_authors_final