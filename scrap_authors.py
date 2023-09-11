import pandas as pd
from src.add_authors import *

# This script makes a database of authors starting by one author, 
# and then moving to his/her co-authors,
# and then to the co-authors of the co-authors and so on and so forth 

# Also it retrieves de publication titles of each author

# The final result is a table with authors name, author google scholar id, and its coauthors
# and for each author a file with all its publications. Each publication file contains
# the title, year and journal

df_authors = pd.DataFrame(columns = ['name', 'scholar_id', 'affiliation', 'interests', 'citedby', 'num_publications', 'coauthors_id'])

# Add one author
authors_seed = ['Marcelo J. Yanovsky', 'Jorge Casal', 'Luciana Bianchimano']
for a in authors_seed:
    df_authors = add_one_author(a, df_authors)

df_authors = add_all_coauthor(df_authors)

df_authors.shape
df_authors.to_csv('./data/df_authors.csv', index=False)

# problem with 3rZSW4YAAAAJ