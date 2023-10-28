import pandas as pd
from src.add_authors import *
from src.get_doi import *
from ast import literal_eval

# This script makes a database of authors starting by one author, 
# and then moving to his/her co-authors,
# and then to the co-authors of the co-authors and so on and so forth 

# Also it retrieves de publication titles of each author

# The final result is a table with authors name, author google scholar id, and its coauthors
# and for each author a file with all its publications. Each publication file contains
# the title, year and journal


##### STEP 1: create authors "seed" #####
# create empty df
df_authors = pd.DataFrame(columns = ['name', 'scholar_id', 'affiliation', 'interests', 'citedby', 'num_publications', 'coauthors_id'])
# Add authors one by one
authors_seed = ['Marcelo J. Yanovsky', 'Jorge Casal', 'Luciana Bianchimano']
for a in authors_seed:
    df_authors = add_one_author(a, df_authors)
# Save df
df_authors.to_csv('./data/df_authors.csv', index=False)

##### STEP 2: authors' coathours #####
# After adding the first authors manually, add their coauthors automatically
# Read csv with df_authors
df_authors = pd.read_csv('./data/df_authors.csv')
# coauthors_id column from string to list 
df_authors.loc[:,'coauthors_id'] = df_authors.loc[:,'coauthors_id'].apply(lambda x: literal_eval(x))
# add coautohors automaticallu
add_all_coauthor(df_authors, './data/df_authors.csv')
# problem with 3rZSW4YAAAAJ
df_authors.shape

##### STEP 3: authors' publications #####
# Read authors df and run get_doi_from_title for first time
df_authors = pd.read_csv('./data/df_authors.csv')
get_doi_from_title(df_papers=None, df_authors=df_authors, df_papers_file_name='./data/df_papers.csv')

# Run get_doi_from_title
df_papers = pd.read_csv('./data/df_papers.csv')
df_authors = pd.read_csv('./data/df_authors.csv')
get_doi_from_title(df_papers=df_papers, df_authors=df_authors, df_papers_file_name='./data/df_papers.csv')