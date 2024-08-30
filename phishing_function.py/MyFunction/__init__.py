import logging
import azure.functions as func
from azure.storage.blob import BlobServiceClient
from azure.ai.textanalytics import TextAnalyticsClient
from azure.core.credentials import AzureKeyCredential
import requests
import json

# Set up Azure Cognitive Services client
endpoint = "YOUR_TEXT_ANALYTICS_ENDPOINT"
key = "YOUR_TEXT_ANALYTICS_KEY"
text_analytics_client = TextAnalyticsClient(endpoint=endpoint, credential=AzureKeyCredential(key))

# Fraud detection model endpoint
model_endpoint = "YOUR_MODEL_ENDPOINT"

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

        return func.HttpResponse(json.dumps(result), mimetype="application/json")

    except Exception as e:
        logging.error(f"Error processing request: {e}")
        return func.HttpResponse(f"Error processing request: {e}", status_code=500)
