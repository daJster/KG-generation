import math
import torch
import wikipedia
from rdflib import Graph, URIRef, Literal, Namespace, RDF, RDFS
import uuid
import json
from merge_RDF import similarity_score
from params import tokenizer, rdf_model, PATH_TO_RDF_FILES, ACTIVATE_SIMILARITY

class KB():
    def __init__(self):
        self.entities = {}
        self.relations = []
        self.group_name = ""

    def get_wikipedia_data(self, candidate_entity):
        try:
            page = wikipedia.page(candidate_entity, auto_suggest=False)
            entity_data = {
                "title": page.title,
                "url": page.url,
                "summary": page.summary
            }
            return entity_data
        except:
            return None

    def add_entity(self, e):
        self.entities[e["title"]] = {k:v for k,v in e.items() if k != "title"}

    def are_relations_equal(self, r1, r2, similarity_threshold=0.8):
        sim_score = similarity_score(r1, r2)
        is_equal = all(r1[attr] == r2[attr] for attr in ["head", "type", "tail"]) 
        if ACTIVATE_SIMILARITY :
            is_equal = is_equal or sim_score > similarity_threshold
        return is_equal

    def exists_relation(self, r1):
        return any(self.are_relations_equal(r1, r2) for r2 in self.relations)

    def add_relation(self, r):
        candidate_entities = [r["head"], r["tail"]]
        entities = [self.get_wikipedia_data(ent) for ent in candidate_entities]

        if any(ent is None for ent in entities):
            return

        for e in entities:
            self.add_entity(e)

        r["head"] = entities[0]["title"]
        r["tail"] = entities[1]["title"]

        if not self.exists_relation(r):
            self.relations.append(r)
        else:
            self.merge_relations(r)


    def print(self):
        print("Entities:")
        for e in self.entities.items():
            print(f"  {e[0]}")
        print("Relations:")
        for r in self.relations:
            print(f"  {r}")

    def merge_relations(self, r1):
        r2 = [r for r in self.relations
              if self.are_relations_equal(r1, r)][0]
        spans_to_add = [span for span in r1["meta"]["spans"]
                        if span not in r2["meta"]["spans"]]
        r2["meta"]["spans"] += spans_to_add
        
        

def extract_relations_from_model_output(text):
    relations = []
    relation, subject, relation, object_ = '', '', '', ''
    text = text.strip()
    current = 'x'
    text_replaced = text.replace("<s>", "").replace("<pad>", "").replace("</s>", "")
    for token in text_replaced.split():
        if token == "<triplet>":
            current = 't'
            if relation != '':
                relations.append({
                    'head': subject.strip(),
                    'type': relation.strip(),
                    'tail': object_.strip()
                })
                relation = ''
            subject = ''
        elif token == "<subj>":
            current = 's'
            if relation != '':
                relations.append({
                    'head': subject.strip(),
                    'type': relation.strip(),
                    'tail': object_.strip()
                })
            object_ = ''
        elif token == "<obj>":
            current = 'o'
            relation = ''
        else:
            if current == 't':
                subject += ' ' + token
            elif current == 's':
                object_ += ' ' + token
            elif current == 'o':
                relation += ' ' + token
    if subject != '' and relation != '' and object_ != '':
        relations.append({
            'head': subject.strip(),
            'type': relation.strip(),
            'tail': object_.strip()
        })
    return relations


        
def from_small_text_to_kb(text, verbose=False):
    kb = KB()

    model_inputs = tokenizer(text, max_length=512, padding=True, truncation=True,
                            return_tensors='pt')
    if verbose:
        print(f"Num tokens: {len(model_inputs['input_ids'][0])}")

    gen_kwargs = {
        "max_length": 216,
        "length_penalty": 0,
        "num_beams": 3,
        "num_return_sequences": 3
    }
    generated_tokens = rdf_model.generate(
        **model_inputs,
        **gen_kwargs,
    )
    decoded_preds = tokenizer.batch_decode(generated_tokens, skip_special_tokens=False)

    for sentence_pred in decoded_preds:
        relations = extract_relations_from_model_output(sentence_pred)
        for r in relations:
            kb.add_relation(r)

    return kb


        
def get_kb(text, span_length=128, verbose=False, kb=KB(), group_name="test", is_new_group=True):
    inputs = tokenizer([text], return_tensors="pt")

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

    tensor_ids = [inputs["input_ids"][0][boundary[0]:boundary[1]]
                  for boundary in spans_boundaries]
    tensor_masks = [inputs["attention_mask"][0][boundary[0]:boundary[1]]
                    for boundary in spans_boundaries]
    inputs = {
        "input_ids": torch.stack(tensor_ids),
        "attention_mask": torch.stack(tensor_masks)
    }

    num_return_sequences = 3
    gen_kwargs = {
        "max_length": 256,
        "length_penalty": 0,
        "num_beams": 3,
        "num_return_sequences": num_return_sequences
    }
    generated_tokens = rdf_model.generate(
        **inputs,
        **gen_kwargs,
    )

    decoded_preds = tokenizer.batch_decode(generated_tokens,
                                           skip_special_tokens=False)


    i = 0
    for sentence_pred in decoded_preds:
        current_span_index = i // num_return_sequences
        relations = extract_relations_from_model_output(sentence_pred)
        for relation in relations:
            relation["meta"] = {
                "spans": [spans_boundaries[current_span_index]]
            }
            kb.add_relation(relation)
        i += 1
        
    kb.group_name = group_name
    if ACTIVATE_SIMILARITY :
        kb.group_name += "_sim"
    kb.is_new_group = is_new_group
    return kb



def store_kb(kb) :
    print("storing...")
    mode="w"
    if kb.is_new_group :
        mode = "w"
    # Save the 'entities' dictionary as a JSON file
    with open(PATH_TO_RDF_FILES+kb.group_name+'.json', mode) as json_file:
        json.dump(kb.entities, json_file, indent=4)
        
    g = Graph()

    # Define a custom namespace
    custom_namespace = Namespace("http://example.org/")

    # Iterate over each relation and add it to the RDF graph
    for relation in kb.relations:
        head = URIRef(custom_namespace[relation["head"].replace(" ", "_")])
        relation_type = URIRef(custom_namespace[relation["type"].replace(" ", "_")])
        tail = URIRef(custom_namespace[relation["tail"].replace(" ", "_")])

        g.add((head, relation_type, tail))

    # Serialize the RDF graph to Turtle format and save it to a file
    g.serialize(destination=PATH_TO_RDF_FILES+kb.group_name+'.ttl', format="turtle", mode=mode)

    return True