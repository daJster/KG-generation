from data_selection import get_files
from text_selection import get_text
from KB_generation import get_kb, store_kb, KB
from graph_generation import get_graph, get_graph2
import time
import streamlit as st #  export PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION=python

def main() :
    """
    Main function for Knowledge Graph Generation.
    
    This function allows the user to upload a directory containing PDF files,
    extract text from the files, and generate a knowledge graph based on the extracted text.
    The generated graph is then stored and the execution time is displayed.
    """
    batch_size_save = 10
    st.title("Knowledge Graph Generation")
    files = st.file_uploader("Upload a directory contaning PDF files", accept_multiple_files=True, type="pdf")
    # files = get_files(path=upload_path)
    if files != [] : 
        with st.status("Generating graph...", expanded=True) as status:
            start_time = time.time()
            kb = KB()
            for file in files :
                st.write("Generating graph for : ", file.name)
                pourcentage_progress_bar = st.progress(0)
                text = get_text(file)
                for i in range(0, len(text), 1000):
                    text_part = text[i:i+1000]
                    kb = get_kb(text_part, verbose=False, kb=kb, pdf_name=file.name)
                    if i % batch_size_save == 0 :
                        is_stored = store_kb(kb)
                        # reset kb
                        kb = KB()
                    pourcentage_progress_bar.progress(int(i/len(text)*100))
                    
                        
                is_stored = store_kb(kb)
                end_time = time.time()
                execution_time = end_time - start_time
                pourcentage_progress_bar.progress(int(100))
                st.write(f"Execution Time for {file.name}: {execution_time:.4f} seconds")         
            st.success(f"graph generated.")
    

if __name__ == "__main__" :
    main()
    
    
