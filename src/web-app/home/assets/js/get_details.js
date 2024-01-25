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

            // button to delete the node : nodeHeadFull, nodeHeadType
            var container = document.createElement("div");
            container.classList.add("container", "text-center", "col-md-12");
            var button = document.createElement("button");
            button.classList.add("btn", "btn-danger", "btn-sm", "rounded", "p-2", "col-md-3");
            button.innerHTML = "Delete node";
            button.onclick = function() {
                var new_name = prompt("Please confirm the name of the node to delete", nodeLabel);
                if (new_name != null) {
                    // call the python function delete_node to delete the node
                    var xhr = new XMLHttpRequest(); 
                    xhr.open("POST", "http://localhost:5000/delete_node", true);
                    xhr.setRequestHeader("Content-Type", "application/json");
                    xhr.send(JSON.stringify({"node": nodeLabel, "node_type": nodeHeadType}));
                    xhr.onreadystatechange = function() {
                        if (this.readyState == 4) {
                            if (this.status == 200) {
                                // delete the node
                                network.body.data.nodes.remove(nodeId);
                                // close the popup
                                popup.classList.toggle("show");
                            } else {
                                // Handle error case if needed
                                console.error("Failed to delete node");
                            }
                        }
                    };
                }
            }
            container.appendChild(button);
            popup.appendChild(container);



            // button to delete the relation : nodeHeadFull, nodeHeadType, nodeTailFull, nodeTailType
            var container = document.createElement("div");
            container.classList.add("container", "text-center", "col-md-12");
            var button = document.createElement("button");
            button.classList.add("btn", "btn-danger", "btn-sm", "rounded", "p-2", "col-md-3");
            button.innerHTML = "Delete relation";
            button.onclick = function() {
                // call the python function delete_relation to delete the relation
                var xhr = new XMLHttpRequest();
                xhr.open("POST", "http://localhost:5000/delete_relation", true);
                xhr.setRequestHeader("Content-Type", "application/json");
                xhr.send(JSON.stringify({"head": nodeHeadFull, "head_type": nodeHeadType, "tail": nodeTailFull, "tail_type": nodeTailType}));
                xhr.onreadystatechange = function() {
                    if (this.readyState == 4 && this.status == 200) {
                        // delete the relation
                        network.body.data.edges.remove(nodeId);
                        // close the popup
                        popup.classList.toggle("show");
                    }
                };
            };
            container.appendChild(button);
            popup.appendChild(container);

            // button to create a new relation : ask to the user :  nodeHead, nodeHeadType, nodeTail, nodeTailType, nodeFname1 nodeFname2, relation

            var container = document.createElement("div");
            container.classList.add("container", "text-center", "col-md-12");
            var button = document.createElement("button");
            button.classList.add("btn", "btn-success", "btn-sm", "rounded", "p-2", "col-md-3");
            button.innerHTML = "Create relation";
            button.onclick = function() {
                //ask to the user :  nodeHead, nodeHeadType, nodeTail, nodeTailType, nodeFname1 nodeFname2, relation
                var new_head = prompt("Please enter the new head", nodeHeadFull);
                var new_head_type = prompt("Please enter the new head type", nodeHeadType);
                var new_fname1 = prompt("Please enter the new fname1", "fname");
                var new_tail = prompt("Please enter the new tail", nodeTailFull);
                var new_tail_type = prompt("Please enter the new tail type", nodeTailType);
                var new_fname2 = prompt("Please enter the new fname2", "fname");
                var new_relation = prompt("Please enter the new relation", "relation");
                if (new_head != null && new_head_type != null && new_fname1 != null && new_tail != null && new_tail_type != null && new_fname2 != null && new_relation != null) {
                    // call the python function create_relation to create the relation
                    var xhr = new XMLHttpRequest();
                    xhr.open("POST", "http://localhost:5000/create_relation", true);
                    xhr.setRequestHeader("Content-Type", "application/json");
                    xhr.send(JSON.stringify({"head": new_head, "head_type": new_head_type, "fname1": new_fname1, "tail": new_tail, "tail_type": new_tail_type, "fname2": new_fname2, "relation": new_relation}));
                    xhr.onreadystatechange = function() {
                        if (this.readyState == 4 && this.status == 200) {
                            // create the relation
                            var new_node = JSON.parse(this.responseText);
                            network.body.data.nodes.add(new_node);
                            // close the popup
                            popup.classList.toggle("show");
                        }
                    };
                }
            };
            container.appendChild(button);
            popup.appendChild(container);
        }
    };
    
    popup.classList.toggle("show");
    // update body size to take into account the popup
    network.setSize("100%", "100%");       
}
});