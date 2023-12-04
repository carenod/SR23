import pandas as pd
from ast import literal_eval

df = pd.read_csv("./data/df_papers.csv")
df.head()
df.columns

# Convert refernce column to list
df.loc[:,'references'] = df.loc[:,'references'].apply(lambda x: literal_eval(x))


# Make a table that has a row for each cited paper (references column) 
# for a given author (scholar_id + author_name)

# if a given author cites that paper more than once, make a row for each
# citation and then group those rows adding a column that count the number of citations

# the final table has these columns: scholar_id, author_name, 'DOI' (of cited paper), 
# published (date), number_of_citations

df = df.explode('references')

df.to_csv("./data/interactions.csv")
#references