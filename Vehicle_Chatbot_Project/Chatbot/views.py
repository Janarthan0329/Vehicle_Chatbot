from django.http import JsonResponse
from .Vehicle_Chatbot import  get_vehicle_table_data
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
from .Vehicle_Chatbot1 import handle_interaction, query_vehicle_data
from .recomendation_engine import compare, get_vehicle_specifications, calculate_finance_details, get_seller_info
from .utils import load_vehicle_data

# Load the dataset globally
df = load_vehicle_data("./data/vehicles_augmented.xlsx")

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
def multi_step_interaction_view(request):
    """
    Django view to handle multi-step interaction for vehicle recommendations.
    """
    if request.method == "POST":
        try:
            # Parse the JSON body
            body = json.loads(request.body)
            query = body.get("query", "")
            user_id = body.get("user_id", "default_user")  

            if not query:
                return JsonResponse({"status": "error", "message": "Query parameter is required."})

            # Import the dataframe and pass it to handle_interaction
            from .Vehicle_Chatbot1 import handle_interaction, df
            result = handle_interaction(query, user_id, df)

            # Ensure result is a dictionary
            if not isinstance(result, dict):
                return JsonResponse({"status": "error", "message": "Invalid response format from handle_interaction."})

            return JsonResponse(result)
        except json.JSONDecodeError:
            return JsonResponse({"status": "error", "message": "Invalid JSON body."})
        except Exception as e:
            logger.error(f"An error occurred: {str(e)}")
            return JsonResponse({"status": "error", "message": "An unexpected error occurred."})
    else:
        return JsonResponse({"status": "error", "message": "Only POST requests are allowed."})



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
            user_id = body.get("user_id", "default_user") 

            if not query:
                return JsonResponse({"status": "error", "message": "Query parameter is required."})

            # Call the query_vehicle_data function
            result = query_vehicle_data(query, user_id)
            return JsonResponse(result)
        except json.JSONDecodeError:
            return JsonResponse({"status": "error", "message": "Invalid JSON body."})
        except Exception as e:
            logger.error(f"An error occurred: {str(e)}")
            return JsonResponse({"status": "error", "message": "An unexpected error occurred."})
    else:
        return JsonResponse({"status": "error", "message": "Only POST requests are allowed."})



@csrf_exempt
def compare_view(request):
    if request.method == "POST":
        try:
            body = json.loads(request.body)
            vehicles = body.get("vehicles", "")
            vehicle_names = [v.strip() for v in vehicles.split(",")]

            if len(vehicle_names) != 2:
                return JsonResponse({"status": "error", "message": "Please provide exactly two vehicle names separated by a comma."})

            vehicle1, vehicle2 = vehicle_names
            result = compare(vehicle1, vehicle2, df)

            # Ensure result is a dictionary
            if not isinstance(result, dict):
                return JsonResponse(result, safe=False)

            return JsonResponse(result)
        except Exception as e:
            return JsonResponse({"status": "error", "message": f"An error occurred: {str(e)}"})
    return JsonResponse({"status": "error", "message": "Invalid request method. Please use POST."})




@csrf_exempt
def specifications_view(request):
    if request.method == "POST":
        try:
            body = json.loads(request.body)
            vehicle_name = body.get("vehicle_name", "")

            if not vehicle_name:
                return JsonResponse({"status": "error", "message": "The 'vehicle_name' parameter is required."})

            result = get_vehicle_specifications(vehicle_name, df)
            return JsonResponse(result)
        except Exception as e:
            return JsonResponse({"status": "error", "message": f"An error occurred: {str(e)}"})
    return JsonResponse({"status": "error", "message": "Invalid request method. Please use POST."})


@csrf_exempt
def financial_options_view(request):
    """
    Django view to handle financial options requests.
    """
    if request.method == "POST":
        try:
            body = json.loads(request.body)
            vehicle_name = body.get("vehicle_name", "").strip()
            installment_months = body.get("installment_months", None)

            if not vehicle_name:
                return JsonResponse({"status": "error", "message": "The 'vehicle_name' parameter is required."})

            if installment_months not in [12, 24, 36, 48]:
                return JsonResponse({"status": "error", "message": "Invalid 'installment_months'. Please choose from 12, 24, 36, or 48."})

            # Calculate finance details
            result = calculate_finance_details(vehicle_name, installment_months, df)

            return JsonResponse(result)
        except json.JSONDecodeError:
            return JsonResponse({"status": "error", "message": "Invalid JSON body."})
        except Exception as e:
            return JsonResponse({"status": "error", "message": f"An error occurred: {str(e)}"})
    return JsonResponse({"status": "error", "message": "Invalid request method. Please use POST."})


@csrf_exempt
def choose_vehicle_view(request):
    """
    Django view to handle the selection of a vehicle and provide seller information.
    """
    if request.method == "POST":
        try:
            # Parse the JSON body
            body = json.loads(request.body)
            vehicle_name = body.get("vehicle_name", "").strip()

            if not vehicle_name:
                return JsonResponse({"status": "error", "message": "The 'vehicle_name' parameter is required."})

            # Fetch seller information for the selected vehicle
            result = get_seller_info(vehicle_name, df)

            if result["status"] == "error":
                return JsonResponse({"status": "error", "message": result["message"]})

            seller_info = result["seller_info"]
            response = {
                "status": "success",
                "response": f"""
🎯 You’ve selected: {seller_info['Vehicle Name']}
📞 Seller Info:
• Dealer: {seller_info['Dealer']}
• Phone: {seller_info['Phone']}
• Email: {seller_info['Email']}
• Location: {seller_info['Location']}
________________________________________
❓Would you recommend this vehicle to others?
👍 Yes
👎 No
"""
            }
            return JsonResponse(response)
        except json.JSONDecodeError:
            return JsonResponse({"status": "error", "message": "Invalid JSON body."})
        except Exception as e:
            return JsonResponse({"status": "error", "message": f"An error occurred: {str(e)}"})
    return JsonResponse({"status": "error", "message": "Invalid request method. Please use POST."})



@csrf_exempt
def restart_server(request):
    """
    Django view to restart the server.
    """
    if request.method == "POST":
        try:
            # Restart the Django server
            os.system("python manage.py runserver")
            return JsonResponse({"status": "success", "message": "Server restarted successfully."})
        except Exception as e:
            return JsonResponse({"status": "error", "message": f"Failed to restart server: {str(e)}"})
    return JsonResponse({"status": "error", "message": "Invalid request method. Please use POST."})


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

            # Remove invalid keys
            valid_columns = vehicle_filter_data['data'].columns
            filters = {key: value for key, value in filters.items() if key in valid_columns}

            # Log and remove unexpected keys
            unexpected_keys = set(body.get("filters", {}).keys()) - set(valid_columns)
            if unexpected_keys:
                logger.warning(f"Unexpected keys in filters: {unexpected_keys}")

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
def vehicle_specifications_view(request, vehicle_id):
    """
    Django view to fetch specifications for a specific vehicle.
    """
    if request.method == "GET":
        try:
            # Load the vehicle dataset
            comparator_path = os.path.join(BASE_DIR, "Chatbot/ml_models", "vehicle_comparator.pkl")
            with open(comparator_path, 'rb') as f:
                df_comparator = pickle.load(f)

            # Find the vehicle by ID
            selected_vehicle = df_comparator[df_comparator['id'] == int(vehicle_id)]

            if selected_vehicle.empty:
                return JsonResponse({"status": "error", "message": "Vehicle not found."})

            # Convert the vehicle details to a dictionary
            vehicle_details = selected_vehicle.iloc[0].to_dict()

            # Prepare the specifications response
            specifications = {
                "Brand": vehicle_details.get("brand"),
                "Model": vehicle_details.get("model"),
                "Type": vehicle_details.get("type"),
                "Category": vehicle_details.get("category"),
                "Price": f"LKR {vehicle_details.get('price', 0)}.00",
                "Year": vehicle_details.get("year"),
                "Fuel Type": vehicle_details.get("fuel_type"),
                "Mileage": vehicle_details.get("mileage"),
                "Engine Capacity": vehicle_details.get("engine_capacity"),
                "Fuel_Tank_Capacity": vehicle_details.get("fuel_tank_capacity"),
                "Seat Capacity": vehicle_details.get("seat_capacity"),
                "Transmission": vehicle_details.get("transmission"),
                "Safety Rating": vehicle_details.get("safety_rating"),
                "Maintenance Cost": vehicle_details.get("maintenance_cost"),
                "After Sales Service": vehicle_details.get("after_sales_service"),
                "Financing Options": vehicle_details.get("financing_options"),
                "Insurance Info": vehicle_details.get("insurance_info"),
                "Additional Features": vehicle_details.get("additional_features"),
                "Warranty": vehicle_details.get("warranty"),
            }

            return JsonResponse({"status": "success", "specifications": specifications})
        except Exception as e:
            logger.error(f"An error occurred: {str(e)}")
            return JsonResponse({"status": "error", "message": "An error occurred while fetching vehicle specifications."})
    else:
        return JsonResponse({"status": "error", "message": "Only GET requests are allowed."})


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

            # Validate vehicle data
            required_keys = ['brand', 'model', 'type']
            for vehicle in [vehicle1, vehicle2]:
                for key in required_keys:
                    if key not in vehicle:
                        return JsonResponse({"status": "error", "message": f"Missing key '{key}' in vehicle data."})
                    
            # Ensure no interference with filters
            logger.info(f"Comparing vehicles: {vehicle1} and {vehicle2}") 
                    
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
    
    
    
    

@csrf_exempt
def price_recommendations_view(request):
    """
    Django view to calculate price and finance recommendations.
    """
    if request.method == "POST":
        try:
            # Parse the JSON body
            body = json.loads(request.body)
            vehicle = body.get("vehicle", {})
            installment_months = body.get("installment_months", None)

            if not vehicle:
                return JsonResponse({"status": "error", "message": "Vehicle details are required."})

            # Load the vehicle_comparator.pkl file
            comparator_path = os.path.join(BASE_DIR, "Chatbot/ml_models", "vehicle_comparator.pkl")
            with open(comparator_path, 'rb') as f:
                df_comparator = pickle.load(f)

            # Find the selected vehicle in the dataset
            selected_vehicle = df_comparator[
                (df_comparator['brand'].str.lower() == vehicle['brand'].lower()) &
                (df_comparator['model'].str.lower() == vehicle['model'].lower()) &
                (df_comparator['type'].str.lower() == vehicle['type'].lower())
            ]

            if selected_vehicle.empty:
                return JsonResponse({"status": "error", "message": "Vehicle not found in the dataset."})

            # Extract vehicle details
            vehicle_details = selected_vehicle.iloc[0].to_dict()
            price = vehicle_details['price']
            tax_rate = 0.1  # Assume 10% tax
            tax = price * tax_rate
            final_price = price + tax
            down_payment = 0.5 * final_price

            # If installment months are provided, calculate monthly payment
            monthly_payment = None
            if installment_months:
                monthly_payment = (final_price - down_payment) / installment_months

            # Round all price-related values and append "LKR"
            price = round(price)
            tax = round(tax)
            final_price = round(final_price)
            down_payment = round(down_payment)
            monthly_payment = round(monthly_payment) if monthly_payment else None
            
            # Prepare the response
            response = {
                "status": "success",
                "vehicle_details": {
                    "brand": vehicle_details.get("brand"),
                    "model": vehicle_details.get("model"),
                    "type": vehicle_details.get("type"),
                    "category": vehicle_details.get("category"),
                    "price": float(vehicle_details.get("price", 0)),
                    "year": vehicle_details.get("year"),
                    "fuel_type": vehicle_details.get("fuel_type"),
                    "mileage": vehicle_details.get("mileage"),
                    "transmission": vehicle_details.get("transmission"),
                    "safety_rating": vehicle_details.get("safety_rating"),
                    "warranty": vehicle_details.get("warranty"),
                },
                "price_details": {
                    "Price": float(price),  # Ensure JSON serializability
                    "Tax": float(tax),
                    "Total Price": float(final_price),
                    "Downpayment": float(down_payment),
                    "Installment Months": installment_months or "N/A",
                    "Monthly Payment": float(monthly_payment) if monthly_payment else "N/A"
                }
            }
            return JsonResponse(response)
        except Exception as e:
            logger.error(f"An error occurred: {str(e)}")
            return JsonResponse({"status": "error", "message": "An error occurred while processing the request."})
    else:
        return JsonResponse({"status": "error", "message": "Only POST requests are allowed."})