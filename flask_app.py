from flask import Flask, request, render_template, make_response, redirect
import recomendar
import random
import sys

app = Flask(__name__)

@app.route('/', methods=('GET', 'POST'))
def login():
    # si me mandaron el formulario y tiene id_lector...
    if request.method == 'POST' and 'name' in request.form:
        name = request.form['name']
        scholar_id = recomendar.get_scholar_id(name)

        # chequeo si el user es nuevo
        if scholar_id is None:
            scholar_id = recomendar.generate_id()
            # creo el usuario al insertar el id_lector en la tabla "lectores"
            recomendar.crear_usuario(scholar_id, name)
            recomendar.retrain_model()

        # mando al usuario a la página de recomendaciones
        res = make_response(redirect("/recomendaciones"))

        # pongo el id_lector en una cookie para recordarlo
        res.set_cookie('scholar_id', scholar_id)
        res.set_cookie('name', name)
        return res

    # si alguien entra a la página principal y conozco el usuario
    if request.method == 'GET' and 'scholar_id' in request.cookies:
        return make_response(redirect("/recomendaciones"))

    # sino, le muestro el formulario de login
    if request.method == 'GET':
        query = "SELECT DISTINCT name FROM autores;"
        autores = [r["name"] for r in recomendar.sql_select(query, params=None)]
        return render_template('login.html', autores=autores)

@app.route('/recomendaciones', methods=('GET', 'POST'))
def recomendaciones():

    # si no hay cookie anda a loguearte pa
    if 'scholar_id' not in request.cookies:
        return make_response(redirect("/"))

    scholar_id = request.cookies.get('scholar_id')
    name = request.cookies.get('name')

    # recomendaciones
    all_papers = recomendar.recomendar(scholar_id)
    papers = all_papers[:9]
    print(papers)

#    if request.method == 'POST' and 'query' in request.form:
#        papers = recomendar.recomendar_whoosh(request.form['query'])
#        #if num_hits > 0:
#        #    papers = all_papers
#        #else:
#        #
    print(request.form)
    # me envían el formulario
    if request.method == 'POST':
        if 'query' in request.form:
            papers = recomendar.recomendar_whoosh(request.form['query'])
            print(len(papers))
            print('searching for ' + request.form['query'])
        #if 'more' in request.form:
        if 'more' in request.form:
            papers = random.sample(all_papers, 9)
            print('showing new recomendations')
        for DOI in request.form.keys():
            try: # agrego puntajes
                read = int(request.form[DOI])
                recomendar.insertar_interacciones(DOI, scholar_id, read)
                print('adding interactions')
            except:
                continue

    cant_valorados = len(recomendar.leidos(scholar_id))
    cant_ignorados = len(recomendar.ignorados(scholar_id))

    return render_template("recomendaciones.html", papers=papers, name=name, scholar_id=scholar_id, cant_valorados=cant_valorados, cant_ignorados=cant_ignorados)

@app.route('/reset')
def reset():
    scholar_id = request.cookies.get('scholar_id')
    recomendar.reset_usuario(scholar_id)

    return make_response(redirect("/recomendaciones"))


#if __name__ == "__main__":
#    app.run(debug=True)