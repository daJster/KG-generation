import hashlib
from flask import Flask, render_template, request, redirect, url_for, send_file, jsonify
from rdflib import Graph
from flask_cors import CORS
import networkx as nx
import json
import re
from unidecode import unidecode
from neo4j import GraphDatabase
from pyvis.network import Network
import networkx as nx
from rdflib import Graph, Namespace
import re
import wikipedia
from GoogleNews import GoogleNews
from googlesearch import search
import ast

app = Flask(__name__, template_folder='./', static_folder='assets')
CORS(app)


def load_data_from_db():
    print("load_data_from_db")
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
    print("load_data_from_db_with_node_and_radius", node_name, radius)
    URI = "bolt://localhost:7687"
    AUTH = ("", "")
    with GraphDatabase.driver(URI, auth=AUTH) as client:
        # Check the connection
        client.verify_connectivity()
        # Get all the relations connected to the node with a range of radius in maximum
        print(f"MATCH path = (startNode {{name: '{node_name}'}})-[*1..{radius}]-(endNode) RETURN relationships(path) AS relationships, nodes(path) AS nodes;")
        relations, summary, keys = client.execute_query(
            f"MATCH path = (startNode {{name: '{node_name}'}})-[*1..{radius}]-(endNode) RETURN relationships(path) AS relationships, nodes(path) AS nodes;",
            database_="memgraph",
        )
        # convert to json :  [<Record relationships=[<Relationship element_id='4999' nodes=(<Node element_id='4484' labels=frozenset({'concept'}) properties={'fname': '14 Emmanuel Petit Christophe Leveque.pdf', 'head_type': 'concept', 'name': 'révolte des vignerons du Midi'}>, <Node element_id='4485' labels=frozenset({'concept'}) properties={'fname': '14 Emmanuel Petit Christophe Leveque.pdf', 'head_type': 'concept', 'name': 'révolte Des gueux'}>) type='part of' properties={}>] nodes=[<Node element_id='4484' labels=frozenset({'concept'}) properties={'fname': '14 Emmanuel Petit Christophe Leveque.pdf', 'head_type': 'concept', 'name': 'révolte des vignerons du Midi'}>, <Node element_id='4485' labels=frozenset({'concept'}) properties={'fname': '14 Emmanuel Petit Christophe Leveque.pdf', 'head_type': 'concept', 'name': 'révolte Des gueux'}>]>, <Record relationships=[<Relationship element_id='5001' nodes=(<Node element_id='4484' labels=frozenset({'concept'}) properties={'fname': '14 Emmanuel Petit Christophe Leveque.pdf', 'head_type': 'concept', 'name': 'révolte des vignerons du Midi'}>, <Node element_id='4488' labels=frozenset({'per'}) propert
        
        
        relations = [dict(record) for record in relations] # convert to dict
        list_of_relations = []
        for relation in relations :
            dict_relation = {}
            for i in range (len(relation["relationships"])) :
                relationships = relation["relationships"][i]
                rel_patern = re.compile(r"<Relationship element_id='(\d+)' nodes=\((.*?)\) type='(.*?)' properties={(.*?)}>")
                rel_matches = rel_patern.findall(str(relationships))
                node_patern = re.compile(r"<Node element_id='(\d+)' labels=(.*?) properties={(.*?)}>")
                node_matches = node_patern.findall(str(rel_matches[0][1]))
                node_matches[0] = (node_matches[0][0], node_matches[0][1], dict(ast.literal_eval('{'+node_matches[0][2]+'}')))
                node_matches[1] = (node_matches[1][0], node_matches[1][1], dict(ast.literal_eval('{'+node_matches[1][2]+'}')))
                dict_relation["head"] = node_matches[0][2]["name"]
                dict_relation["type_head"] = node_matches[0][2]["head_type"]
                dict_relation["tail"] = node_matches[1][2]["name"]
                dict_relation["type_tail"] = node_matches[1][2]["head_type"]
                dict_relation["type"] = rel_matches[0][2]
                dict_relation["fname"] = node_matches[0][2]["fname"]
                list_of_relations.append(dict_relation)
        
        # for relation in list_of_relations :
        #     print("head : ", relation["head"], " type : ", relation["type"], " tail : ", relation["tail"])
        
        return list_of_relations       

    
@app.route('/load_data_partially', methods=['POST'])
def construct_graph_partialy():
    print("\nconstruct_graph_partialy\n")
    data = request.get_json()
    node_name = data["search_term"]
    radius = data["radius"]
    group_by = data["group_by"]
    
    relations_clean = []
    relations = load_data_from_db_with_node_and_radius(node_name, radius)

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
            "head_type": relation["type_head"],
            "type": relation_type + "..." if len(relation_type) > 20 else relation_type,
            "tail": tail[:20] + "..." if len(tail) > 20 else tail,
            "tail_type": relation["type_tail"],
            "tail_full": tail,
            "fname": fname
        }
        relations_clean.append(relation)
        
    # create graph
    g = nx.DiGraph()

   # Add entities
    for r in relations_clean:
        g.add_node(r['head'], label=r['head'], title=f" from file : {r['fname']} \n full name : {r['head_full']}", color=create_color_from_string(r['fname'], group_by, r['head_type']), fname=r['fname'], head_full=r['head_full'], head_type=r['head_type'])
        if r['tail'] not in g.nodes:
            g.add_node(r['tail'], label=r['tail'], title=f" from file : {r['fname']} \n full name : {r['tail_full']}", color=create_color_from_string(r['fname'], group_by, r['head_type']), fname=r['fname'], head_full=r['tail_full'], tail_type=r['head_type'])




    # Add relations
    for r in relations_clean:
        # orientated graph
        g.add_edge(r["head"], r["tail"], label=r["type"], color=create_color_from_string(r['fname'], group_by, r["type"]), arrows='to')
    
    # Create a Network instance from the directed graph
    net = Network(height="600px", width="100%", directed=True, notebook=True, cdn_resources='remote')

    # Add nodes and edges from the directed graph to the Network instance
    net.from_nx(g)
    net.barnes_hut()
        
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
        },
        "interaction": {
            "hover": True,
        }
    }

    # Conversion du dictionnaire en chaîne JSON
    options_str = json.dumps(options)

    # Activation du zoom lors du clic sur un nœud
    net.set_options(options_str)
        
        
    # Sauvegarde du graph
    net.save_graph("graph.html")
    
    html_popup = """
    <div class="popup container col-md-12 p-3" id="myPopup"></div>
    <link rel='stylesheet' type='text/css' href='assets/css/loader.css'>
    <script src='assets/js/get_details.js'></script>"""
    

    # Add the event listener code to the generated HTML file
    with open("graph.html", "a") as file:
        file.write(html_popup)
        
    
    
    return send_file("graph.html", mimetype='text/html')


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



        # var xhr = new XMLHttpRequest();
        # xhr.open("POST", "http://localhost:5000/wikipedia_details", true);
        # xhr.setRequestHeader("Content-Type", "application/json");
        # xhr.send(JSON.stringify({"node": nodeLabel}));
        # xhr.onreadystatechange = function() {
        #     if (this.readyState == 4 && this.status == 200) {
        #         var details = JSON.parse(this.responseText);
        #         popup.innerHTML = details["html"];
        #         popup.appendChild(button);
        #     }
        # };
        
@app.route('/wikipedia_details', methods=['POST'])
def wikipedia_details():
    data = request.get_json()
    node = data["node"]
    try : 
        node_type = data["node_type"]
    except :
        node_type = data["node_tail_type"]
    print("node : ", node, "node_type : ", node_type)
    html, wiki = get_wikipedia(node, node_type)
    html = get_google(node, node_type, wiki, html)
    html += get_news(node, node_type)
    return {"html": html}

def get_wikipedia(node, node_type):
    wiki = 0
    try :
        ## give a summury of the wikipedia page and then a button to go to the wikipedia page
        html = f"""
        <div class="container">
            <div class="row">
                <div class="col-12">
                    <h1>Wikipedia</h1>
                    <p>{wikipedia.summary(node)}</p>
                    <a href="{wikipedia.page(node).url}" target="_blank">Go to wikipedia page</a>
                </div>
            </div>
        </div>
        """
        wiki = 1
    ## if there are too many possible pages get the list of possible pages and then let the user choose the node name he wants and recall the function
    except wikipedia.exceptions.DisambiguationError as e:
        html = f"""
        <div class="container">
            <div class="row">
                <div class="col-12">
                    <h1>Wikipedia</h1>
                    <p>Too many possible pages</p>    
                </div>
            </div>
        </div>
        """
    ## if there are no information on wikipedia return "no information found on wikipedia"
    except wikipedia.exceptions.PageError as e:
        html = f"""
        <div class="container">
            <div class="row">
                <div class="col-12">
                    <h1>Wikipedia</h1>
                    <div class="nowiki">
                        <p>No information found on wikipedia</p>
                    </div>
                </div>
            </div>
        </div>
        """
    return html, wiki
def get_google(node, node_type, wiki, html):
    ## return html code of the google search
    html += f"""
    <div class="container">
        <div class="row">
            <div class="col-12">
                <h1>Google search</h1>
                <ul>
    """
    i=0
    try :
        for url in search(node + " " + node_type, num_results=5):
            i+=1
            html += f"""
            <li>
                <a href="{url}" target="_blank">{url}</a>
            </li>
            """
            ## if we found a wikipedia page then we modify the wikipedia html code to add the summary of the wikipedia page found by google
            if "wikipedia" in url:
                ## si on avait pas trouvé de page wikipedia a l'étape de get_wikipedia alors on ajoute le résumé de la page wikipedia trouvé par google dans la section wikipedia class = nowiki
                if wiki == 0 :
                    html = html.replace("""<div class="nowiki">
                        <p>No information found on wikipedia</p>
                    </div>""", '<div class="nowiki"><p>Wikipedia failed to find a page for this node but google seems to have found one, here is the link</p><a href="{url}" target="_blank">Go to wikipedia page</a></div>')
    except :
        pass
    if i == 0:
        html += "<p>We were not able to find any results</p>"
    html += """
                </ul>
            </div>
        </div>
    </div>
    """
    return html


def get_news(node, node_type):
    ## return html code of the news (max 5 news summary)
    try :
        googlenews = GoogleNews()
        googlenews.search(node + " " + node_type)
        result = googlenews.result()
    except :
        result = []
        
    html = f"""
    <div class="container">
        <div class="row">
            <div class="col-12">
                <h1>News</h1>
                <ul>
    """
    i=0
    for news in result[:5]:
        if len(news["title"]) > 5:
            i+=1
            html += f"""
            <li>
                <p>{news["title"]}</p>
                <a href="{news["link"]}" target="_blank">Go to news page</a>
            </li>
            """
    if i == 0:
        html += "<p>We were not able to find any news</p>"
    html += """
                </ul>
            </div>
        </div>
    </div>
    """
    return html



@app.route('/generate_html', methods=['POST'])
def construct_graph():
    print("\nconstruct_graph")
    data = request.get_json()
    relations_clean = []
    relations = load_data_from_db()

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
            "head_type": relation["type_head"],
            "type": relation_type + "..." if len(relation_type) > 20 else relation_type,
            "tail": tail[:20] + "..." if len(tail) > 20 else tail,
            "tail_type": relation["type_tail"],
            "tail_full": tail,
            "fname": fname
        }
        relations_clean.append(relation)
        
    # create graph
    g = nx.DiGraph()

   # Add entities
    for r in relations_clean:
        g.add_node(r['head'], label=r['head'], title=f" from file : {r['fname']} \n full name : {r['head_full']}", color=create_color_from_string(r['fname']), fname=r['fname'], head_full=r['head_full'], head_type=r['head_type'])
        if r['tail'] not in g.nodes:
            g.add_node(r['tail'], label=r['tail'], title=f" from file : {r['fname']} \n full name : {r['tail_full']}", color=create_color_from_string(r['fname']), fname=r['fname'], head_full=r['tail_full'], tail_type=r['head_type'])




    # Add relations
    for r in relations_clean:
        # orientated graph
        g.add_edge(r["head"], r["tail"], label=r["type"], color=create_color_from_string(r['fname']), arrows='to')
    
    # Create a Network instance from the directed graph
    net = Network(height="600px", width="100%", directed=True, notebook=True, cdn_resources='remote')

    # Add nodes and edges from the directed graph to the Network instance
    net.from_nx(g)
    net.barnes_hut()
        
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
        },
        "interaction": {
            "hover": True,
        }
    }

    # Conversion du dictionnaire en chaîne JSON
    options_str = json.dumps(options)

    # Activation du zoom lors du clic sur un nœud
    net.set_options(options_str)
        
        
    # Sauvegarde du graph
    net.save_graph("graph.html")
    
    html_popup = """
    <div class="popup container col-md-12 p-3" id="myPopup"></div>
    <link rel='stylesheet' type='text/css' href='assets/css/loader.css'>
    <script src='assets/js/get_details.js'></script>"""
    

    # Add the event listener code to the generated HTML file
    with open("graph.html", "a") as file:
        file.write(html_popup)
        
    
    
    return send_file("graph.html", mimetype='text/html')

@app.route('/change_name', methods=['POST'])
def change_name():
    data = request.get_json()
    old_name = data["old_name"]
    new_name = data["new_name"]
    
    # Connect to the database and run 2 queries
    URI = "bolt://localhost:7687"
    AUTH = ("", "")
 
    with GraphDatabase.driver(URI, auth=AUTH) as client:
        # Check the connection
        client.verify_connectivity()
        # Get all the relations with type of relation
        relations, summary, keys = client.execute_query(
            f"MATCH (n)-[r]->(m) WHERE n.name = '{old_name}' SET n.name = '{new_name}' RETURN n, r, m;",
            database_="memgraph",
        )
        
        relations, summary, keys = client.execute_query(
            f"MATCH (n)-[r]->(m) WHERE m.name = '{old_name}' SET m.name = '{new_name}' RETURN n, r, m;",
            database_="memgraph",
        )
        
        return "ok"


@app.route('/delete_node', methods=['POST'])
def delete_node(node_name, node_type):
    data = request.get_json()
    node_name = data["node_name"]
    node_type = data["node_type"]
    
    # Connect to the database and run 2 queries
    URI = "bolt://localhost:7687"
    AUTH = ("", "")
    
    with GraphDatabase.driver(URI, auth=AUTH) as client:
        # Check the connection
        client.verify_connectivity()
        # Get all the relations with type of relation
        relations, summary, keys = client.execute_query(
            f"MATCH (n)-[r]->(m) WHERE n.name = '{node_name}' AND n.head_type = '{node_type}' DETACH DELETE n, r;",
            database_="memgraph",
        )
        
        relations, summary, keys = client.execute_query(
            f"MATCH (n)-[r]->(m) WHERE m.name = '{node_name}' AND m.head_type = '{node_type}' DETACH DELETE r, m;",
            database_="memgraph",
        )
        
        return "ok"
    
@app.route('/delete_relation', methods=['POST'])
def delete_relation():
    data = request.get_json()
    head = data["head"]
    tail = data["tail"]
    head_type = data["head_type"]
    tail_type = data["tail_type"]
    
    # Connect to the database and run 2 queries
    URI = "bolt://localhost:7687"
    AUTH = ("", "")
    
    with GraphDatabase.driver(URI, auth=AUTH) as client:
        # Check the connection
        client.verify_connectivity()
        # Get all the relations with type of relation
        relations, summary, keys = client.execute_query(
            f"MATCH (n)-[r]->(m) WHERE n.name = '{head}' AND m.name = '{tail}' AND n.head_type = '{head_type}' AND m.head_type = '{tail_type}' DELETE r;",
            database_="memgraph",
        )
        
        relations, summary, keys = client.execute_query(
            f"MATCH (n)-[r]->(m) WHERE n.name = '{tail}' AND m.name = '{head}' AND n.head_type = '{tail_type}' AND m.head_type = '{head_type}' DELETE r;",
            database_="memgraph",
        )
        
        return "ok"
    
    
def clear_num(text):
    result = []
    for word in text.split(" "):
        try :
            int_val = int(word)
            result.append(str(int_val))
        except ValueError :
            clean_word = [l for l in word if not l.isdigit()]
            if len(clean_word) > 1: # TO CHANGE STV XD
                result.append("".join(clean_word))

    return " ".join(result) 



        


def clear_str(word):
    # remove all caractere like : ',|- and replace them by space
    word = re.sub(r'[\',\|\-]', ' ', word)

    # if their are repetition of a word like : "the the" we remove the second "the" until there is no more repetition
    while re.search(r'(\w+) \1', word) :
        word = re.sub(r'(\w+) \1', r'\1', word)
        
    # if a word is ending with numbers without space like : "the2" we remove the numbers
    
                
    word = clear_num(word)
    # delete double space
    word = re.sub(r' +', ' ', word)
    
    return word    

@app.route('/create_relation', methods=['POST'])
def create_relation():
    data = request.get_json()
                    # xhr.send(JSON.stringify({"head": new_head, "head_type": new_head_type, "fname1": new_fname1, "tail": new_tail, "tail_type": new_tail_type, "fname2": new_fname2, "relation": new_relation}));
    

    head = data["head"]
    head_type = data["head_type"]
    fname1 = data["fname1"]
    tail = data["tail"]
    tail_type = data["tail_type"]
    fname2 = data["fname2"]
    relation = data["relation"]
    
    head = clear_str(head)
    tail = clear_str(tail)
    head_type = clear_str(head_type)
    tail_type = clear_str(tail_type)
    relation_type = clear_str(relation_type)
    fname = clear_str(fname)
    
    if head != "" and tail != "" and relation_type != "" and head != tail and head != relation_type and tail != relation_type :
        # get all node's name where node's head_type is the same as the head_type of the current head node
        query_head = f"MATCH (n) WHERE n.head_type = '{head_type}' RETURN n.name"
        query_tail = f"MATCH (n) WHERE n.head_type = '{head_type}' RETURN n.name"
        
        URI = "bolt://localhost:7687"
        AUTH = ("", "")
        
        with GraphDatabase.driver(URI, auth=AUTH) as client:
            try :
                result = session.run(query_head)
            except :
                print("query error : ", query_head)
            nodes_with_same_head_type = [r["n.name"] for r in result]
            
            try :
                result = session.run(query_tail)
            except :
                print("query error : ", query_tail)
            nodes_with_same_tail_type = [r["n.name"] for r in result]
            
            best_node_head = ""
            best_score_head = 0
            best_node_tail = ""
            best_score_tail = 0
            start_time = time.time()
            for node in nodes_with_same_head_type and nodes_with_same_tail_type :
                score_text_compare = text_compare(node, head)
                if score_text_compare > 0.8 :
                    best_node_head = node
                    best_score_head = score_text_compare
                    break
                else :
                    score_head = compare_with_all_mini(head, node)
                    # print("We need to use all_mini, score is : ", score_head)
                score_text_compare = text_compare(node, tail)   
                if score_text_compare > 0.8 :
                    best_node_tail = node
                    best_score_tail = score_text_compare
                    break
                else :
                    score_tail = compare_with_all_mini(tail, node)
                    # print("We need to use all_mini, score is : ", score_head)
                
                if score_head > best_score_head :
                    best_score_head = score_head
                    best_node_head = node
                    
                if score_tail > best_score_tail :
                    best_score_tail = score_tail
                    best_node_tail = node
                    
            if best_score_head > 0.8 :
                head = best_node_head
                print("c    ", head, "is the same as", best_node_head)
                

            if best_score_tail > 0.8 :
                tail = best_node_tail
                print("c    ", tail, "is the same as", best_node_tail)
                
            partial_merge_time += time.time() - start_time
            
        # check if head with head_type is aleady in the database memgraph
        query = f"MATCH (n:`{head_type}`) WHERE n.name = '{head}' RETURN n"
        with client.session() as session:
            try :
                result = session.run(query)
            except :
                print("query error : ", query)
            if not result.single():
                # add head with head_type to the database memgraph
                query = f"CREATE (n:`{head_type}` {{name: '{head}', fname: '{fname}', head_type: '{head_type}'}})"
                with client.session() as session:
                    try :
                        result = session.run(query)
                    except :
                        print("query error : ", query)
                    history.append(query)
            else :
                print("c    ", query, "already in the database")
                
        # check if tail with tail_type is aleady in the database memgraph
        query = f"MATCH (n:`{tail_type}`) WHERE n.name = '{tail}' RETURN n"
        with client.session() as session:
            result = session.run(query)
            if not result.single():
                # add tail with tail_type to the database memgraph
                query = f"CREATE (n:`{tail_type}` {{name: '{tail}', fname: '{fname}', head_type: '{tail_type}'}})"
                with client.session() as session:
                    try :
                        result = session.run(query)
                    except :
                        print("query error : ", query)
                    history.append(query)
            else :
                print("c    ", query, "already in the database")
                
        # check if relation between head and tail is aleady in the database memgraph
        query = f"MATCH (n:`{head_type}`)-[r:`{relation_type}`]->(m:`{tail_type}`) WHERE n.name = '{head}' AND m.name = '{tail}' RETURN n"
        with client.session() as session:
            try :
                result = session.run(query)
            except :
                print("query error : ", query)
            if not result.single():
                # add relation between head and tail to the database memgraph
                query = f"MATCH (n:`{head_type}`), (m:`{tail_type}`) WHERE n.name = '{head}' AND m.name = '{tail}' CREATE (n)-[r:`{relation_type}`]->(m)"
                with client.session() as session:
                    try :
                        result = session.run(query)
                    except :
                        print("query error : ", query)
                    history.append(query)
            else :
                print("c    ", query, "already in the database")
    else :
        print("something is wrong with the relation : ", head, relation_type, tail)


def create_color_from_string(string, group_by="File", node_type=""):
    # Create a color based on the string
    color = ""
    if group_by == "file":
        color = hashlib.md5(string.encode()).hexdigest()[:6]
    elif group_by == "nodeType":
        color = hashlib.md5(node_type.encode()).hexdigest()[:6]
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
    
@app.route('/get_entities', methods=['GET'])
def get_entities():
    # Define correct URI and AUTH arguments (no AUTH by default)
    URI = "bolt://localhost:7687"
    AUTH = ("", "")
    with GraphDatabase.driver(URI, auth=AUTH) as client:
        entities, _, _= client.execute_query(
            "MATCH (n) RETURN n.name, n.head_type;",
            database_="memgraph",
        )
        return jsonify(entities)


if __name__ == '__main__':
    app.run(debug=True)
