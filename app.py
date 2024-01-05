
from flask import Flask, render_template, jsonify, request, flash

from werkzeug.utils import secure_filename

from flask_socketio import SocketIO

import os
from os import listdir
from os.path import isfile, join
import json
from threading import Thread

import time

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

# Configuration
UPLOAD_FOLDER = 'users_files/'
ALLOWED_EXTENSIONS = {'pdf', 'docx'}
MAX_FILE_SIZE_MB = 20  # Maximum file size in Megabytes
MAX_FILE_SIZE = MAX_FILE_SIZE_MB * 1024 * 1024  # Convert to bytes
FOLDER ='./new_fiches' 

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_FILE_SIZE
def lister_cours():
    files = [f for f in listdir(FOLDER) if isfile(join(FOLDER, f)) and f.endswith('.json')]
    return files

def background_processing(filename, sid):
    # Simulate a long-running task with sleep
    for i in range(1, 11):
        time.sleep(1)  # simulate work being done
        progress = i * 10
        # Use the SocketIO instance to emit a message to the client
        socketio.emit('processing_update', {'progress': progress}, to=sid)
    # End of processing

@app.route('/', methods=['GET', 'POST'])
def index():
    available_cours = lister_cours()
    return render_template('index_new.html', available_cours=available_cours)

@app.route('/fiches/<filename>')
def fiche(filename):
    # Set the path to the folder containing the files you want to view
    files_folder = FOLDER
    file_path = join(files_folder, filename)
    if os.path.exists(file_path) and os.path.isfile(file_path):
        with open(file_path, 'r', encoding='utf-8') as fichier:
            contenu = json.load(fichier)
        return render_template('view_fiche.html', contenu=contenu)
    else:
        return "File not found", 404


@app.route('/upload')
def upload():
    return render_template('upload.html')

@app.route('/process_file', methods=['POST'])
def process_file():
    file = request.files.get('file')
    if not file:
        return 'No file part', 400

    if file.filename == '':
        return 'No selected file', 400

    if not allowed_file(file.filename):
        return 'Invalid file type', 400

    try:
        filename = secure_filename(file.filename)
      
        # Here you can add additional file size validation if needed
        # Actual file size validation can be handled by the MAX_CONTENT_LENGTH
        #file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        
        sid = request.form.get('sid')  # Session ID for SocketIO

        # Start the processing in a background thread
        thread = Thread(target=background_processing, args=(filename, sid))
        thread.start()

        return jsonify({'message': 'File upload started.'}), 202

        return 'File successfully uploaded', 200

    except Exception as e:
        return str(e), 500

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


if __name__ == '__main__':
    socketio.run(app, debug=True)