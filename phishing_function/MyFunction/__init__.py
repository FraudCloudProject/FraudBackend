import logging
import azure.functions as func
import json
import traceback
import cgi
from io import BytesIO

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

        # Handle CORS preflight request
        if req.method == 'OPTIONS':
            return func.HttpResponse("", status_code=204, headers=headers)

        # Only allow POST requests
        if req.method == 'POST':
            try:
                body = req.get_body()
                content_type = req.headers.get('Content-Type', '')

                logging.info(f"Content-Type: {content_type}")
                logging.info(f"Body length: {len(body)}")

                # Handle multipart/form-data
                if 'multipart/form-data' in content_type:
                    try:
                        # Create a fake file-like object for parsing
                        body_stream = BytesIO(body)

                        # Parse multipart form data
                        env = {'REQUEST_METHOD': 'POST'}
                        form = cgi.FieldStorage(fp=body_stream, environ=env, headers=req.headers)

                        message_type = form.getvalue('type')
                        file_item = form['file']

                        if file_item.filename:
                            file_content = file_item.file.read()
                            file_name = file_item.filename
                        else:
                            logging.error("No file content received")
                            return func.HttpResponse(
                                json.dumps({"error": "No file content received"}),
                                status_code=400,
                                headers=headers,
                                mimetype="application/json"
                            )

                        logging.info(f"Received message type: {message_type}")
                        logging.info(f"Received file: {file_name}")
                        logging.info(f"File content length: {len(file_content)}")

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
                        json.dumps({"error": "Unsupported Content-Type", "received": content_type}),
                        status_code=415,
                        headers=headers,
                        mimetype="application/json"
                    )
            except Exception as e:
                logging.error(f"Unexpected error in POST processing: {str(e)}")
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
