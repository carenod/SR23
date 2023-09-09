from crossref_commons.retrieval import get_entity
from crossref_commons.types import EntityType, OutputType
import json




# Esto devuelve todas las citas de un paper
dictionary = get_entity('10.1093/pcp/pcac126', EntityType.PUBLICATION, OutputType.JSON)

json_object = json.dumps(dictionary, indent=4)

with open("sample.json", "w") as outfile:
    outfile.write(json_object)