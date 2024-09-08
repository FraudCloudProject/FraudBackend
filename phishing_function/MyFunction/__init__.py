import logging
import azure.functions as func
import json
from requests_toolbelt.multipart import decoder
from io import BytesIO

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    # CORS headers
    headers = {
        "Access-Control-Allow-Origin": "https://jolly-bay-02c912b03.5.azurestaticapps.net",
        "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
        "Access-Control-Allow-Headers": "Content-Type"
    }

    # Handle OPTIONS requests for CORS preflight
    if req.method == 'OPTIONS':
        return func.HttpResponse("", status_code=204, headers=headers)

    # Handle POST request
    if req.method == 'POST':
        try:
            # Read the request body
            body = req.get_body().decode('utf-8')
            content_type = req.headers.get('Content-Type')
            
            # Parse multipart/form-data
            if content_type and 'multipart/form-data' in content_type:
                multipart_data = decoder.MultipartDecoder(body, content_type)
                fields = {part.headers[b'Content-Disposition'].decode('utf-8').split(';')[1].split('=')[1].strip('"'): part for part in multipart_data.parts}

                # Extract file and text data
                file_part = fields.get('file')
                if file_part:
                    file_content = file_part.content.decode('utf-8')  # Change decoding based on your file type
                    file_name = file_part.headers[b'Content-Disposition'].decode('utf-8').split(';')[2].split('=')[1].strip('"')
                    logging.info(f"Received file: {file_name}")
                    logging.info(f"File content: {file_content}")

                # Extract text data
                text_part = fields.get('text')
                if text_part:
                    text_content = text_part.content.decode('utf-8')
                    logging.info(f"Received text: {text_content}")

                # Your processing logic here
                result = {"message": "Data received successfully"}

                return func.HttpResponse(
                    json.dumps(result),
                    status_code=200,
                    headers=headers,
                    mimetype="application/json"
                )
            else:
                return func.HttpResponse(
                    json.dumps({"error": "Unsupported Content-Type"}),
                    status_code=415,
                    headers=headers,
                    mimetype="application/json"
                )
        except ValueError as ve:
            logging.error(f"ValueError: {str(ve)}")
            return func.HttpResponse(
                json.dumps({"error": "Invalid JSON input"}),
                status_code=400,
                headers=headers,
                mimetype="application/json"
            )
        except Exception as e:
            logging.error(f"Unexpected error: {str(e)}")
            return func.HttpResponse(
                json.dumps({"error": "Internal server error", "details": str(e)}),
                status_code=500,
                headers=headers,
                mimetype="application/json"
            )

    # If the method is not supported, return a 405 Method Not Allowed response
    return func.HttpResponse(
        json.dumps({"error": "Method not allowed"}),
        status_code=405,
        headers=headers,
        mimetype="application/json"
    )
