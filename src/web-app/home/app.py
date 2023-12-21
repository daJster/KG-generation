import hashlib
from flask import Flask, render_template, request, redirect, url_for, send_file
from rdflib import Graph
from flask_cors import CORS
import networkx as nx
import json
import re
from unidecode import unidecode
from neo4j import GraphDatabase
from pyvis.network import Network
from rdflib import Graph, Namespace


app = Flask(__name__, template_folder='./', static_folder='assets')
CORS(app)


# Chargement du graph 
# with open('../../../RDFs/new_r.json', "r") as json_file:
#     relations = json.load(json_file)


def load_data_from_db():
    URI = "bolt://localhost:7687"
    AUTH = ("", "")
 
    with GraphDatabase.driver(URI, auth=AUTH) as client:
        # Check the connection
        client.verify_connectivity()
        # Get all the relations with type of relation
        relations, summary, keys = client.execute_query(
            "MATCH (n)-[r]->(m) RETURN n.name AS head, m.name AS tail,  type(r) AS type, n.fname AS fname;",
            database_="memgraph",
        )        
        relations = [dict(record) for record in relations]
        return relations
    


# Function to clean and process a string
def clean_string(value):
    # Replace %20 and %C3%A9 with spaces
    value = re.sub(r'%20|%C3%A9', ' ', value)
    
    # Remove special characters and accents using unidecode
    value = unidecode(value)
    
    # Replace underscores with spaces
    value = value.replace("_", " ")
    
    # Take the last element after splitting by '/'
    value = value.split('/')[-1]
    
    return value

@app.route('/') #, methods=['GET', 'POST'])
def index():
    # if request.method == 'POST':
    #     search_term = request.form['search']
    #     return construct_graph(search_term)
    # else:
    return render_template('index.html')

@app.route('/generate_html', methods=['POST'])
def construct_graph():
    data = request.get_json()

    relations_clean = []
    relations = load_data_from_db()

    # Iterate over the RDF triples and extract 'head,' 'type,' and 'tail' information
    for relation in relations:
        head = str(relation["head"])
        relation_type = str(relation["type"])
        tail = str(relation["tail"])

        # Clean and process each component
        head = clean_string(head)
        relation_type = clean_string(relation_type)
        tail = clean_string(tail)

        # Skip the iteration if the node is equal to the filename
        relation = {
            "head": head,
            "type": relation_type,
            "tail": tail
        }
        relations_clean.append(relation)
        
    # create graph
    g = Network(height="600px", width="100%", select_menu=True, cdn_resources='remote')#, filter_menu=True)
    g.barnes_hut()

    # add entities
    for r in relations:
        g.add_node(r['head'], label=r['head'], titre=f" from file : {r['fname']}", color=create_color_from_string(r['fname']))
        if r['tail'] not in g.nodes:
            g.add_node(r['tail'], label=r['tail'], title=f" from file : {r['fname']}", color=create_color_from_string(r['fname']))

    # add relations
    for r in relations:
        g.add_edge(r["head"], r["tail"], label=r["type"], color=create_color_from_string(r['fname']))
    
    # Sauvegarde du graph
    g.save_graph("graph.html")
    return send_file("graph.html", mimetype='text/html')

def create_color_from_string(string):
    # Create a color based on the string
    color = hashlib.md5(string.encode()).hexdigest()[:6]
    return f"#{color}"

    
# function to create graph from memgraph database
def create_graph_from_db():
    # Define correct URI and AUTH arguments (no AUTH by default)
    URI = "bolt://localhost:7687"
    AUTH = ("", "")
    
    with GraphDatabase.driver(URI, auth=AUTH) as client:
        # Check the connection
        client.verify_connectivity()
        # Get all the relations with type of relation
        relations, summary, keys = client.execute_query(
            "MATCH (n)-[r]->(m) RETURN n.name_head AS name_head, m.name_tail AS name_tail,  type(r) AS relation;",
            database_="memgraph",
        )
        
        # createe graph from relations
        g = Network(height="600px", width="100%", select_menu=True, cdn_resources='remote')#, filter_menu=True)
        g.barnes_hut()

        # add entities
        for r in relations:
            g.add_node(r['name_head'], label=r['name_head'], color=create_color_from_string(r['fname']))
            if r['name_tail'] not in g.nodes:
                g.add_node(r['name_tail'], label=r['name_tail'], color=create_color_from_string(r['fname']))

        # add relations
        for r in relations:
            g.add_edge(r["name_head"], r["name_tail"], label=r["relation"], color=create_color_from_string(r['fname']))
        
        # Sauvegarde du graph
        g.save_graph("graph.html")
        return send_file("graph.html", mimetype='text/html')
    

if __name__ == '__main__':
    app.run(debug=True)
