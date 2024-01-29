from text_selection import get_text
from KB_generation import get_kb, store_kb, KB
import time
import streamlit as st #  export PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION=python
from codecarbon import EmissionsTracker, track_emissions

@track_emissions(
    measure_power_secs=30,
    api_call_interval=4,
    experiment_id="KGGen",
    save_to_api=True,
)
def main() :
    """
    Main function for Knowledge Graph Generation.
    
    This function allows the user to upload a directory containing PDF files,
    extract text from the files, and generate a knowledge graph based on the extracted text.
    The generated graph is then stored and the execution time is displayed.
    """
    tracker = EmissionsTracker(api_key="835030e3-24cb-4cc6-bfdd-ac8201fb3a31", save_to_file=True, output_file="emissions.csv")
    tracker.start()
    batch_size_save = 10
    st.title("Knowledge Graph Generation")
    files = st.file_uploader("Upload a directory contaning PDF files", accept_multiple_files=True, type="pdf")
    # files = get_files(path=upload_path)
    if files != [] : 
        with st.status("Generating graph...", expanded=True) as status:
            start_time = time.time()
            model_time = 0
            merge_time = 0
            model_time = 0
            kb = KB()
            for idx, file in enumerate(files):
                st.write("Generating graph for : ", file.name)
                pourcentage_progress_bar = st.progress(0)
                text = get_text(file)
                batch_size = 15000
                for i in range(0, len(text), batch_size):
                    if i+batch_size > len(text) :
                        text_part = text[i:]
                    else :
                        text_part = text[i:i+batch_size]
                    kb, partial_model_time = get_kb(text_part, verbose=False, kb=kb, pdf_name=file.name)
                    if i % batch_size_save == 0 :
                        is_stored, partial_merge_time = store_kb(kb)
                        # reset kb
                        kb = KB()
                    pourcentage_progress_bar.progress(int(i/len(text)*100))
                    model_time += partial_model_time
                    merge_time += partial_merge_time
                        
                is_stored, partial_merge_time = store_kb(kb)
                merge_time += partial_merge_time
                
                end_time = time.time()
                execution_time = end_time - start_time
                print(f"c    ################# Generation Time : {model_time:.4f} seconds #################")
                print(f"c    ################# Merge Time : {merge_time:.4f} seconds #################")
                print(f"c    ################# Total Time : {execution_time:.4f} seconds #################")
                print(f"c    #################  {idx} #################")
                pourcentage_progress_bar.progress(int(100))
                st.write(f"Total Time for {file.name}: {execution_time:.4f} seconds.")
                st.write(f"Model Time for {file.name}: {model_time:.4f} seconds.")
                st.write(f"Merge Time for {file.name}: {merge_time:.4f} seconds.")      
            st.success(f"graph generated.")
            tracker.stop()
    

if __name__ == "__main__" :
    main()
    
    
