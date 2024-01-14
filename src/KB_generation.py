import math
import torch
import wikipedia
from neo4j import GraphDatabase 
from rdflib import Graph, URIRef, Literal, Namespace, RDF, RDFS
from urllib.parse import quote
import re
import uuid
import json
from merge_RDF import similarity_score
from params import tokenizer, rdf_model, PATH_TO_RDF_FILES, ACTIVATE_SIMILARITY, DEVICE
from all_mini import compare_with_all_mini

# knowledge base class for meta data collection
class KB():
    def __init__(self):
        self.relations = []
        self.pdf_name = ""

    # def are_relations_equal(self, r1, r2, similarity_threshold=0.8):
    #     is_equal = all(r1[attr] == r2[attr] for attr in ["head", "type", "tail"])
    #     if ACTIVATE_SIMILARITY :
    #         sim_score = similarity_score(r1, r2)
    #         is_equal = is_equal or sim_score > similarity_threshold
    #     return is_equal

    # def exists_relation(self, r1):
    #     # check if relations are equal among those with the same "head_type" for head and "tail_type" for tail, to limit the number of comparisons
        
    #     # get all relations with the same "head_type" for head and "tail_type" for tail
    #     relations_with_same_head_type = [r for r in self.relations if r["head_type"] == r1["head_type"]]
    #     relations_with_same_tail_type = [r for r in self.relations if r["tail_type"] == r1["tail_type"]]
                
    #     return any(self.are_relations_equal(r1, r) for r in relations_with_same_head_type) or any(self.are_relations_equal(r1, r) for r in relations_with_same_tail_type)

    # def merge_relations(self, r1):
    #     r2 = [r for r in self.relations
    #           if self.are_relations_equal(r1, r)][0]
    #     spans_to_add = [span for span in r1["meta"]["spans"]
    #                     if span not in r2["meta"]["spans"]]
    #     r2["meta"]["spans"] += spans_to_add

    def add_relation(self, r):
        # if not self.exists_relation(r):
        #     self.relations.append(r)
        # else:
        #     self.merge_relations(r)
        self.relations.append(r)

    def print(self):
        print("Relations:")
        for r in self.relations:
            print(f"  {r}")
        

def extract_relations_from_model_output(text):
    triplets = []
    relation = ''
    text = text.strip()
    current = 'x'
    subject, relation, object_, object_type, subject_type = '','','','',''

    for token in text.replace("<s>", "").replace("<pad>", "").replace("</s>", "").replace("tp_XX", "").replace("__en__", "").split():
        if token == "<triplet>" or token == "<relation>":
            current = 't'
            if relation != '':
                triplets.append({'head': subject.strip(), 'head_type': subject_type, 'type': relation.strip(),'tail': object_.strip(), 'tail_type': object_type})
                relation = ''
            subject = ''
        elif token.startswith("<") and token.endswith(">"):
            if current == 't' or current == 'o':
                current = 's'
                if relation != '':
                    triplets.append({'head': subject.strip(), 'head_type': subject_type, 'type': relation.strip(),'tail': object_.strip(), 'tail_type': object_type})
                object_ = ''
                subject_type = token[1:-1]
            else:
                current = 'o'
                object_type = token[1:-1]
                relation = ''
        else:
            if current == 't':
                subject += ' ' + token
            elif current == 's':
                object_ += ' ' + token
            elif current == 'o':
                relation += ' ' + token
    if subject != '' and relation != '' and object_ != '' and object_type != '' and subject_type != '':
        triplets.append({'head': subject.strip(), 'head_type': subject_type, 'type': relation.strip(),'tail': object_.strip(), 'tail_type': object_type})
    return triplets



# extract relations for each span and put them together in a knowledge base
def get_kb(text, span_length=128, verbose=False, kb=KB(), pdf_name=""):
    # tokenize whole text
    inputs = tokenizer([text], max_length=256, padding=True, truncation=True,  return_tensors = 'pt')

    # compute span boundaries
    num_tokens = len(inputs["input_ids"][0])
    if verbose:
        print(f"Input has {num_tokens} tokens")
    num_spans = math.ceil(num_tokens / span_length)
    if verbose:
        print(f"Input has {num_spans} spans")
    overlap = math.ceil((num_spans * span_length - num_tokens) /
                        max(num_spans - 1, 1))
    spans_boundaries = []
    start = 0
    for i in range(num_spans):
        spans_boundaries.append([start + span_length * i,
                                 start + span_length * (i + 1)])
        start -= overlap
    if verbose:
        print(f"Span boundaries are {spans_boundaries}")

    # transform input with spans
    tensor_ids = [inputs["input_ids"][0][boundary[0]:boundary[1]]
                  for boundary in spans_boundaries]
    tensor_masks = [inputs["attention_mask"][0][boundary[0]:boundary[1]]
                    for boundary in spans_boundaries]

    inputs = {
        "input_ids": torch.stack(tensor_ids).to(DEVICE),
        "attention_mask": torch.stack(tensor_masks).to(DEVICE)
    }

    # generate relations
    num_return_sequences = 3
    gen_kwargs = {
      "max_length": 256,
      "length_penalty": 0,
      "num_beams": 3,
      "num_return_sequences": num_return_sequences,
      "forced_bos_token_id": None,
    }


    generated_tokens = rdf_model.generate(
      inputs["input_ids"].to(rdf_model.device),
      attention_mask=inputs["attention_mask"].to(rdf_model.device),
      decoder_start_token_id = tokenizer.convert_tokens_to_ids("tp_XX"),
      **gen_kwargs,
    )

    del inputs, tensor_ids, tensor_masks
    torch.cuda.empty_cache()

    # decode relations
    decoded_preds = tokenizer.batch_decode(generated_tokens, skip_special_tokens=False)
    torch.cuda.empty_cache()

    i = 0
    for sentence_pred in decoded_preds:
        current_span_index = i // num_return_sequences
        relations = extract_relations_from_model_output(sentence_pred)
        # print("Sub part ", i)
        for relation in relations:
            relation["meta"] = {
                "spans": [spans_boundaries[current_span_index]]
            }
            relation["fname"] = pdf_name
            # print(relation)
            kb.add_relation(relation)
        i += 1

    return kb


# def store_kb(kb):
#     """
#     Store the knowledge base (KB) as JSON and RDF files.

#     Args:
#         kb (KnowledgeBase): The knowledge base object containing the entities and relations.

#     Returns:
#         bool: True if the KB is successfully stored, False otherwise.
#     """
#     mode = "w"
#     store_fname = "new"

#     # Your existing code to create and populate the RDF graph
#     relations = []

#     # Iterate over each relation and add it to the relations list
#     for relation in kb.relations:
#         # check if head, relation_type, and tail are URI safe
#         head = relation["head"]
#         relation_type = relation["type"]
#         tail = relation["tail"]
#         fname = relation["fname"]
#         # Add the triple to the list
#         relation_dict = {
#             "head": head,
#             "type": relation_type,
#             "tail": tail,
#             "fname" : fname
#         }
#         relations.append(relation_dict)

#     # Save the list of triples to a JSON file
#     json_filename = "../RDFs/" + store_fname + '_r.json'
#     with open(json_filename, 'w') as json_file:
#         json.dump(relations, json_file)

#     return True


def clear_num(text):
    result = []
    for word in text.split(" "):
        try :
            int_val = int(word)
            result.append(str(int_val))
        except ValueError :
            clean_word = [l for l in word if not l.isdigit()]
            if len(clean_word) > 1:
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


def date_detection_in_string(string):
    # detect if there is a date in the string whatever the format is
    return 0


def add_in_file(text, file_name):
    with open(file_name, "a") as f:
        f.write(text + "\n")

def text_compare(text1, text2):
    # compare two text and return a score between 0 and 1
    # 0 means that the two text are different
    # 1 means that the two text are the same
    # consider capital letters or not as the same
    # consider the order of words or not as the same
    
    # remove all caractere like : ',|- and replace them by space
    
    if text1 == text2 :
        return 1
    
    text1 = clear_str(text1)
    text2 = clear_str(text2)
    
    if text1 == text2 :
        return 1
    
    # split text into words
    words1 = text1.split()
    words2 = text2.split()
    
    # get the number of words in each text
    nb_words1 = len(words1)
    nb_words2 = len(words2)
    
    nb_cara1 = 0
    nb_cara2 = 0
    for word1 in words1 :
        nb_cara1 += len(word1)
    for word2 in words2 :
        nb_cara2 += len(word2)
    
    first_letters1 = ""
    first_letters2 = ""
    
    for word1 in words1 :
        if word1 != "of" and word1 != "the" and word1 != "and" :
            first_letters1 += word1[0]
    for word2 in words2 :
        if word2 != "of" and word2 != "the" and word2 != "and" :
            first_letters2 += word2[0]

    if first_letters1 == text2 :
        print("text2", text2, "is the acronym of text1", text1)
        return 1
    if first_letters2 == text1 :
        print("text1", text1, "is the acronym of text2", text2)
        return 1
        
    if first_letters1 == text2 :
        print("text2", text2, "is the acronym of text1", text1)
        add_in_file(text1 + " = " + text2, "../datasets/acronyms.txt")
        return 1
    if first_letters2 == text1 :
        print("text1", text1, "is the acronym of text2", text2)
        add_in_file(text2 + " = " + text1, "../datasets/acronyms.txt")
        return 1
    
    # if it's just the plural of the other text
    if nb_cara1 >= nb_cara2 + 1 and nb_cara1 <= nb_cara2 + nb_words2 + 1 :
        if text2 in text1 and (text1[-1] == "s" or text1[-1] == "x") and (text2[-1] != "s" and text2[-1] != "x") :
            print("text1", text1, "is the plural of text2", text2)
            add_in_file(text1 + " = " + text2, "../datasets/plurals.txt")
            return 1
    elif nb_cara2 >= nb_cara1 + 1 and nb_cara2 <= nb_cara1 + nb_words1 + 1:
        if text1 in text2 and (text2[-1] == "s" or text2[-1] == "x") and (text1[-1] != "s" and text1[-1] != "x") :
            print("text2", text2, "is the plural of text1", text1)
            add_in_file(text2 + " = " + text1, "../datasets/plurals.txt")
            return 1
    
    # get the number of words in common between the two text consider capital letters or not as the same
    nb_letters_in_common = 0
    for word1 in words1 :
        for word2 in words2 :
            for i in range(min(len(word1), len(word2))) :
                # consider é and e and è as the same
                if word1[i].lower() == word2[i].lower() or (word1[i] in "éèe" and word2[i] in "éèe"):
                    nb_letters_in_common += 1
            
    score = nb_letters_in_common / (max(len(text1), len(text2)))
    if score > 0.8 :
        print("score = ", score, "text1 = ", text1, "text2 = ", text2)
        add_in_file(text1 + " = " + text2, "../datasets/similarities.txt")
    elif score > 0.5 :
        add_in_file(text1 + " ~ " + text2, "../datasets/nearly_similarities.txt")
    ##else :
        ##add_in_file(text1 + " != " + text2, "../datasets/differences.txt")
    return score


    

def store_kb(kb):
    """
    Store the knowledge base (KB) as JSON and RDF files.

    Args:
        kb (KnowledgeBase): The knowledge base object containing the entities and relations.

    Returns:
        bool: True if the KB is successfully stored, False otherwise.
    """
    print("c    storing...")

    # Define correct URI and AUTH arguments (no AUTH by default)
    URI = "bolt://localhost:7687"
    AUTH = ("", "")
 
    with GraphDatabase.driver(URI, auth=AUTH) as client:
        # Check the connection
        client.verify_connectivity()

        history=[]
                
        for r in kb.relations :
            head = r["head"]
            head_type = r["head_type"]
            relation_type = r["type"]
            tail = r["tail"]
            tail_type = r["tail_type"]
            fname = r["fname"]
            
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
                
                with client.session() as session:
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
            
        # save the history of queries
        with open("../RDFs/_history.txt", "w") as f:
            for query in history:
                f.write(query + "\n")
        