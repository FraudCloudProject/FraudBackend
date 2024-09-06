import logging
import azure.functions as func
from io import BytesIO
from werkzeug.utils import secure_filename
import json

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Processing a file upload request.')

    # Check if the request contains files
    if 'file' not in req.files:
        return func.HttpResponse(
            "No file part",
            status_code=400
        )
    
    file = req.files['file']
    if file.filename == '':
        return func.HttpResponse(
            "No selected file",
            status_code=400
        )
    
    # Process the file
    filename = secure_filename(file.filename)
    file_content = file.read()

    # Here you would handle the file content
    # For demonstration purposes, we return a success message
    return func.HttpResponse(
        json.dumps({"message": "File received", "filename": filename}),
        mimetype="application/json"
    )
