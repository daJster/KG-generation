const searchInput = document.getElementById("searchInput");
const searchButton = document.getElementById("searchButton");
const loadingAnimation = document.getElementById("loadingAnimation");
const searchResults = document.getElementById("searchResults");
const dropdownMenuButton = document.getElementById("dropdownMenuButton");
const loadedContent = document.getElementById("loadedContent");
const htmlFrame = document.getElementById("htmlFrame");


document.addEventListener("DOMContentLoaded", function () {
    
    searchButton.addEventListener("click", function () {
        const query = searchInput.value;
        if (query) {
            loadingAnimation.style.display = "block";
            searchResults.innerHTML = "";
            
            fetch(`/search?query=${query}`)
                .then(response => response.json())
                .then(data => {
                    loadingAnimation.style.display = "none";
                    searchResults.innerHTML = data.results;
                })
                .catch(error => {
                    console.error(error);
                    loadingAnimation.style.display = "none";
                });
        }
    });

    dropdownMenuButton.addEventListener("click", function () {
        event.preventDefault();
        loadingAnimation.style.display = "block";
        searchResults.innerHTML = "";

        fetch("/list_graphs")
            .then(response => response.json())
            .then(data => {
                loadingAnimation.style.display = "none";
                const graphFiles = data.graph_files;
                updateDropdown(graphFiles);
            })
            .catch(error => {
                console.error(error);
                loadingAnimation.style.display = "none";
            });
    });

    function updateDropdown(graphFiles) {
        const dropdownMenu = document.querySelector(".dropdown-menu");
        dropdownMenu.innerHTML = "";

        graphFiles.forEach(graphFile => {
            const dropdownItem = document.createElement("a");
            dropdownItem.classList.add("dropdown-item");
            dropdownItem.href = "#";
            dropdownItem.textContent = graphFile;
            dropdownItem.addEventListener("click", function () {
                loadingAnimation.style.display = "block";
                dropdownMenuButton.textContent = graphFile
                loadAndRenderHTML(graphFile);
            });
            dropdownMenu.appendChild(dropdownItem);
        });
    }

    function loadAndRenderHTML(graphFile) {
        // Fetch the HTML content from Flask
        fetch(`/get_graph_file/${graphFile}`)
            .then(response => response.text())
            .then(htmlContent => {
                const iframeDocument = htmlFrame.contentDocument || htmlFrame.contentWindow.document;
                iframeDocument.open();
                iframeDocument.write(htmlContent);
                iframeDocument.close();
                loadingAnimation.style.display = "none";
            })
            .catch(error => {
                console.error(error);
                loadingAnimation.style.display = "none";
            });
    }

});