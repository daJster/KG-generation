import json
from pyvis.network import Network
from rdflib import Graph, Namespace
from params import PATH_TO_RDF_FILES, PATH_TO_GRAPH_FILES

def get_graph(kb):
    """
    Generate a graph based on the given knowledge base.

    Parameters:
    kb (KnowledgeBase): The knowledge base containing entities and relations.

    Returns:
    Network: The generated graph.
    """
    # create graph
    g = Network(height="1000px", width="100%", bgcolor="#222222", font_color="white")
    g.barnes_hut()

    # add entities
    for e in kb.entities.items():
        g.add_node(e[0], label=e[0], color="#FFA500")

    # add relations
    for r in kb.relations:
        g.add_edge(r["head"], r["tail"], label=r["type"], color="#FFA500")
    g.save_graph(PATH_TO_GRAPH_FILES+kb.group_name+".html")
    return g



def get_graph2(group_name):
    """
    Generate a graph based on the given group name.

    Args:
        group_name (str): The name of the group.

    Returns:
        Network: The generated graph.
    """
    # Read and load the 'entities' from the JSON file
    with open(PATH_TO_RDF_FILES+group_name+'.json', "r") as json_file:
        entities = json.load(json_file)
        
    g = Graph()

    # Load the RDF data from the Turtle file
    g.parse(PATH_TO_RDF_FILES+group_name+'.ttl', format="turtle")

    # Define the custom namespace used during serialization
    custom_namespace = Namespace("http://example.org/")

    relations = []

    # Iterate over the RDF triples and extract 'head,' 'type,' and 'tail' information
    for head, relation_type, tail in g:
        head = str(head).replace(str(custom_namespace), "").replace("_", " ")
        relation_type = str(relation_type).replace(str(custom_namespace), "").replace("_", " ")
        tail = str(tail).replace(str(custom_namespace), "").replace("_", " ")

        relation = {
            "head": head,
            "type": relation_type,
            "tail": tail
        }
        relations.append(relation)
        
    # create graph
    g = Network(height="1000px", width="100%", bgcolor="#222222", font_color="white")
    g.barnes_hut()

    # add entities
    for e in entities.items():
        g.add_node(e[0], label=e[0], color="#FFA500")

    # add relations
    for r in relations:
        g.add_edge(r["head"], r["tail"], label=r["type"], color="#FFA500")
    g.save_graph(PATH_TO_GRAPH_FILES+group_name+".html")
    return g