from scholarly import scholarly
import pandas as pd
import json

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
                
    print('Retriving data from Google Scholar')            
    dict = scholarly.fill(author, sections=['basics', 'publications', 'coauthors'])

    print('Writing table')
    if dict['scholar_id'] not in df_authors['scholar_id'] or df_authors.shape[0] == 0:
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
        
        json_object = json.dumps(dict['publications'], indent=4)
        file_name = './data/publications/' + dict['scholar_id'] + '.json'
        with open(file_name, "w") as outfile:
            outfile.write(json_object)
        print('Publications retrived')
        
    else:
        print('The author already exists in the database')
        raise 
    
    return df_authors_final

def add_all_coauthor(df_authors):
    
    all_authors = [element for innerList in df_authors['coauthors_id'] for element in innerList]
    
    # remove repeated ids and ids that are already present in the table
    all_authors = set(all_authors)
    authors_in_df = set(df_authors['scholar_id'])
    new_authors = all_authors.difference(authors_in_df)
    
    for author_id in new_authors:
       
        print('Retriving data from Google Scholar for author ', author_id)
        author = scholarly.search_author_id(author_id)
                            
        dict = scholarly.fill(author, sections=['basics', 'publications', 'coauthors'])

        print('Writing table')
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
        df_authors = pd.concat([df_authors, df_new_row], ignore_index=True) 
        print('Author added to table')
        
        json_object = json.dumps(dict['publications'], indent=4)
        file_name = './data/publications/' + dict['scholar_id'] + '.json'
        with open(file_name, "w") as outfile:
            outfile.write(json_object)
        print('Publications retrived')
    
    return df_authors