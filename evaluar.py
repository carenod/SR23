import sqlite3
import pandas as pd
import os
import math

import recomendar

# recomendar.sql_execute("DELETE FROM interacciones_train")
# recomendar.sql_execute("INSERT INTO interacciones_train SELECT * FROM interacciones")
# recomendar.sql_execute("DELETE FROM interacciones_test")
# id_lectores = recomendar.sql_select("SELECT id_lector FROM interacciones GROUP BY id_lector HAVING COUNT(*) >= 20")
# for row_lector in id_lectores:
#     id_libros = recomendar.sql_select("SELECT * FROM interacciones WHERE id_lector = ?", (row_lector["id_lector"], ))
#     cant_train = int(len(id_libros) * 0.8)
#     # for row in id_libros[0:cant_train]:
#     #     recomendar.sql_execute("INSERT INTO interacciones_train(id_libro, id_lector, rating) VALUES (?, ?, ?)", [row["id_libro"], row_lector["id_lector"], row["rating"]])
#     for row in id_libros[cant_train:]:        
#         recomendar.sql_execute("INSERT INTO interacciones_test SELECT * FROM interacciones_train WHERE id_lector = ? AND id_libro = ?", [row_lector["id_lector"], row["id_libro"]])
#         recomendar.sql_execute("DELETE FROM interacciones_train WHERE id_lector = ? AND id_libro = ?", [row_lector["id_lector"], row["id_libro"]])
#     print(row["id_lector"])

def ndcg(groud_truth, recommendation):
    dcg = 0
    idcg = 0
    for i, r in enumerate(recommendation):
        rel = int(r in groud_truth)
        dcg += rel / math.log2(i+1+1)
        idcg += 1 / math.log2(i+1+1)

    return dcg / idcg

def precision_at(ground_truth, recommendation, n=9):
    return len(set(ground_truth[:n-1]).intersection(recommendation[:len(ground_truth[:n-1])])) / len(ground_truth[:n-1])

id_lectores = recomendar.sql_select("SELECT DISTINCT id_lector FROM interacciones_test")

for row in id_lectores:
    libros_leidos = [row["id_libro"] for row in recomendar.sql_select("SELECT DISTINCT id_libro FROM interacciones_test WHERE id_lector = ?", (row["id_lector"],))]
    recomendacion = recomendar.recomendar(row["id_lector"], interacciones="interacciones_test")
    p = precision_at(libros_leidos, recomendacion)
    n = ndcg(libros_leidos, recomendacion)
    print(f"{row['id_lector']}\t\tndcg: {m:.5f}\tprecision@9: {p: .5f}")

