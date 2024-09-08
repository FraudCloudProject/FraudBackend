import logging
import azure.functions as func
import json
import traceback
from requests_toolbelt.multipart import decoder

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')
    # CORS headers
    headers = {
        "Access-Control-Allow-Origin": "https://jolly-bay-02c912b03.5.azurestaticapps.net",
        "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
        "Access-Control-Allow-Headers": "Content-Type"
    }
    
    try:
        # Log request details
        logging.info(f"Request method: {req.method}")
        logging.info(f"Request headers: {dict(req.headers)}")
        
        # Handle OPTIONS requests for CORS preflight
        if req.method == 'OPTIONS':
            return func.HttpResponse("", status_code=204, headers=headers)
        
        # Handle POST request
        if req.method == 'POST':
            # Read the request body
            body = req.get_body()
            content_type = req.headers.get('Content-Type')
            
            logging.info(f"Content-Type: {content_type}")
            logging.info(f"Body length: {len(body)}")
            
            # Parse multipart/form-data
            if content_type and 'multipart/form-data' in content_type:
                try:
                    multipart_data = decoder.MultipartDecoder(body, content_type)
                    
                    # Initialize variables to store form data
                    message_type = None
                    file_content = None
                    file_name = None

                    # Process each part of the multipart data
                    for part in multipart_data.parts:
                        content_disposition = part.headers.get(b'Content-Disposition', b'').decode('utf-8')
                        logging.info(f"Part Content-Disposition: {content_disposition}")
                        
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
                except Exception as e:
                    logging.error(f"Error parsing multipart data: {str(e)}")
                    logging.error(traceback.format_exc())
                    return func.HttpResponse(
                        json.dumps({"error": "Error parsing multipart data", "details": str(e)}),
                        status_code=400,
                        headers=headers,
                        mimetype="application/json"
                    )
            else:
                logging.warning(f"Unsupported Content-Type: {content_type}")
                return func.HttpResponse(
                    json.dumps({"error": "Unsupported Content-Type"}),
                    status_code=415,
                    headers=headers,
                    mimetype="application/json"
                )
        else:
            logging.warning(f"Unsupported HTTP method: {req.method}")
            return func.HttpResponse(
                json.dumps({"error": "Method not allowed"}),
                status_code=405,
                headers=headers,
                mimetype="application/json"
            )
    except Exception as e:
        logging.error(f"Unexpected error: {str(e)}")
        logging.error(traceback.format_exc())
        return func.HttpResponse(
            json.dumps({
                "error": "Internal server error",
                "details": str(e),
                "type": str(type(e)),
                "traceback": traceback.format_exc()
            }),
            status_code=500,
            headers=headers,
            mimetype="application/json"
        )