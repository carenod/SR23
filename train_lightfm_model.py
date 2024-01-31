# this script trains lightfm model and saves its as a pickle file
import sqlite3
import pandas as pd
import os
from itertools import product
import numpy as np
from sklearn.model_selection import train_test_split

import lightfm as lfm
from lightfm import data
from lightfm import cross_validation
from lightfm import evaluation

THIS_FOLDER = os.path.dirname(os.path.abspath("__file__"))

# define 10 seeds
seeds = [96821, 461437, 927683, 447247, 632189]

# only run this the first time
# define hyperparameters to test
no_components = list(range(10, 100 + 1, 20))
loss = ['logistic', 'bpr', 'warp', 'warp-kos'] # 
k = list(range(1, 8 + 1, 2)) + list(range(10, 50 + 1, 25)) # 'warp-kos'
n = [i * 2 for i in k] # 'warp-kos'
learning_rate = [5e-3, 5e-2, .1]
learning_schedule = ['adagrad', 'adadelta']
max_sampled = [5, 10, 50] # 'warp', 'warp-kos'

hp1_adadelta = pd.DataFrame(list(product(no_components, loss[0:2])), 
                   columns=['no_components', 'loss'])
hp1_adadelta['learning_schedule'] = 'adadelta'

hp1_adagrad = pd.DataFrame(list(product(no_components, loss[0:2], learning_rate)), 
                   columns=['no_components', 'loss', 'learning_rate'])
hp1_adagrad['learning_schedule'] = 'adagrad'

hp2_adadelta = pd.DataFrame(list(product(no_components, max_sampled)), 
                   columns=['no_components', 'max_sampled'])
hp2_adadelta['loss'] = loss[2]
hp2_adadelta['learning_schedule'] = 'adadelta'

hp2_adagrad = pd.DataFrame(list(product(no_components, max_sampled, learning_rate)), 
                   columns=['no_components', 'max_sampled', 'learning_rate'])
hp2_adagrad['loss'] = loss[2]
hp2_adagrad['learning_schedule'] = 'adagrad'

hp3_adadelta = pd.DataFrame(list(product(no_components, max_sampled, k, n)), 
                   columns=['no_components', 'max_sampled', 'k', 'n'])
hp3_adadelta['loss'] = loss[3]
hp3_adadelta['learning_schedule'] = 'adadelta'

hp3_adagrad = pd.DataFrame(list(product(no_components, learning_rate, max_sampled, k, n)), 
                   columns=['no_components', 'learning_rate', 'max_sampled', 'k', 'n'])
hp3_adagrad['loss'] = loss[3]
hp3_adagrad['learning_schedule'] = 'adagrad'
     
       
hp = pd.concat([hp1_adadelta, hp1_adagrad, hp2_adadelta, hp2_adagrad, hp3_adadelta, hp3_adagrad], ignore_index=True)
hp['auc_train'] =  np.nan
hp['recall_train'] = np.nan
hp['reciprocal_train'] = np.nan
hp['auc_test'] =  np.nan
hp['recall_test'] = np.nan
hp['reciprocal_test'] = np.nan

hp.to_csv(os.path.join(THIS_FOLDER, "data/hp.csv"), index=False)
hp = pd.read_csv(os.path.join(THIS_FOLDER, "data/hp.csv"))

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

# make modelo
total_length = len(hp)
for i in range(len(hp)):
    
    if not np.isnan(hp.loc[i, "auc_train"]):
        continue
    
    auc_train = []
    recall_train = []
    reciprocal_train = []
    auc_test = []
    recall_test = []
    reciprocal_test = []
    
    for seed in seeds:
        
        (train, test) = cross_validation.random_train_test_split(interactions, test_percentage=0.2, random_state=seed)
        
        k = 5 if np.isnan(hp.loc[i, 'k']) else hp.loc[i, 'k']
        n =  10 if np.isnan(hp.loc[i, 'n']) else hp.loc[i, 'n']
        ms =  10 if np.isnan(hp.loc[i, 'max_sampled']) else hp.loc[i, 'max_sampled']

        model = lfm.LightFM(no_components= hp.loc[i, 'no_components'] , # dim de embedding: hay que optimizar
                            loss= hp.loc[i, 'loss'], #‘logistic’, ‘bpr’, ‘warp’, ‘warp-kos’
                            k= k, # applies for warp-kos
                            n= n, # applies for warp-kos
                            learning_schedule=hp.loc[i, 'learning_schedule'], # ‘adagrad’, ‘adadelta’
                            learning_rate=hp.loc[i, 'learning_rate'], 
                            rho=0.95, # only for adadelta 
                            epsilon=1e-06, # only for adadelta 
                            item_alpha=0.0, # L2 penalty on item features
                            user_alpha=0.0, # L2 penalty on user features
                            max_sampled= ms, # for warp
                            random_state=seed) # use multiple seeds

        model.fit(train,  
                  user_features=user_features, 
                  item_features=item_features,
                  epochs=100)

        auc_train.append(lfm.evaluation.auc_score(model, train, user_features=user_features, item_features=item_features).mean())
        recall_train.append(lfm.evaluation.recall_at_k(model, train, k=10, user_features=user_features, item_features=item_features).mean())
        reciprocal_train.append(lfm.evaluation.reciprocal_rank(model, train, user_features=user_features, item_features=item_features).mean())

        auc_test.append(lfm.evaluation.auc_score(model, test, user_features=user_features, item_features=item_features).mean())
        recall_test.append(lfm.evaluation.recall_at_k(model, test, k=10, user_features=user_features, item_features=item_features).mean())
        reciprocal_test.append(lfm.evaluation.reciprocal_rank(model, test, user_features=user_features, item_features=item_features).mean())
        
    hp.loc[i, 'auc_train'] = np.average(auc_train)
    hp.loc[i, 'recall_train'] = np.average(recall_train)
    hp.loc[i, 'reciprocal_train'] = np.average(reciprocal_train)
    hp.loc[i, 'auc_test'] = np.average(auc_test)
    hp.loc[i, 'recall_test'] = np.average(recall_test)
    hp.loc[i, 'reciprocal_test'] = np.average(reciprocal_test)
    hp.to_csv(os.path.join(THIS_FOLDER, "data/hp.csv"), index=False)
        
    if i % 10 == 0 :
        print('Advance ' + str(i / total_length * 100) + '%')
 