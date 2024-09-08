import logging
import azure.functions as func
import json
import traceback
from requests_toolbelt.multipart import decoder

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')
    
    headers = {
        "Access-Control-Allow-Origin": "https://jolly-bay-02c912b03.5.azurestaticapps.net",
        "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
        "Access-Control-Allow-Headers": "Content-Type"
    }
    
    try:
        logging.info(f"Request method: {req.method}")
        logging.info(f"Request headers: {dict(req.headers)}")
        
        if req.method == 'OPTIONS':
            return func.HttpResponse("", status_code=204, headers=headers)
        
        if req.method == 'POST':
            body = req.get_body()
            content_type = req.headers.get('Content-Type', '')
            
            logging.info(f"Content-Type: {content_type}")
            logging.info(f"Body length: {len(body)}")
            
            if 'multipart/form-data' in content_type:
                try:
                    multipart_data = decoder.MultipartDecoder(body, content_type)
                    
                    message_type = None
                    file_content = None
                    file_name = None

                    for part in multipart_data.parts:
                        part_headers = {k.decode('utf-8').lower(): v.decode('utf-8') for k, v in part.headers.items()}
                        content_disposition = part_headers.get('content-disposition', '')
                        logging.info(f"Part headers: {part_headers}")
                        
                        if 'name="type"' in content_disposition:
                            message_type = part.content.decode('utf-8').strip()
                        elif 'name="file"' in content_disposition:
                            file_content = part.content
                            file_name = content_disposition.split('filename=')[1].strip('"') if 'filename=' in content_disposition else 'unnamed_file'

                    logging.info(f"Received message type: {message_type}")
                    logging.info(f"Received file: {file_name}")
                    logging.info(f"File content length: {len(file_content) if file_content else 0}")

                    result = {
                        "message": "Data received successfully",
                        "type": message_type,
                        "fileName": file_name
                    }
                    return func.HttpResponse(json.dumps(result), status_code=200, headers=headers, mimetype="application/json")
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