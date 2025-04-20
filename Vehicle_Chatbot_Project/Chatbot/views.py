from django.http import JsonResponse
from .Vehicle_Chatbot import query_vehicle_data, get_vehicle_table_data
from django.shortcuts import render
import json
from django.views.decorators.csrf import csrf_exempt
import logging


def home_view(request):
    """
    Renders the homepage.
    """
    return render(request, 'chatbot/home.html')

def default_chatbot_view(request):
    """
    Renders the chatbot interface.
    """
    return render(request, 'chatbot/chatbot.html')

logger = logging.getLogger(__name__)

@csrf_exempt
def vehicle_query_view(request):
    """
    Django view to handle vehicle-related queries.
    """
    if request.method == "POST":
        try:
            # Parse the JSON body
            body = json.loads(request.body)
            query = body.get("query", "")
            logger.info(f"Received query: {query}")
            if not query:
                return JsonResponse({"status": "error", "message": "Query parameter is required."})
            
            # Call the query_vehicle_data function
            result = query_vehicle_data(query)
            logger.info(f"Query result: {result}")
            return JsonResponse(result)
        except json.JSONDecodeError:
            logger.error("Invalid JSON body.")
            return JsonResponse({"status": "error", "message": "Invalid JSON body."})
    else:
        logger.error("Invalid request method.")
        return JsonResponse({"status": "error", "message": "Only POST requests are allowed."})
    
    

@csrf_exempt
def get_vehicle_table_view(request):
    """
    Django view to fetch vehicle details for the table.
    """
    if request.method == "POST":
        try:
            # Fetch vehicle table data
            result = get_vehicle_table_data()
            print(result)
            
            # Check if the result contains vehicles
            if result.get("status") == "success" and "vehicles" in result:
                return JsonResponse(result)
            else:
                logger.error("No vehicles found in the response.")
                return JsonResponse({"status": "error", "message": "No vehicles found."})
        except Exception as e:
            logger.error(f"An error occurred while processing the request: {str(e)}")
            return JsonResponse({"status": "error", "message": "An error occurred while processing the request."})
    else:
        logger.error("Invalid request method.")
        return JsonResponse({"status": "error", "message": "Only POST requests are allowed."})