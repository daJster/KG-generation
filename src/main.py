from data_selection import get_files
from text_selection import get_text
from KB_generation import get_kb, store_kb, KB
from graph_generation import get_graph, get_graph2
import time
import streamlit as st

def main() :
    """
    Main function for Knowledge Graph Generation.
    
    This function allows the user to upload a directory containing PDF files,
    extract text from the files, and generate a knowledge graph based on the extracted text.
    The generated graph is then stored and the execution time is displayed.
    """
    start_time = time.time()
    st.title("Knowledge Graph Generation")
    files = st.file_uploader("Upload a directory contaning PDF files", accept_multiple_files=True, type="pdf")
    # files = get_files(path=upload_path)
    if files != [] : 
        kb = KB() #! TODO 
        st.spinner("Generating Graph...")
        for file in files :
            st.write("file :", file.name)
            text = get_text(file)
            st.write(f"Text extracted from {file.name}.")
            for i in range(0, len(text), 1000):
                text_part = text[i:i+1000]
                st.write(f"Extracting relations from text part : {i}")
                kb = get_kb(text_part, group_name="100m", is_new_group=False, verbose=True, kb=kb)
                st.write(f"Relations extracted from text part : {i}")
                
            is_stored = store_kb(kb)
        # graph = get_graph(kb)
        #graph2 = get_graph2("neuron")
        end_time = time.time()
        execution_time = end_time - start_time
        st.success(f"graph generated.")
        st.write(f"Execution Time: {execution_time:.4f} seconds")
    

if __name__ == "__main__" :
    main()
    
    
