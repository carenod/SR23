from operator import ixor
from whoosh.index import create_in
from whoosh.fields import *
from whoosh.index import create_in
from whoosh.qparser import MultifieldParser
from whoosh.qparser import OrGroup
from whoosh.qparser import FuzzyTermPlugin

import os.path
import sqlite3
import pandas as pd

THIS_FOLDER = os.path.dirname(os.path.abspath("__file__"))

con = sqlite3.connect(os.path.join(THIS_FOLDER, "data/data.db"))
df_papers = pd.read_sql_query("SELECT * from papers", con)
con.close()

schema = Schema(title=TEXT(stored=True), author=TEXT(stored=True), publisher=TEXT(stored=True), URL=TEXT(stored=True), DOI=TEXT(stored=True))

if not os.path.exists(os.path.join(THIS_FOLDER, "index")):
    os.mkdir(os.path.join(THIS_FOLDER, "index"))
ix = create_in(os.path.join(THIS_FOLDER, "index"), schema)

writer = ix.writer()
for i in df_papers.index:
    writer.add_document(title=df_papers['title'][i], 
                        author=df_papers['author_name'][i],
                        publisher=df_papers['short-container-title'][i], 
                        URL=df_papers['URL'][i],
                        DOI=df_papers['DOI'][i])
writer.commit()

