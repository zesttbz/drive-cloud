from flask import Flask, request, jsonify, send_file, redirect, render_template
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload, MediaIoBaseDownload
import io
import os

app = Flask(__name__)

# Cấu hình Google Drive API
SCOPES = ['https://www.googleapis.com/auth/drive']
SERVICE_ACCOUNT_FILE = 'credentials.json'  # OAuth 2.0 Service Account file

credentials = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=SCOPES)
drive_service = build('drive', 'v3', credentials=credentials)

# Folder Drive ID nếu bạn muốn upload vào 1 folder cụ thể (có thể để trống)
PARENT_FOLDER_ID = None


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/upload', methods=['POST'])
def upload_file():
    file = request.files['file']
    if not file:
        return jsonify({'success': False, 'error': 'No file'}), 400

    file_metadata = {'name': file.filename}
    if PARENT_FOLDER_ID:
        file_metadata['parents'] = [PARENT_FOLDER_ID]

    media = MediaIoBaseUpload(file.stream, mimetype=file.mimetype)
    uploaded_file = drive_service.files().create(
        body=file_metadata,
        media_body=media,
        fields='id'
    ).execute()

    return jsonify({'success': True, 'file_id': uploaded_file.get('id')})


@app.route('/files', methods=['GET'])
def list_files():
    results = drive_service.files().list(
        pageSize=20,
        fields="files(id, name)"
    ).execute()
    items = results.get('files', [])
    return jsonify(items)


@app.route('/download/<file_id>', methods=['GET'])
def download_file(file_id):
    request_file = drive_service.files().get_media(fileId=file_id)
    fh = io.BytesIO()
    downloader = MediaIoBaseDownload(fh, request_file)
    done = False
    while done is False:
        status, done = downloader.next_chunk()

    fh.seek(0)
    file_info = drive_service.files().get(fileId=file_id, fields='name').execute()
    return send_file(fh, as_attachment=True, download_name=file_info['name'])


@app.route('/delete/<file_id>', methods=['GET'])
def delete_file(file_id):
    try:
        drive_service.files().delete(fileId=file_id).execute()
        return redirect('/')
    except Exception as e:
        return str(e), 500


if __name__ == '__main__':
    app.run(debug=True)
