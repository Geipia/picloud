from flask import Flask, request, redirect, url_for, send_from_directory, render_template_string, Response
from flask_httpauth import HTTPBasicAuth
import os
import shutil
import zipfile
from io import BytesIO

app = Flask(__name__)
auth = HTTPBasicAuth()

UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# User credentials for basic authentication
users = {
    "admin": "tata",
}

@auth.get_password
def get_pw(username):
    if username in users:
        return users.get(username)
    return None

@app.route('/')
@auth.login_required
def index():
    files = os.listdir(UPLOAD_FOLDER)
    return render_template_string('''
        <h1>Cloud Storage</h1>
        <form method="post" action="/upload" enctype="multipart/form-data">
            <input type="file" name="files" multiple webkitdirectory mozdirectory msdirectory odirectory directory>
            <input type="submit" value="Upload">
        </form>
        <h2>Files</h2>
        <ul>
            {% for file in files %}
            <li><a href="/download/{{ file }}">{{ file }}</a></li>
            {% endfor %}
        </ul>
    ''', files=files)

@app.route('/upload', methods=['POST'])
@auth.login_required
def upload_file():
    if 'files' not in request.files:
        return redirect(url_for('index'))
    
    files = request.files.getlist('files')
    
    for file in files:
        if file.filename == '':
            continue
        
        file_path = os.path.join(UPLOAD_FOLDER, file.filename)
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        file.save(file_path)
    
    return redirect(url_for('index'))

@app.route('/download/<filename>')
@auth.login_required
def download_file(filename):
    file_path = os.path.join(UPLOAD_FOLDER, filename)
    if os.path.isdir(file_path):
        # Create a temporary directory to store the compressed file
        temp_dir = '/tmp'
        temp_zip_path = os.path.join(temp_dir, filename + '.zip')

        # Compress the folder into a ZIP file
        with zipfile.ZipFile(temp_zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(file_path):
                for file in files:
                    file_abs_path = os.path.join(root, file)
                    rel_path = os.path.relpath(file_abs_path, file_path)
                    zipf.write(file_abs_path, arcname=rel_path)

        # Serve the ZIP file for download
        with open(temp_zip_path, 'rb') as f:
            zip_data = f.read()
        os.remove(temp_zip_path)
        return Response(zip_data, mimetype='application/zip', headers={
            'Content-Disposition': f'attachment; filename="{filename}.zip"'
        })
    else:
        # Serve the file for download
        return send_from_directory(UPLOAD_FOLDER, filename, as_attachment=True)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
