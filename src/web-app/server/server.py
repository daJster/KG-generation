from flask import Flask, render_template, url_for, request, jsonify, send_file
from utils import CommandStorage
import os
import uuid
import time
from datetime import datetime


HOST = "localhost"
PORT = 5000
TEMPLATE_DIR = os.path.abspath("../client/")
STATIC_DIR = os.path.abspath(TEMPLATE_DIR+"/static/")
GRAPH_DIR = os.path.abspath("../../../graphs/")
print(f"Host: {HOST} : {PORT}")
print(f"Template dir: {TEMPLATE_DIR}")
print(f"Static dir: {STATIC_DIR}")

app = Flask(__name__, template_folder=TEMPLATE_DIR, static_folder=STATIC_DIR)


@app.route('/')
def render_index() :
    return render_template('index.html')

@app.route('/search')
def search():
    query = request.args.get('query')
    results = f"Search results for '{query}'"
    return jsonify({'results': results})

@app.route('/list_graphs')
def list_graphs():
    file_names_without_extension = []

    for filename in os.listdir(f"{GRAPH_DIR}/"):
        if os.path.isfile(os.path.join(f"{GRAPH_DIR}/", filename)):
            name, extension = os.path.splitext(filename)
            file_names_without_extension.append(name)

    return jsonify({'graph_files': file_names_without_extension})

@app.route('/get_graph_file/<graph_file>')
def load_html(graph_file):
    # Replace this path with the actual path to your HTML files
    html_path = f'{GRAPH_DIR}/{graph_file}.html'
    return send_file(html_path, mimetype='text/html')


@app.route('/send_command')
def send_command():
    command = request.args.get('command', '')
    command_name = request.args.get('command_name', '')
    dt_string = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    output = ''
    data_dict = {
        'id' : uuid.uuid4(),
        'command_name' : command_name,
        'command': command,
        'output': output,
        'status': '',
        'time_of_execution': dt_string,
        'duration': ''
    }

    pass
    start = time.time()
    try:
        # Send data to the server
        pass

        # Recv data from the server
        data = None
        end = time.time()
        status = 'success'
        output = str(data)
        if '-1' in output : 
            status = 'fail'
        
    except None:
        end = time.time()
        status = 'fail'
        output = 'Timeout error occurred.'
    
    except None:
        pass
        end = time.time()
        status = 'fail'
        ouput = 'Broken connection.'

    duration = str(round(end - start, 6)) + ' seconds'
    data_dict['status'] = status
    data_dict['output'] = output
    data_dict['duration'] =  duration
    pass
    return data_dict


@app.route('/get_data', methods=['GET'])
def get_data():
    data = None
    return data
    
@app.route('/test_send_recv_route', methods=['GET'])
def test_send_recv() :
    return {
        "title" : "send recv test", 
        "status" : "success"    
        }
    

if __name__ == "__main__":
    app.run(debug=True)
