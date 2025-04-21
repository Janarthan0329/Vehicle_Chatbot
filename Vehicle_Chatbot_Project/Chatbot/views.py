from django.http import JsonResponse
from .Vehicle_Chatbot import query_vehicle_data, get_vehicle_table_data
from django.shortcuts import render
import json
from django.views.decorators.csrf import csrf_exempt
import logging
import pickle
import pandas as pd
import os
import joblib
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

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
    
    
    
    
# BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# # Load everything once at the top
# intent_classifier = joblib.load(os.path.join(BASE_DIR, "Chatbot/query_models", "intent_classifier.pkl"))
# embedder = joblib.load(os.path.join(BASE_DIR, "Chatbot/query_models", "semantic_embedder.pkl"))
# index = faiss.read_index(os.path.join(BASE_DIR, "Chatbot/query_models", "vehicle_faiss_index.index"))
# vehicle_texts = pd.read_csv(os.path.join(BASE_DIR, "Chatbot/query_models", "vehicle_combined_texts.csv"))['combined_text'].tolist()

# @csrf_exempt
# def vehicle_query_view(request):
#     if request.method == "POST":
#         try:
#             data = json.loads(request.body)
#             query = data.get("query", "").strip()
#             if not query:
#                 return JsonResponse({"status": "error", "message": "Empty query"})

#             # Predict intent
#             predicted_intent = intent_classifier.predict([query])[0]

#             # Embed and search
#             query_vector = embedder.encode([query])
#             _, top_k_indices = index.search(np.array(query_vector), k=3)
#             matches = [vehicle_texts[i] for i in top_k_indices[0]]

#             # Format result
#             formatted = format_response(predicted_intent, matches)
#             return JsonResponse({"status": "success", "response": formatted})

#         except Exception as e:
#             return JsonResponse({"status": "error", "message": str(e)})
#     else:
#         return JsonResponse({"status": "error", "message": "Only POST requests allowed"})

# def format_response(intent, matches):
#     response = f"Intent Detected: {intent.replace('_', ' ').title()}\n\n"
#     for idx, match in enumerate(matches, 1):
#         response += f"---\nVehicle {idx}:\n{match.strip()}\n"
#     return response






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







# Load the vehicle_filter.pkl model
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
model_path = os.path.join(BASE_DIR, "Chatbot/ml_models", "vehicle_filter.pkl")
with open(model_path, 'rb') as model_file:
    vehicle_filter_data = pickle.load(model_file)
    
@csrf_exempt
def filter_vehicles_view(request):
    if request.method == "POST":
        try:
            body = json.loads(request.body)
            filters = body.get("filters", {})
            logger.info(f"Received filters: {filters}")

            if not filters:
                return JsonResponse({"status": "error", "message": "Filters are required."})

            df_filter = vehicle_filter_data['data']
            encoders = vehicle_filter_data['encoders']

            # Transform filters using encoders
            for key, value in filters.items():
                if key in encoders:
                    filters[key] = encoders[key].transform([value])[0]

            # Apply filters to the dataset
            filtered_df = df_filter.copy()
            for key, value in filters.items():
                filtered_df = filtered_df[filtered_df[key] == value]

            # Inverse transform the filtered data
            for key, encoder in encoders.items():
                if key in filtered_df.columns:
                    filtered_df[key] = encoder.inverse_transform(filtered_df[key])

            # Convert the filtered data to a list of dictionaries
            vehicles = filtered_df.to_dict(orient='records')
            return JsonResponse({"status": "success", "response": vehicles})
        except Exception as e:
            logger.error(f"An error occurred: {str(e)}")
            return JsonResponse({"status": "error", "message": "An error occurred while processing the request."})
    else:
        return JsonResponse({"status": "error", "message": "Only POST requests are allowed."})






@csrf_exempt
def compare_vehicles_view(request):
    """
    Django view to compare two vehicles based on their specifications.
    """
    if request.method == "POST":
        try:
            # Parse the JSON body
            body = json.loads(request.body)
            vehicle1 = body.get("vehicle1", {})
            vehicle2 = body.get("vehicle2", {})

            if not vehicle1 or not vehicle2:
                return JsonResponse({"status": "error", "message": "Both vehicles must be provided."})

            # Load the vehicle_comparator.pkl file
            comparator_path = os.path.join(BASE_DIR, "Chatbot/ml_models", "vehicle_comparator.pkl")
            with open(comparator_path, 'rb') as f:
                df_comparator = pickle.load(f)

            # Filter the DataFrame for the two vehicles
            v1 = df_comparator[
                (df_comparator['brand'].str.lower() == vehicle1['brand'].lower()) &
                (df_comparator['model'].str.lower() == vehicle1['model'].lower()) &
                (df_comparator['type'].str.lower() == vehicle1['type'].lower())
            ]
            v2 = df_comparator[
                (df_comparator['brand'].str.lower() == vehicle2['brand'].lower()) &
                (df_comparator['model'].str.lower() == vehicle2['model'].lower()) &
                (df_comparator['type'].str.lower() == vehicle2['type'].lower())
            ]

            if v1.empty or v2.empty:
                return JsonResponse({"status": "error", "message": "One or both vehicles not found in the dataset."})

            # Create a comparison table
            comparison_data = {
                "Aspect": list(df_comparator.columns[3:]), 
                "Vehicle 1": v1.iloc[0, 3:].apply(lambda x: x.item() if hasattr(x, 'item') else x).tolist(),
                "Vehicle 2": v2.iloc[0, 3:].apply(lambda x: x.item() if hasattr(x, 'item') else x).tolist() 
            }

            return JsonResponse({"status": "success", "comparison": comparison_data})
        except Exception as e:
            logger.error(f"An error occurred: {str(e)}")
            return JsonResponse({"status": "error", "message": "An error occurred while processing the request."})
    else:
        return JsonResponse({"status": "error", "message": "Only POST requests are allowed."})