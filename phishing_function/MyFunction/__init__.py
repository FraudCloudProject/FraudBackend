import logging
import azure.functions as func
import json
import os

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
            req_body = req.get_json()
            logging.info(f"Received request body: {req_body}")

            # Your processing logic here
            # For now, we'll just echo back the received data
            result = {"message": "Data received successfully", "data": req_body}

            return func.HttpResponse(
                json.dumps(result),
                status_code=200,
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