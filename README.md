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
7. [Notebooks](#Notebooks)

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

### Memgraph Installation

1) Install Docker if not already installed. Refer to the [official documentation](https://docs.docker.com/get-docker/) for installation instructions.

2) Start Docker by running the following command:

```bash
sudo service docker start
```

3) Install Memgraph using the following commands if not already installed:

```bash
sudo docker run -p 7687:7687 -p 7444:7444 -p 3000:3000 --name memgraph memgraph/memgraph-platform
```

4) Start Memgraph using the following command:

```bash
sudo docker start memgraph
```
5) Check if Memgraph is running by visiting http://localhost:3000 in your web browser.

## Pipeline Explanation

The pipeline consists of the following steps:

1) Text Extraction: Extract text from PDF files using PyMuPDF.

2) Relation Extraction: Utilize NLP libraries such as nltk, llm, and transformers for relation extraction from the extracted text.

3) Merge entities: Avoid duplicate entities by merging entities. Use the AI model including All_Mini to identify same semantic entities.

4) Graph Generation: Construct a knowledge graph using extracted relations. Pygraft and rdflib are used for graph creation.

5) Admin interface: Automize pipeline use with streamlit and choose any pdf file to run in our model.

6) User Interface (UI): Create a Streamlit frontend application (app.py) for users to interact with the generated knowledge graph.


## Running the Application

Both the admin and user interfaces need memgraph to be running. Ensure that memgraph is running before proceeding (refer to the [Memgraph Installation](#memgraph-installation) section for instructions).

### Admin interface
Run the main.py file for the first time to build streamlit web-app and to execute the knowledge graph generation process :

```bash
python3 src/pipeline/main.py
```

Then run the streamlit web-app :

```bash
streamlit run src/pipeline/main.py
```

If you encounter any issues, run the following command in the terminal and run the Streamlit app again.

```bash
export PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION=python
```

Visit http://localhost:8501 in your web browser to access the admin web-app.


### User interface (graph visualization)
To run the UI interface :
1) Go to the web-app folder :
```bash
cd src/web-app
```
2) Run the app.py file :
```bash
python3 app.py
```

> :warning: **DO NOT run python3 src/web-app directly**: otherwise you won't be able to use radius search in the graph

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
    ├── docker-compose.yml
    ├── dockerfile
    ├── notebooks
    │   ├── Entities.ipynb
    │   ├── Entity_Alignment_Hash.ipynb
    │   ├── Evaluation_Metrics.ipynb
    │   ├── Fine_tuning_2.ipynb
    │   ├── Merge.ipynb
    │   ├── NLP_for_economy.ipynb
    │   ├── NLPlanet.ipynb
    │   └── Pykeen_Metrics.ipynb
    ├── requirements.txt
    └── src
        ├── pipeline
        │   ├── KB_generation.py
        │   ├── all_mini.py
        │   ├── data_selection.py
        │   ├── emissions.csv
        │   ├── main.py
        │   ├── merge_RDF.py
        │   ├── params.py
        │   └── text_selection.py
        ├── test_text_compare.py
        └── web-app
            ├── app.py
            ├── assets
            │   ├── css
            │   │   ├── loader.css
            │   │   └── style.css
            │   ├── js
            │   │   ├── get_details.js
            │   │   ├── main.js
            │   │   └── wikipedia_details.js
            ├── game_of_thrones.html
            ├── graph.html
            ├── index.html
```  

# Notebooks
The notebooks folder contains the following Jupyter notebooks:


## Entities.ipynb
This notebook focuses on accelerating the merge process of relations or entities in a graph, especially when dealing with large graphs where the merge operation can be computationally expensive (exponential complexity). The objective is to pre-categorize entities quickly and efficiently. The notebook explores various methods, including using BERT, NER (Named Entity Recognition), Zero-shot classification, FastText with a linear classifier, and an LSTM (Long Short-Term Memory) model.

## Entity_Alignment_Hash.ipynb

This notebook introduces an approach for entity alignment and merging utilizing sentence embeddings and hashing to enhance processing efficiency. The primary focus is on addressing the challenge of merging entities or aligning them in a knowledge graph. The notebook employs a hashing function to group entities with similar types and presents practical examples to illustrate the merging process.

## Evaluation_Metrics.ipynb


Analyzing a knowledge graph poses challenges as there is no ideal metric. Metrics such as the accuracy of information, the relationships between entities, and the overall coherence are subjective and often require expert judgment. Implementing these metrics on-the-fly in a calculative manner is challenging. While there are no supervised metrics for dynamic evaluation, unsupervised metrics can help compare the evolution of a graph. By observing changes in metric values between iterations, one can infer improvements or deteriorations. Although these metrics are not implemented here, exploring such approaches could be beneficial.

To address the absence of a native metric, this notebook proposes the use of [PyKEEN](https://pykeen.readthedocs.io/en/stable/tutorial/understanding_evaluation.html), an implementation offering a variety of evaluation metrics.

Before running the notebook, install PyKEEN:

```bash
pip install pykeen
```

The notebook calculates various metrics such as Mean Rank, Hits@K, and Mean Reciprocal Rank (MRR) from the results.

## Fine_tuning_2.ipynb

This notebook demonstrates the fine-tuning of the "All-MiniLM-L6-v2" model to address the challenge of entity alignment and merging. The model, known for its small size, fast inference, and proficiency in identifying sentence similarities, was originally trained on a dataset generated by OpenAI's gpt4 model, focusing on the fields of economy and finance.

## Merge.ipynb

This file represents an initial ''trial'' version for merging entities, not triplets, extracted from mRebel. It does not require improvement, as it is an old version. The new version favors merging across the entire relation.

## NLP_for_economy.ipynb
This pipeline aims to test the inference time based on the length of the text/context given to mRebel and different hyperparameters to obtain the best set of performance.

## NLPlanet.ipynb
This pipeline focuses on extracting triplets using the REBEL and mREBEL models. It involves comparing inferences from both models and adapting the pipeline accordingly, including various tests. This comprehensive pipeline covers various aspects, from short text extraction to processing longer documents and generating knowledge graphs from PDFs, providing a versatile tool for information extraction and analysis.

## Pykeen_Metrics.ipynb
This notebook uses the Pykeen library to evaluate the robustness of a set of triplets, which form a knowledge graph. It focuses on three evaluation metrics: Mean Rank (MR), Mean Reciprocal Rank (MRR), and Hits at K.