import logging
import azure.functions as func
from azure.storage.blob import BlobServiceClient
from azure.ai.textanalytics import TextAnalyticsClient
from azure.core.credentials import AzureKeyCredential
import requests
import json
import os

# Set up Azure Cognitive Services client
endpoint = "https://homaphising.cognitiveservices.azure.com/"
key_1 = os.environ['API_KEY_1']
key_2 = os.environ['API_KEY_2']
text_analytics_client = TextAnalyticsClient(
    endpoint=endpoint, credential=AzureKeyCredential(key_1, key_2))

# Fraud detection model endpoint
model_endpoint = "http://d3251e64-1a14-46c8-b197-5541ab06a38e.swedencentral.azurecontainer.io/score"

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Processing a request.')

    # Handle OPTIONS requests for CORS preflight
    if req.method == 'OPTIONS':
        # Provide CORS headers
        headers = {
            "Access-Control-Allow-Origin": "https://jolly-bay-02c912b03.5.azurestaticapps.net",
            "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
            "Access-Control-Allow-Headers": "Content-Type"
        }
        return func.HttpResponse(
            "", status_code=204, headers=headers
        )

    # Handle POST request (or other methods)
    if req.method == 'POST':
        try:
            # Example logic for POST request
            req_body = req.get_json()
            # Here you would process the JSON data as needed for fraud detection
            result = {"message": "Data processed successfully", "data": req_body}

            # Send a successful response with CORS headers
            headers = {
                "Access-Control-Allow-Origin": "https://jolly-bay-02c912b03.5.azurestaticapps.net",
                "Content-Type": "application/json"
            }
            return func.HttpResponse(
                json.dumps(result),
                status_code=200,
                headers=headers
            )

        except ValueError:
            # Handle JSON parsing errors
            return func.HttpResponse(
                json.dumps({"error": "Invalid JSON input"}),
                status_code=400,
                content_type="application/json",
                headers={
                    "Access-Control-Allow-Origin": "https://jolly-bay-02c912b03.5.azurestaticapps.net"
                }
            )

    # If the method is not supported, return a 405 Method Not Allowed response
    return func.HttpResponse(
        "Method not allowed",
        status_code=405,
        headers={
            "Access-Control-Allow-Origin": "https://jolly-bay-02c912b03.5.azurestaticapps.net"
        }
    )
