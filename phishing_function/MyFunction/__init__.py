import logging
import azure.functions as func
import json
from requests_toolbelt.multipart import decoder

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
            body = req.get_body()
            content_type = req.headers.get('Content-Type')
           
            # Parse multipart/form-data
            if content_type and 'multipart/form-data' in content_type:
                multipart_data = decoder.MultipartDecoder(body, content_type)
                
                # Initialize variables to store form data
                message_type = None
                file_content = None
                file_name = None

                # Process each part of the multipart data
                for part in multipart_data.parts:
                    content_disposition = part.headers.get(b'Content-Disposition', b'').decode('utf-8')
                    if 'name="type"' in content_disposition:
                        message_type = part.content.decode('utf-8').strip()
                    elif 'name="file"' in content_disposition:
                        file_content = part.content.decode('utf-8').strip()
                        file_name = content_disposition.split('filename=')[1].strip('"') if 'filename=' in content_disposition else 'unnamed_file'

                # Log received data
                logging.info(f"Received message type: {message_type}")
                logging.info(f"Received file: {file_name}")
                logging.info(f"File content: {file_content}")

                # Your processing logic here
                result = {
                    "message": "Data received successfully",
                    "type": message_type,
                    "fileName": file_name
                }
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
        except Exception as e:
            logging.error(f"Unexpected error: {str(e)}")
            return func.HttpResponse(
                json.dumps({"error": "Internal server error", "details": str(e), "type": str(type(e))}),
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