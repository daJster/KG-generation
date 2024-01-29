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