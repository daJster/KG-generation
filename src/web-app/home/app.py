from flask import Flask, render_template, request, redirect, url_for, send_file
from rdflib import Graph
from flask_cors import CORS
import networkx as nx
import json
from pyvis.network import Network
from rdflib import Graph, Namespace


app = Flask(__name__, template_folder='./', static_folder='assets')
CORS(app)


# Chargement du graph ttl
graph = Graph()
graph.parse("example_graph.ttl", format="turtle")

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
    search_term = data.get('search_term')
    # Recherche du nœud dans le graph
    query = """
        SELECT ?subject ?predicate ?object
        WHERE {
            ?subject ?predicate ?object.
        }
    """
    results = graph.query(query)

    # Construction d'un sous-graphe centré sur le nœud recherché
    G = nx.Graph()
    for triple in results:
        G.add_node(str(triple['subject']))
        G.add_node(str(triple['object']))
        G.add_edge(str(triple['subject']), str(triple['object']))

    subgraph = nx.ego_graph(G, search_term, radius=5)
    
    # Création du graph
    g = Network(height="600px", width="100%", bgcolor="#222222", font_color="white")
    g.barnes_hut()
    
    # Ajout des nœuds
    for node in subgraph.nodes():
        g.add_node(node, label=node, color="#FFA500")
        
    # Ajout des relations
    for edge in subgraph.edges():
        g.add_edge(edge[0], edge[1], color="#FFA500")
    
    # Sauvegarde du graph
    
    g.save_graph("graph.html")
    return send_file("graph.html", mimetype='text/html')
    
    
    
    
    
    

    

if __name__ == '__main__':
    app.run(debug=True)
