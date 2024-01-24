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
    
    event_listener_code = """
    
    
    // function to get wikipedia details of a node    
    function details(nodeLabel, nodeTitle, nodeFname, nodeHeadFull, nodeTailFull, nodeHeadType, nodeTailType) {
        return `
        <div class="container">
            <div class="row">
                <div class="col-12 text-center mt-5">
                    <h1 class="display-4">${nodeHeadFull}</h1>
                    <p class="lead">From: ${nodeFname}</p>
                </div>
            </div>
        </div>
        `;
    }
    
    
    
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
        
        var node = network.body.nodes[nodeId];
        var nodeLabel = node.options.label;
        var nodeTitle = node.options.title;
        var nodeFname = node.options.fname;
        var nodeHeadFull = node.options.head_full;
        var nodeTailFull = node.options.tail_full;
        var nodeHeadType = node.options.head_type;
        var nodeTailType = node.options.tail_type;
        var div_loader = `<div class="loader">
                                <div class="lds-ellipsis">
                                    <div></div>
                                    <div></div>
                                    <div></div>
                                    <div></div>
                                </div>
                            </div>`;
                        
        var popup = document.getElementById("myPopup");
        
        popup.innerHTML = details(nodeLabel, nodeTitle, nodeFname, nodeHeadFull, nodeTailFull, nodeHeadType, nodeTailType);
              
        
        // call the python function wikipedia_details to get the html details code of the node
        var xhr = new XMLHttpRequest();
        xhr.open("POST", "http://localhost:5000/wikipedia_details", true);
        xhr.setRequestHeader("Content-Type", "application/json");
        xhr.send(JSON.stringify({"node": nodeLabel, "node_type": nodeHeadType, "node_tail_type": nodeTailType}));
        // loading animation
        popup.innerHTML += div_loader;
        xhr.onreadystatechange = function() {
            if (this.readyState == 4 && this.status == 200) {
                var details = JSON.parse(this.responseText);
                var text_info = document.createElement("div");
                text_info.innerHTML += details["html"];
                popup.appendChild(text_info);
                //popup.appendChild(button);       
                // loading animation stop
                popup.innerHTML = popup.innerHTML.replace(div_loader, "");                    
                
                // button to change the name of the node
                var container = document.createElement("div");
                container.classList.add("container", "text-center", "col-md-12");
                var button = document.createElement("button");
                button.classList.add("btn", "btn-primary", "btn-sm", "rounded", "p-2", "col-md-3");
                button.innerHTML = "Change name";
                button.onclick = function() {
                    var new_name = prompt("Please enter the new name", nodeLabel);
                    if (new_name != null) {
                        // call the python function change_name to change the name of the node
                        var xhr = new XMLHttpRequest();
                        xhr.open("POST", "http://localhost:5000/change_name", true);
                        xhr.setRequestHeader("Content-Type", "application/json");
                        xhr.send(JSON.stringify({"old_name": nodeLabel, "new_name": new_name}));
                        xhr.onreadystatechange = function() {
                            if (this.readyState == 4 && this.status == 200) {
                                // change the name of the node
                                node.options.label = new_name;
                                node.options.title = node.options.title.replace(nodeLabel, new_name);
                                nodeLabel = new_name;
                                nodeTitle = node.options.title;
                                // update the popup
                                popup.innerHTML = details(nodeLabel, nodeTitle, nodeFname, nodeHeadFull, nodeTailFull);
                            }
                        };
                    }
                };
                document.querySelectorAll('h1').forEach(element => {element.className = 'display-4';});
                container.appendChild(button);
                popup.appendChild(container);
                                    
            }
        };
        
        popup.classList.toggle("show");
        // update body size to take into account the popup
        network.setSize("100%", "100%");       
    }
    });
    """
    html_popup = """
    <div class="popup" id="myPopup"></div>    
    """
    
    style = """
    <style>
    .lds-ellipsis {
    display: inline-block;
    position: relative;
    left: 50%;
    top: 5%;
    width: 90px;
    height: 90px;
    }
    .lds-ellipsis div {
    position: absolute;
    top: 33px;
    width: 13px;
    height: 13px;
    border-radius: 50%;
    background: #cef;
    animation-timing-function: cubic-bezier(0, 1, 1, 0);
    }
    .lds-ellipsis div:nth-child(1) {
    left: 8px;
    animation: lds-ellipsis1 0.6s infinite;
    }
    .lds-ellipsis div:nth-child(2) {
    left: 8px;
    animation: lds-ellipsis2 0.6s infinite;
    }
    .lds-ellipsis div:nth-child(3) {
    left: 32px;
    animation: lds-ellipsis2 0.6s infinite;
    }
    .lds-ellipsis div:nth-child(4) {
    left: 56px;
    animation: lds-ellipsis3 0.6s infinite;
    }
    @keyframes lds-ellipsis1 {
    0% {
        transform: scale(0);
    }
    100% {
        transform: scale(1);
    }
    }
    @keyframes lds-ellipsis3 {
    0% {
        transform: scale(1);
    }
    100% {
        transform: scale(0);
    }
    }
    @keyframes lds-ellipsis2 {
    0% {
        transform: translate(0, 0);
    }
    100% {
        transform: translate(24px, 0);
    }
    }
    </style>
    """
    
    


    # Add the event listener code to the HTML file
    # g.set_edge_smooth("continuous")
    # g.show_buttons()

    # Add the event listener code to the generated HTML file
    with open("graph.html", "a") as file:
        file.write(html_popup + style + "<script>" + event_listener_code + "</script>")
        
    
    
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
