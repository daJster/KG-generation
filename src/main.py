from data_selection import get_files
from text_selection import get_text
from KB_generation import get_kb, store_kb, KB
from graph_generation import get_graph, get_graph2
import time

def main() :
    files = get_files()
    kb = KB()
    for file in files :
        text = get_text(file)
        print(f"Text extracted from {file}.")
        for i in range(0, len(text), 3500):
            text_part = text[i:i+3500]
            print("Extracting relations from text part : ",i)
            kb = get_kb(text_part, group_name="100m", is_new_group=False, verbose=True, kb=kb)
            print(f"Relations extracted from text part {i}.")
        is_stored = store_kb(kb)
    # graph = get_graph(kb)
    #graph2 = get_graph2("neuron")
    print(f"graph generated.")
    

if __name__ == "__main__" :
    start_time = time.time()
    main()
    end_time = time.time()
    execution_time = end_time - start_time
    print(f"Execution Time: {execution_time:.4f} seconds")
