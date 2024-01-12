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
import re

app = Flask(__name__, template_folder='./', static_folder='assets')
CORS(app)


# Chargement du graph 
# with open('../../../RDFs/new_r.json', "r") as json_file:
#     relations = json.load(json_file)

def record_str_to_dict(record_str):
    # Pattern to match relationships
    rel_pattern = re.compile(r"<Relationship element_id='(\d+)' nodes=\((.*?)\) type='(.*?)' properties={(.*?)}>\]")
    # Pattern to match nodes
    node_pattern = re.compile(r"<Node element_id='(\d+)' labels=frozenset\((.*?)\) properties={(.*?)}>")
    
    # Extract relationships
    rel_matches = rel_pattern.findall(record_str)
    relationships = [{'element_id': rel[0], 
                      'nodes': [{'element_id': node[0], 
                                 'labels': eval(node[1]), 
                                 'properties': eval(node[2])} 
                                for node in [tuple(part.strip() for part in node.split(',')) for node in rel[1].split('),')]], 
                      'type': rel[2], 
                      'properties': eval(rel[3])} for rel in rel_matches]
    
    # Extract nodes
    node_matches = node_pattern.findall(record_str)
    nodes = [{'element_id': node[0], 
              'labels': eval(node[1]), 
              'properties': eval(node[2])} for node in node_matches]
    
    return {'relationships': relationships, 'nodes': nodes}

def transform_to_json(input_data):
    output_data = []
    
    for entry in input_data:
        output_data.append(record_str_to_dict(str(entry)))
    return output_data


def convert_to_desired_format(data):
    result_list = []
    
    for json in data:

        for rel in json["relationships"]:
            if rel != None:
                start_node_id = rel["start"]
                end_node_id = rel["end"]
                relationship_type = rel["label"]

                start_node = next(node for node in json["nodes"] if node["id"] == start_node_id)
                end_node = next(node for node in json["nodes"] if node["id"] == end_node_id)

                result_dict = {
                    "head": start_node["properties"]["name"],
                    "tail": end_node["properties"]["name"],
                    "type": relationship_type,
                    "fname": start_node["properties"]["fname"]
                }
                
                # avoid duplicates
                if result_dict not in result_list:
                    result_list.append(result_dict)

    return result_list


def load_data_from_db():
    URI = "bolt://localhost:7687"
    AUTH = ("", "")
 
    with GraphDatabase.driver(URI, auth=AUTH) as client:
        # Check the connection
        client.verify_connectivity()
        # Get all the relations with type of relation
        relations, summary, keys = client.execute_query(
            # "MATCH (n)-[r]->(m) RETURN n.name AS head, m.name AS tail,  type(r) AS type, n.fname AS fname;",
            "MATCH (n)-[r]->(m) RETURN n.name AS head, n.head_type AS type_head, m.name AS tail, m.head_type AS type_tail, type(r) AS type, n.fname AS fname;",
            database_="memgraph",
        )        
        relations = [dict(record) for record in relations] # convert to dict
        return relations
    
    
def load_data_from_db_with_node_and_radius(node_name, radius):
    URI = "bolt://localhost:7687"
    AUTH = ("", "")
 
    with GraphDatabase.driver(URI, auth=AUTH) as client:
        # Check the connection
        client.verify_connectivity()
        # Get all the relations connected to the node with a range of radius in maximum
        
        relations, summary, keys = client.execute_query(
            f"MATCH path = (startNode {{name: '{node_name}'}})-[*1..{radius}]-(endNode) RETURN relationships(path) AS relationships,  nodes(path) AS nodes;",
            database_="memgraph",
        )
        
        #! TODO  convert to dict with transform_to_json(relations)
        
        relations = convert_to_desired_format(transform_to_json(relations))
        
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
    # relations = load_data_from_db_with_node_and_radius('Audi A1', 3)

    # Iterate over the RDF triples and extract 'head,' 'type,' and 'tail' information
    for relation in relations:
        head = str(relation["head"])
        relation_type = str(relation["type"])
        tail = str(relation["tail"])
        fname = str(relation["fname"])

        # Clean and process each component
        head = clean_string(head)
        relation_type = clean_string(relation_type)
        tail = clean_string(tail)
        # fname = clean_string(fname)

        # Skip the iteration if the node is equal to the filename
        relation = {
            # if len(head) > 20 take the first 20 characters else take the whole string
            "head": head[:20] + "..." if len(head) > 20 else head,
            "head_full": head,
            "type": relation_type,
            "tail": tail[:20] + "..." if len(tail) > 20 else tail,
            "tail_full": tail,
            "fname": fname
        }
        relations_clean.append(relation)
        
    # create graph
    g = Network(height="600px", width="100%", select_menu=True, cdn_resources='remote')#, filter_menu=True)
    g.barnes_hut()

    # add entities
    for r in relations_clean:
        g.add_node(r['head'], label=r['head'], titre=f" from file : {r['fname']} \n full name : {r['head_full']}", color=create_color_from_string(r['fname']))
        if r['tail'] not in g.nodes:
            g.add_node(r['tail'], label=r['tail'], title=f" from file : {r['fname']} \n full name : {r['tail_full']}", color=create_color_from_string(r['fname']))

    # add relations
    for r in relations_clean:
        g.add_edge(r["head"], r["tail"], label=r["type"], color=create_color_from_string(r['fname']))
    
        
    # Définition des options en tant que dictionnaire Python
    options = {
        # for more lisible graph avoid overlap of nodes and edges
        "edges": {
            "smooth": {
                "forceDirection": "none",
                "roundness": 0.15
            }
        },
        "nodes": {
            "shape": "dot",
            "size": 16
        },
        "physics": {
            "forceAtlas2Based": {
                "gravitationalConstant": -26,
                "centralGravity": 0.005,
                "springLength": 230,
                "springConstant": 0.18
            },
            "maxVelocity": 146,
            "solver": "forceAtlas2Based",
            "timestep": 0.35,
            "stabilization": {
                "enabled": True,
                "iterations": 2000,
                "updateInterval": 25
            }
        }
    }

    # Conversion du dictionnaire en chaîne JSON
    options_str = json.dumps(options)

    # Activation du zoom lors du clic sur un nœud
    g.set_options(options_str)
        
        
    # Sauvegarde du graph
    g.save_graph("graph.html")
    
    event_listener_code = """
    network.on("click", function (params) {
    if (params.nodes.length > 0) {
        var nodeId = params.nodes[0];
        network.focus(nodeId, {
        scale: 1.5,  // Adjust the scale as needed
        locked: false,
        animation: {
            duration: 1000,
            easingFunction: "easeInOutQuad"
        }
        });
    }
    });
    """

    # Add the event listener code to the HTML file
    # g.set_edge_smooth("continuous")
    # g.show_buttons()

    # Add the event listener code to the generated HTML file
    with open("graph.html", "a") as file:
        file.write("<script>{}</script>".format(event_listener_code))
    
    
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
            "MATCH (n)-[r]->(m) RETURN n.name AS name_head, m.name AS name_tail,  type(r) AS relation;",
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
