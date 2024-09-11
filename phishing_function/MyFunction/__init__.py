import re
import logging
import azure.functions as func
import json
import traceback
import cgi
from io import BytesIO
import os
import requests
from azure.ai.formrecognizer import FormRecognizerClient
from azure.core.credentials import AzureKeyCredential



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
                        form = cgi.FieldStorage(
                            fp=body_stream, environ=env, headers=req.headers)

                        message_type = form.getvalue('type')
                        file_item = form['file']

                        if file_item.filename:
                            file_content = file_item.file.read()
                            file_name = file_item.filename
                            logging.info(f"Received file: {file_name}")

                            # Check if the file is a PDF
                            if file_name.endswith('.pdf'):
                                file_content = extract_text_from_pdf(file_content)
                                logging.info(f"Converted PDF to text. Length: {len(file_content)}")

                            # Process the file content (whether plain text or converted PDF)
                            result = call_ml_model(file_content, message_type)
                            response_data = {
                                "result": result,
                            }
                            return func.HttpResponse(json.dumps(response_data), status_code=200, headers=headers, mimetype="application/json")
                        else:
                            logging.error("No file content received")
                            return func.HttpResponse(
                                json.dumps({"error": "No file content received"}),
                                status_code=400,
                                headers=headers,
                                mimetype="application/json"
                            )
                    except Exception as e:
                        logging.error(f"Error parsing multipart data: {str(e)}")
                        logging.error(traceback.format_exc())
                        return func.HttpResponse(
                            json.dumps(
                                {"error": "Error parsing multipart data", "details": str(e)}),
                            status_code=400,
                            headers=headers,
                            mimetype="application/json"
                        )
                else:
                    logging.warning(f"Unsupported Content-Type: {content_type}")
                    return func.HttpResponse(
                        json.dumps(
                            {"error": "Unsupported Content-Type", "received": content_type}),
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
    """Call the Azure ML model endpoint and check for URLs."""
    model_endpoint = "http://d3251e64-1a14-46c8-b197-5541ab06a38e.swedencentral.azurecontainer.io/score"

    try:
        # Convert the file content to a string
        content_str = file_content.decode('utf-8')
        
        # Define the regex pattern for URLs
        url_pattern = r'(https?://[^\s]+)'
        
        # Find all URLs in the content
        urls = re.findall(url_pattern, content_str)
        
        # If URLs were found, set the `url` flag to True
        url_detected = len(urls) > 0

        # Prepare payload for the model
        data = {
            "Inputs": {
                "data": [
                    {
                        "TEXT": content_str,  # Send the full text content
                        "URL": url_detected,  # Set to True if URLs were detected
                        "EMAIL": message_type.lower() == 'email',  # True if message type is 'email'
                        "PHONE": message_type.lower() == 'sms'  # True if message type is 'sms'
                    }
                ]
            }
        }

        headers = {
            'Content-Type': 'application/json',
        }

        # Make the API request to the model
        response = requests.post(model_endpoint, headers=headers, json=data)

        if response.status_code == 200:
            model_result = response.json()
            return {
                "ml_result": model_result,
                "url_detected": url_detected,
                "urls": urls  # Return the list of URLs found
            }
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

def extract_text_from_pdf(pdf_path):
    endpoint = os.environ["https://pdfconverterpihising.cognitiveservices.azure.com/"]
    api_key = os.environ["PDF_API_KEY"]
    form_recognizer_client = FormRecognizerClient(endpoint=endpoint, credential=AzureKeyCredential(api_key))
    with open(pdf_path, "rb") as pdf_file:
        poller = form_recognizer_client.begin_read_in_stream(pdf_file, form_type="preprinted", pages="1-")
        result = poller.result()

        text = ""
        for page_result in result.analyze_result.read_results:
            for line in page_result.lines:
                text += line.text + "\n"

    return text