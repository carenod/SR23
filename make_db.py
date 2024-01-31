import sqlite3
import pandas as pd
from ast import literal_eval
from sklearn.model_selection import train_test_split
import csv

##### ACA CARGO CSV Y LOS EDITO PARA QUE QUEDEN LAS COLUMNAS QUE ME INTERESAN #####
df_papers = pd.read_csv("./data/df_papers_final.csv")
df_autores = pd.read_csv("./data/df_authors.csv")
df_int = pd.read_csv("./data/df_int.csv")

# edit df_papers
df_papers.columns
df_papers.drop(['issue', 'subject', 'references'], axis=1, inplace=True)
df_papers.duplicated().sum()
df_papers.shape

# published column to year and month columns
df_papers['published'].isna().sum() # remove papers without date
df_papers.dropna(subset=['published'], inplace=True)
df_papers.loc[:,'published'] = df_papers.loc[:,'published'].apply(lambda x: literal_eval(x))
df_papers.loc[:,'year'] = df_papers.loc[:,'published'].apply(lambda x: x['date-parts'][0][0])
df_papers.drop(['published'], axis=1, inplace=True)

df_papers['short-container-title'].isna().sum() # remove papers without date
df_papers.dropna(subset=['short-container-title'], inplace=True)
df_papers.loc[:,'short-container-title'] = df_papers.loc[:,'short-container-title'].apply(lambda x: literal_eval(x)[0])

df_papers['author_name'] = df_papers['author_name'].astype(str)
df_papers['author_name'] = df_papers['author_name'].str.replace(r'(^[0-9]{,3}\s{4})', '', regex=True)
df_papers['author_name'] = df_papers['author_name'].str.replace('\nName: name, dtype: object', '', regex=False)

df_papers = df_papers.drop_duplicates(subset='DOI', keep='last')

# edit df_autores
df_autores.columns
df_autores.drop(['interests', 'coauthors_id'], axis=1, inplace=True)
df_autores.drop_duplicates(inplace=True)
df_autores.duplicated().sum()
df_autores.shape

# edit df_int
df_int.columns
df_int.drop(['Unnamed: 0', 'publisher', 'issue', 'short-container-title', 'type', 'score', 
             'references-count', 'URL', 'subject', 'published', 'author_name', 'DOI', 'title'],
            axis=1, inplace=True)
df_int.drop_duplicates(inplace=True)
df_int.duplicated().sum()
df_int.shape # 1 172 332 rows
df_int.rename(columns={"references": "DOI"}, inplace=True)
df_int['read'] = 1 # 1 if it has been read, and 0 if it has been shown and the user didn't show interest

# keep interactions that are presente in the other df
df_int = df_int[df_int.DOI.isin(df_papers['DOI']) == True] 
df_int = df_int[df_int.scholar_id.isin(df_autores['scholar_id']) == True] # 62 772 rows

# split train and test
df_int_train, df_int_test = train_test_split(df_int, test_size=0.2, random_state=42)

df_int.to_csv("./data/df_int_for_db.csv", index=False, header=False)
df_int_train.to_csv("./data/df_int_train_for_db.csv", index=False, header=False)
df_int_test.to_csv("./data/df_int_test_for_db.csv", index=False, header=False)

# Now make the db
con = sqlite3.connect('./data/data.db')
c = con.cursor()

# Table Definition
#create_table_papers = '''CREATE TABLE IF NOT EXISTS papers(
#                         scholar_id VARCHAR(40),
#                         DOI VARCHAR(40) UNIQUE NOT NULL,
#                         publisher VARCHAR(40),
#                         short_container_title VARCHAR(40),
#                         type VARCHAR(40),
#                         score FLOAT,
#                         references_count INTEGER NOT NULL,
#                         URL VARCHAR(40) NOT NULL,
#                         author_name VARCHAR(40) NOT NULL,
#                         title VARCHAR NOT NULL,
#                         year YEAR NOT NULL,
#                         PRIMARY KEY (DOI));
#                         '''
#                         #first_author VARCHAR(40),
#                         #last_author VARCHAR(40) NOT NULL,
#
#create_table_autores = '''CREATE TABLE IF NOT EXISTS autores(
#                          name VARCHAR,
#                          scholar_id VARCHAR(40) NOT NULL PRIMARY KEY,
#                          affiliation VARCHAR,
#                          cited_by INTEGER,
#                          num_publication INTEGER);
#                          '''
#                          #coauthors_id VARCHAR40(40) NOT NULL;
#                          #interest VARCHAR(40) NOT NULL,                   

create_table_interacciones = '''CREATE TABLE IF NOT EXISTS interacciones(
                                scholar_id VARCHAR(40) NOT NULL,
                                DOI VARCHAR(40) NOT NULL,
                                read INTEGER,
                                PRIMARY KEY (scholar_id, DOI));
                                '''
                                #count INTEGER NOT NULL

create_table_interacciones_train = '''CREATE TABLE IF NOT EXISTS interacciones_train(
                                      scholar_id VARCHAR(40) NOT NULL,
                                      DOI VARCHAR(40) NOT NULL,
                                      read INTEGER,
                                      PRIMARY KEY (scholar_id, DOI));
                                      '''
                                
create_table_interacciones_test = '''CREATE TABLE IF NOT EXISTS interacciones_test(
                                     scholar_id VARCHAR(40) NOT NULL,
                                     DOI VARCHAR(40) NOT NULL,
                                     read INTEGER,
                                     PRIMARY KEY (scholar_id, DOI));
                                     '''                   
        
# Creating the table into our database
#c.execute(create_table_papers)
#c.execute(create_table_autores)
c.execute(create_table_interacciones)
c.execute(create_table_interacciones_train)
c.execute(create_table_interacciones_test)

# insert the data from the DataFrame into the SQLite table
df_papers.to_sql('papers', con, if_exists='replace', index = False,
                 dtype={ 'scholar_id': 'VARCHAR(40)',
                         'DOI': 'VARCHAR(40) PRIMARY KEY',
                         'publisher': 'VARCHAR(40)',
                         'short_container_title':' VARCHAR(40)',
                         'type': 'VARCHAR(40)',
                         'score': 'FLOAT',
                         'references_count': 'INTEGER NOT NULL',
                         'URL': 'VARCHAR(40) NOT NULL',
                         'author_name': 'VARCHAR(40) NOT NULL',
                         'title': 'VARCHAR NOT NULL',
                         'year': 'YEAR NOT NULL'})

df_autores.to_sql('autores', con, if_exists='replace', index = False,
                  dtype={'name': 'VARCHAR',
                         'scholar_id': 'VARCHAR(40) PRIMARY KEY',
                         'affiliation': 'VARCHAR',
                         'cited_by': 'INTEGER',
                         'num_publication': 'INTEGER'})


# db with two primary keys (not supported by pandas)
file = open("./data/df_int_for_db.csv")
file_train = open("./data/df_int_train_for_db.csv")
file_test = open("./data/df_int_test_for_db.csv")
contents = csv.reader(file)
contents_train = csv.reader(file_train)
contents_test = csv.reader(file_test)

# SQL query to insert data into the table
insert_records = "INSERT INTO interacciones (scholar_id, DOI, read) VALUES(?, ?, ?)"
insert_records_train = "INSERT INTO interacciones_train (scholar_id, DOI, read) VALUES(?, ?, ?)"
insert_records_test = "INSERT INTO interacciones_test (scholar_id, DOI, read) VALUES(?, ?, ?)"
 
# Importing the contents of the file into our tables
con.executemany(insert_records, contents)
con.executemany(insert_records_train, contents_train)
con.executemany(insert_records_test, contents_test)

con.commit()
con.close()
