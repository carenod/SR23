import pandas as pd
import lightfm as lfm
from lightfm import data
from lightfm import cross_validation
from lightfm import evaluation 
from lightfm.evaluation import auc_score
import time

# cargo dataset interacciones
df_int = pd.read_csv("./data/df_int.csv")
df_int.head()
# cargo dataset papers
df_items = pd.read_csv("./data/df_items.csv")
df_items.head()
df_items.shape

# me quedo con las interacciones que estan en df_items
df_int = df_int[df_int['references'].isin(df_items['DOI'])]
df_items = df_items[df_items['DOI'].isin(df_int['references'])]
df_int.shape

# armo item_features
ifs = []
for index, row in df_items.iterrows():
    ifs.append( (row["DOI"], [row["publisher"], row["type"], row["last_author"]])  )
    #ifs.append( (row["id_libro"], {row["autor"]:0.1, row["genero"]: 0.9} )  )

# aramo interacciones
ds = lfm.data.Dataset()
item_features_list = df_items["publisher"].unique().tolist() + df_items["type"].unique().tolist() + df_items["last_author"].unique().tolist() 
# sin features
ds.fit(users=df_int["scholar_id"].unique(), items=df_int["references"].unique())
# con features
ds.fit(users=df_int["scholar_id"].unique(), items=df_int["references"].unique(), item_features=item_features_list)

# las interacciones no tienen pesos, weight=1 para todas
item_features = ds.build_item_features(ifs)
item_features
(interactions, weights) = ds.build_interactions(df_int[["scholar_id", "references"]].itertuples(index=False))

(train, test) = lfm.cross_validation.random_train_test_split(interactions, test_percentage=0.2, random_state=42)

#TODO optimizar
model = lfm.LightFM(no_components=100, k=5, n=10, learning_schedule='adagrad', loss='warp', learning_rate=0.05, 
                    rho=0.95, epsilon=1e-06, item_alpha=0.0, user_alpha=0.0, max_sampled=10, random_state=42)

# sin features
model.fit(train, epochs=100, num_threads=2)
train_precision = lfm.evaluation.precision_at_k(model, train, k=100, num_threads=2)
test_precision  = lfm.evaluation.precision_at_k(model, test,  k=100, num_threads=2)
# con features
model.fit(train, item_features=item_features, epochs=1000, num_threads=2)
train_precision = lfm.evaluation.precision_at_k(model, train, item_features=item_features, k=100, num_threads=2)
test_precision  = lfm.evaluation.precision_at_k(model, test,  item_features=item_features, k=100, num_threads=2)

print("Precision@10 en training:", train_precision.mean())
print("Precision@10 en testing:", test_precision.mean())

# prediccion

user_id_map, user_feature_map, item_id_map, item_feature_map = ds.mapping()
user_id_map



alpha = 1e-05
epochs = 70
num_components = 32

warp_model = lfm.LightFM(no_components=num_components,
                    loss='warp',
                    learning_schedule='adagrad',
                    max_sampled=100,
                    user_alpha=alpha,
                    item_alpha=alpha)

warp_duration = []
warp_auc = []

for epoch in range(epochs):
    start = time.time()
    warp_model.fit_partial(train, epochs=1)
    warp_duration.append(time.time() - start)
    warp_auc.append(auc_score(warp_model, test, train_interactions=train).mean())