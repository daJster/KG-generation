from data_selection import get_files
from text_selection import get_text
from KB_generation import get_kb, store_kb
from graph_generation import get_graph, get_graph2
import time

def main() :
    files = get_files()
    text = get_text(files) 
    # stop text at 800 tokens for benchmarking
    kb = get_kb(text[:3500], group_name="neuron", is_new_group=True, verbose=True)
    #is_stored = store_kb(kb)
    graph = get_graph(kb)
    #graph2 = get_graph2("neuron")
    print(f"graph generated as html file.")
    

if __name__ == "__main__" :
    start_time = time.time()
    main()
    end_time = time.time()
    execution_time = end_time - start_time
    print(f"Execution Time: {execution_time:.4f} seconds")
