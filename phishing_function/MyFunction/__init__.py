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
key = os.environ['KEY']
text_analytics_client = TextAnalyticsClient(endpoint=endpoint, credential=AzureKeyCredential(key))

# Fraud detection model endpoint
model_endpoint = "http://d3251e64-1a14-46c8-b197-5541ab06a38e.swedencentral.azurecontainer.io/score"

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Processing upload...')

    try:
        # Retrieve uploaded file from request
        uploaded_file = req.files['file']

        # Process the file content using Text Analytics
        documents = [uploaded_file.read().decode('utf-8')]
        response = text_analytics_client.analyze_sentiment(documents=documents)
        sentiments = [doc.sentiment for doc in response]

        # Call the fraud detection model with processed features
        model_response = requests.post(model_endpoint, json={"text": documents[0], "sentiments": sentiments})
        result = model_response.json()

        headers = {
                "Access-Control-Allow-Origin": "*",  # Allow requests from all domains (use a specific domain in production)
                "Access-Control-Allow-Methods": "POST, OPTIONS",
                "Access-Control-Allow-Headers": "Content-Type"
            }

        return func.HttpResponse(
            json.dumps(result),
            mimetype="application/json",
            headers=headers
        )
    except Exception as e:
        logging.error(f"Error processing request: {e}")
        return func.HttpResponse(f"Error processing request: {e}", status_code=500)

    
