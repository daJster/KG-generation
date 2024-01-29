# Knowledge Graph Generation

## Overview

This project aims to generate a knowledge graph from PDF files by extracting text and identifying relations within the text. The generated knowledge graph can be visualized through a Streamlit-based frontend application.

## Table of Contents

1. [Introduction](#introduction)
2. [Installation](#installation)
3. [Software Requirements](#software-requirements)
4. [Pipeline Explanation](#pipeline-explanation)
5. [Running the Application](#running-the-application)
6. [Folder Structure](#folder-structure)
7. [Acknowledgments](#acknowledgments)

## Introduction

The knowledge graph generation process involves extracting text from PDF files, identifying relationships within the text, and visualizing the relationships in a graph. This README provides a comprehensive guide on setting up the project and running the application.

## Installation

Clone the repository to your local machine:

```bash
git clone https://github.com/daJster/KG-generation.git
cd KG-generation
```

## Software Requirements
Install the required packages using pip :
```bash
pip3 install -r requirements.txt
```

Ensure the following Python packages are installed:

- nltk
- llm
- pygraft
- rdflib
- torch
- torchvision
- torchaudio
- pyvis
- PyMuPDF
- langdetect
- transformers
- -U sentence-transformers
- streamlit
- flask

## Pipeline Explanation

The pipeline consists of the following steps:

1) Text Extraction: Extract text from PDF files using PyMuPDF.

2) Relation Extraction: Utilize NLP libraries such as nltk, llm, and transformers for relation extraction from the extracted text.

3) Merge entities: Avoid duplicate entities by merging entities. Use the AI model including All_Mini to identify same semantic entities.

4) Graph Generation: Construct a knowledge graph using extracted relations. Pygraft and rdflib are used for graph creation.

5) Admin interface: Automize pipeline use with streamlit and choose any pdf file to run in our model.

6) User Interface (UI): Create a Streamlit frontend application (app.py) for users to interact with the generated knowledge graph.


## Running the Application
### Admin interface
Run the main.py file for the first time to build streamlit web-app and to execute the knowledge graph generation process :

```bash
python3 main.py
```

Then run the streamlit web-app :

```bash
streamlit run main.py
```

If you encounter any issues, run the following command in the terminal and run the Streamlit app again.

```bash
export PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION=python
```

Visit http://localhost:8501 in your web browser to access the admin web-app.


### User interface (graph visualization)
To run the UI interface :
```bash
python3 app.py
```

## Folder Structure
```
└── KG-generation
    ├── Knowledge Graphs.pdf
    ├── README.md
    ├── datasets
    │   ├── acronyms.txt
    │   ├── differences.txt
    │   ├── nearly_similarities.txt
    │   ├── plurals.txt
    │   └── similarities.txt
    ├── dockerfile
    ├── notebooks
    │   ├── Entities.ipynb
    │   ├── Evaluation_Metrics.ipynb
    │   ├── Merge.ipynb
    │   ├── NLP_for_economy.ipynb
    │   └── NLPlanet.ipynb
    ├── requirements.txt
    └── src
        ├── KB_generation.py
        ├── all_mini.py
        ├── data_selection.py
        ├── emissions.csv
        ├── game_of_thrones.html
        ├── graph_generation.py
        ├── main.py
        ├── merge_RDF.py
        ├── params.py
        ├── plot_stats.py
        ├── plot_times.png
        ├── test_text_compare.py
        ├── text_selection.py
        └── web-app
            └── home
                ├── app.py
                ├── graph.html
                ├── index.html
                └── lib
                    ├── bindings
                       └── utils.js
```
