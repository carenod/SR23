# SR23

Este es repositorio del trabajo final de la materia Sistemas de Recomendación de la Maestria en Data Mininf de FCEN-UBA.

## Objetivo

El objetivo de este trabajo es generar un sistema de recomendación (SR) de papers científicos basado en los papers que un autor ya ha leido. 
Se toman como papers que el autor ha leido aquellos que ha citado en su trabajos pasados.

## Datos

Se utiliza [scholarly](https://pypi.org/project/scholarly/) para buscar los papers publicados por autores. 
Luego, se utilizará [crossref_commons_py](https://gitlab.com/crossref/crossref_commons_py) para obener los papers que han citado.

## Pagina web

El recomendador se puede visitar haciendo click [aquí](http://carenod.pythonanywhere.com/).
