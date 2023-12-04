import pandas as pd
import lightfm as lfm
from lightfm import data
from lightfm import cross_validation
from lightfm import evaluation

# cargo dataset interacciones
df_int = pd.read_csv("./data/interactions.csv")
df_int.head()
# cargo dataset papers
df_items = pd.read_csv("./data/df_papers_final.csv")

# armo item_features
ifs = []

for index, row in df_items.iterrows():
    ifs.append( (row["DOI"], [row["publisher"]])  )
    #ifs.append( (row["id_libro"], {row["autor"]:0.1, row["genero"]: 0.9} )  )

# aramo interacciones
ds = lfm.data.Dataset()
item_features_list = df_items["publisher"].unique().tolist() # + df_items["score"].unique().tolist() + df_items["author_name"].unique().tolist()
ds.fit(users=df_int["scholar_id"].unique(), items=df_int["references"].unique(), item_features=item_features_list)

# las interacciones no tienen pesos, weight=1 para todas
item_features = ds.build_item_features(ifs)
item_features
(interactions, weights) = ds.build_interactions(df_int[["scholar_id", "references"]].itertuples(index=False))

(train, test) = lfm.cross_validation.random_train_test_split(interactions, test_percentage=0.2, random_state=42)

#TODO optimizar
model = lfm.LightFM(no_components=10, k=5, n=10, learning_schedule='adagrad', loss='logistic', learning_rate=0.05, rho=0.95, epsilon=1e-06, item_alpha=0.0, user_alpha=0.0, max_sampled=10, random_state=42)
model.fit(train, epochs=10, num_threads=2)

train_precision = lfm.evaluation.precision_at_k(model, train, k=10, num_threads=2)
test_precision = lfm.evaluation.precision_at_k(model, test, k=10, num_threads=2)

print("Precision@10 en training:", train_precision.mean())
print("Precision@10 en testing:", test_precision.mean())