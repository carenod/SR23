import sqlite3
import pandas as pd
import numpy as np
import sys
import os
import random
import string

import lightfm as lfm
from lightfm import data
from lightfm import cross_validation
from lightfm import evaluation
import pickle

from whoosh.index import open_dir
from whoosh.qparser import MultifieldParser
from whoosh.qparser import OrGroup
from whoosh.qparser import FuzzyTermPlugin

THIS_FOLDER = os.path.dirname(os.path.abspath("__file__"))

def sql_execute(query, params=None):
    con = sqlite3.connect(os.path.join(THIS_FOLDER, "data/data.db"))
    cur = con.cursor()
    if params:
        res = cur.execute(query, params)
    else:
        res = cur.execute(query)

    con.commit()
    con.close()
    return

def sql_select(query, params=None):
    con = sqlite3.connect(os.path.join(THIS_FOLDER, "data/data.db"))
    con.row_factory = sqlite3.Row # esto es para que devuelva registros en el fetchall
    cur = con.cursor()
    if params:
        res = cur.execute(query, params)
    else:
        res = cur.execute(query)

    ret = res.fetchall()
    con.close()

    return ret

def get_scholar_id(name):
    query = "SELECT scholar_id FROM autores WHERE name = ?"
    try:
        scholar_id = sql_select(query, (name,))[0]['scholar_id']
    except:
        scholar_id = None
    return scholar_id

def crear_usuario(scholar_id, name):
    query = "INSERT INTO autores(scholar_id, name, affiliation, citedby, num_publications) VALUES (?, ?, ?, ?, ?) ON CONFLICT DO NOTHING;" # si el id_lector existia, se produce un conflicto y le digo que no haga nada
    sql_execute(query, (scholar_id, name, 'ninguna', 0, 0))
    return

def insertar_interacciones(DOI, scholar_id, read, interacciones="interacciones"):
    if read == -1:
        query = f"INSERT INTO {interacciones}(scholar_id, DOI, read) VALUES (?, ?, ?) ON CONFLICT (scholar_id, DOI) DO UPDATE SET read = read + ?;"
        sql_execute(query, (scholar_id, DOI, read, read,))
    else:
        query = f"INSERT INTO {interacciones}(scholar_id, DOI, read) VALUES (?, ?, ?) ON CONFLICT (scholar_id, DOI) DO UPDATE SET read = ?;" # si el rating existia lo actualizo
        sql_execute(query, (scholar_id, DOI, read, read,))
    return

def reset_usuario(scholar_id, interacciones="interacciones"):
    query = f"DELETE FROM {interacciones} WHERE scholar_id = ?;"
    sql_execute(query, (scholar_id,))
    return

def generate_id():
    # from https://pynative.com/python-generate-random-string/
    letters = ''.join((random.choice(string.ascii_letters) for i in range(9)))
    digits = ''.join((random.choice(string.digits) for i in range(3)))

    # Convert resultant string to list and shuffle it to mix letters and digits
    sample_list = list(letters + digits)
    random.shuffle(sample_list)
    # convert list to string
    final_string = ''.join(sample_list)

    #TODO: veer que ids nuevos no se repitan
    #all_scholar_id = sql_select(query, params=None)
    #if final_string in all_scholar_id:
    #    final_string = generate_id()

    return final_string

def retrain_model():
    # load train and test datasets
    con = sqlite3.connect(os.path.join(THIS_FOLDER, "data/data.db"))
    df_autores = pd.read_sql_query("SELECT * from autores", con)
    df_papers = pd.read_sql_query("SELECT * from papers", con)
    df_int = pd.read_sql_query("SELECT * from interacciones", con)
    con.close()

    # create dataset
    ds = data.Dataset()

    item_features_list = df_papers["publisher"].unique().tolist() + df_papers["year"].unique().tolist() + \
        df_papers["type"].unique().tolist() + df_papers["score"].unique().tolist() + \
        df_papers["references-count"].unique().tolist() + df_papers["scholar_id"].unique().tolist()

    user_features_list =  df_autores["citedby"].unique().tolist() + df_autores["num_publications"].unique().tolist()

    # con features
    ds.fit(users=df_autores["scholar_id"].unique(), items=df_papers["DOI"].unique(),
           item_features=item_features_list, user_features=user_features_list)

    num_users, num_items = ds.interactions_shape()
    print('Num users: {}, num_items {}.'.format(num_users, num_items))

    (interactions, weights) = ds.build_interactions(df_int[["scholar_id", "DOI"]].itertuples(index=False))

    ifs = []
    for index, row in df_papers.iterrows():
        ifs.append( (row["DOI"], (row["publisher"], row["year"], row["type"], row["score"],
                                  row["references-count"], row["scholar_id"]))  )
    item_features = ds.build_item_features(ifs)

    ufs = []
    for index, row in df_autores.iterrows():
        ufs.append( (row["scholar_id"], (row["citedby"], row["num_publications"]))  )
    user_features = ds.build_user_features(ufs)

    model = lfm.LightFM(no_components= 30, # dim de embedding: hay que optimizar
                        loss= 'warp', #‘logistic’, ‘bpr’, ‘warp’, ‘warp-kos’
                        learning_schedule= 'adadelta', # ‘adagrad’, ‘adadelta’
                        max_sampled= 5, # for warp
                        random_state=96821) # use multiple seeds
    model.fit(interactions,
              user_features=user_features,
              item_features=item_features,
              epochs=100)

    #auc_train= lfm.evaluation.auc_score(model, interactions, user_features=user_features, item_features=item_features)
    #recall_train = lfm.evaluation.recall_at_k(model, interactions, k=10, user_features=user_features, item_features=item_features)
    #reciprocal_train = lfm.evaluation.reciprocal_rank(model, interactions, user_features=user_features, item_features=item_features)

    with open(os.path.join(THIS_FOLDER, "data/saved_model.pck"),'wb') as f:
        saved_model={'model':model}
        pickle.dump(saved_model, f)

    return

def obtener_libro(id_libro):
    query = "SELECT * FROM libros WHERE id_libro = ?;"
    libro = sql_select(query, (id_libro,))[0]
    return libro

def leidos(scholar_id, interacciones="interacciones"):
    query = f"SELECT * FROM {interacciones} WHERE scholar_id = ? AND read = 1"
    leidos = sql_select(query, (scholar_id,))
    return leidos

def ignorados(id_lector, interacciones="interacciones"):
    query = f"SELECT * FROM {interacciones} WHERE scholar_id = ? AND read < -9"
    ignorados = sql_select(query, (id_lector,))
    return ignorados

def datos_papers(DOIs):
    query = f"SELECT DISTINCT * FROM papers WHERE DOI IN ({','.join(['?']*len(DOIs))})"
    papers = sql_select(query, DOIs)
    return papers

def recomendar_top_9():
    query = """
        SELECT DISTINCT DOI, COUNT(DOI) AS doi_count
          FROM interacciones
      GROUP BY DOI
      ORDER BY doi_count DESC
         LIMIT 90;
    """
    DOIs = [r["DOI"] for r in sql_select(query)]
    return DOIs

def recomendar_lightfm(scholar_id, interacciones="interacciones"):
    # TODO: optimizar hiperparámetros
    # TODO: entrenar el modelo de forma parcial
    # TODO: user item_features y user_features
    # TODO: usar los items ignorados (usar pesos)

    model = pickle.load(open(os.path.join(THIS_FOLDER, "data/saved_model.pck"), 'rb'))['model']

    con = sqlite3.connect(os.path.join(THIS_FOLDER, "data/data.db"))
    df_int = pd.read_sql_query("SELECT * FROM interacciones", con)
    df_papers = pd.read_sql_query("SELECT * FROM papers", con)
    df_autores = pd.read_sql_query("SELECT * FROM autores", con)
    con.close()

    ds = data.Dataset()

    item_features_list = df_papers["publisher"].unique().tolist() + df_papers["year"].unique().tolist() + \
        df_papers["type"].unique().tolist() + df_papers["score"].unique().tolist() + \
        df_papers["references-count"].unique().tolist() + df_papers["scholar_id"].unique().tolist()

    user_features_list =  df_autores["citedby"].unique().tolist() + df_autores["num_publications"].unique().tolist()

    # con features
    ds.fit(users=df_autores["scholar_id"].unique(), items=df_papers["DOI"].unique(),
           item_features=item_features_list, user_features=user_features_list)

    scholar_id_map, scholar_feature_map, paper_id_map, paper_feature_map = ds.mapping()
    (interactions, weights) = ds.build_interactions(df_int[["scholar_id", "DOI"]].itertuples(index=False))

    ifs = []
    for index, row in df_papers.iterrows():
        ifs.append( (row["DOI"], (row["publisher"], row["year"], row["type"], row["score"],
                                  row["references-count"], row["scholar_id"]))  )
    item_features = ds.build_item_features(ifs)

    ufs = []
    for index, row in df_autores.iterrows():
        ufs.append( (row["scholar_id"], (row["citedby"], row["num_publications"]))  )
    user_features = ds.build_user_features(ufs)

    #model = lfm.LightFM(no_components=20, k=5, n=10, learning_schedule='adagrad', loss='logistic', learning_rate=0.05, rho=0.95, epsilon=1e-06, item_alpha=0.0, user_alpha=0.0, max_sampled=10, random_state=42)
    #model.fit(interactions, sample_weight=weights, epochs=10)

    model.fit_partial(interactions, user_features=user_features, item_features=item_features, epochs=1, num_threads=1, verbose=False)

    papers_leidos = df_int.loc[(df_int["scholar_id"] == scholar_id) & (df_int['read'] > -9), "DOI"].tolist()
    todos_los_papers = df_papers["DOI"].tolist()
    papers_no_leidos = set(todos_los_papers).difference(papers_leidos)

    predicciones = model.predict(scholar_id_map[scholar_id],
                                 [paper_id_map[l] for l in papers_no_leidos],
                                 item_features=item_features,
                                 user_features=user_features)

    recomendaciones = sorted([(p, l) for (p, l) in zip(predicciones, papers_no_leidos)], reverse=True)[:90]
    recomendaciones = [paper[1] for paper in recomendaciones]
    return recomendaciones

def recomendar_whoosh(query):

    ix = open_dir(os.path.join(THIS_FOLDER, "index"))

    mparser = MultifieldParser(["title", "author_name", 'short-container-title', 'URL'], schema=ix.schema, group=OrGroup)
    mparser.add_plugin(FuzzyTermPlugin())
    myquery = mparser.parse(query)

    with ix.searcher() as searcher:
        results = searcher.search(myquery, limit=None)
        DOIs = [r["DOI"] for r in results]
        print(len(DOIs))

    recomendaciones = datos_papers(DOIs)

    return recomendaciones


def recomendar(scholar_id):
    # TODO: combinar mejor los recomendadores
    # TODO: crear usuarios fans para llenar la matriz

    cant_leidos = len(leidos(scholar_id))
    #
    if cant_leidos <= 10:
        print("recomendador: top9", file=sys.stdout)
        DOIs = recomendar_top_9()
    else:
        print("recomendador: lightfm", file=sys.stdout)
        #id_libros = recomendar_lightfm(scholar_id, interacciones)
        DOIs = recomendar_lightfm(scholar_id)

    # TODO: como completo las recomendaciones cuando vienen menos de 9?

    recomendaciones = datos_papers(DOIs)

    return recomendaciones

