import logging
import azure.functions as func
import json
import traceback
import cgi
from io import BytesIO
import os
import requests

# endpoint = "https://homaphising.cognitiveservices.azure.com/"
# key = os.environ['API_KEY_1']
# key_1 = os.environ['API_KEY_1']
# key_2 = os.environ['API_KEY_2']
# text_analytics_client = TextAnalyticsClient(
# endpoint=endpoint, credential=AzureKeyCredential(key))
# # endpoint=endpoint, credential=AzureKeyCredential(key_1, key_2))

# # Fraud detection model endpoint
# model_endpoint = "http://d3251e64-1a14-46c8-b197-5541ab06a38e.swedencentral.azurecontainer.io/score"


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

                        # Call your ML model here (example below)
                        result = call_ml_model(file_content, message_type)
                        
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

def call_ml_model(file_content, message_type):
    """Call the Azure ML model endpoint."""
    endpoint = "https://homaphising.cognitiveservices.azure.com/"
    # key_1 = os.environ['API_KEY_1']
    # key_2 = os.environ['API_KEY_2']
    # text_analytics_client = TextAnalyticsClient(
    # endpoint=endpoint, credential=AzureKeyCredential(key))
    # endpoint=endpoint, credential=AzureKeyCredential(key_1, key_2))

    # Fraud detection model endpoint
    model_endpoint = "http://d3251e64-1a14-46c8-b197-5541ab06a38e.swedencentral.azurecontainer.io/score"


    
    try:
        headers = {
            'Content-Type': 'application/json',
        }

        # Prepare payload for the model
        
        data = {
            "data": {
                "TEXT": file_content.decode('utf-8'),  # Assuming the content is a plain text
                "URL": False, # Set to True if the content includes a URL
                "EMAIL": message_type.lower() == 'email',  # Set to True if the message type is 'email'
                "PHONE": message_type.lower() == 'sms'   # Set to True if the message type is 'phone'
            }
        }


        response = requests.post(model_endpoint, headers=headers, json=data)
        
        if response.status_code == 200:
            return response.json()
        else:
            return {
                "error": "Failed to call ML model",
                "status_code": response.status_code,
                "details": response.text
            }

    except Exception as e:
        logging.error(f"Error calling ML model: {str(e)}")
        logging.error(traceback.format_exc())
        return {
            "error": "Internal error calling ML model",
            "details": str(e)
        }
