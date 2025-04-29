import pandas as pd
from .database.db_config import get_db_connection
import logging

logger = logging.getLogger(__name__)


def store_vehicle(vehicle_name, excel_file_path):
    logger.info(f"Updating recommendation score for vehicle: {vehicle_name}")
    """
    Store a vehicle in the database or update its recommendation score if it already exists.
    
    Args:
        vehicle_name (str): The name of the vehicle (model) to store or update.
        excel_file_path (str): Path to the Excel file containing vehicle details.
    """
    # Load the Excel file
    try:
        df = pd.read_excel(excel_file_path)
    except Exception as e:
        print(f"Error reading Excel file: {e}")
        return

    # Find the vehicle details by name
    df["vehicle_name"] = (df["brand"] + " " + df["model"] + " " + df["type"] + " " + df["category"]).str.lower()
    vehicle_data = df[df["vehicle_name"] == vehicle_name.lower()].to_dict(orient="records")
    if not vehicle_data:
        print(f"Vehicle '{vehicle_name}' not found in the Excel file.")
        return

    # Extract the first matching vehicle (assuming unique model names)
    vehicle_data = vehicle_data[0]

    # Connect to the database
    conn = get_db_connection()
    cursor = conn.cursor()

    # Check if the vehicle already exists in the database
    cursor.execute("SELECT recomendation_score FROM vehicles WHERE id = %s", (vehicle_data["id"],))
    result = cursor.fetchone()

    if result:
        # Update recommendation score
        new_score = result[0] + 1
        cursor.execute("UPDATE vehicles SET recomendation_score = %s WHERE id = %s", (new_score, vehicle_data["id"]))
    else:
        # Insert new vehicle record
        cursor.execute("""
            INSERT INTO vehicles (
                id, recomendation_score, brand, model, type, category, price, year, fuel_type, mileage,
                engine_capacity, fuel_tank_capacity, seat_capacity, transmission, safety_rating,
                maintenance_cost, after_sales_service, financing_options, insurance_info,
                additional_features, warranty, seller_name, seller_contact, seller_location,
                make_country, imported_from
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            vehicle_data["id"], 1, vehicle_data["brand"], vehicle_data["model"], vehicle_data["type"],
            vehicle_data["category"], vehicle_data["price"], vehicle_data["year"], vehicle_data["fuel_type"],
            vehicle_data["mileage"], vehicle_data["engine_capacity"], vehicle_data["fuel_tank_capacity"],
            vehicle_data["seat_capacity"], vehicle_data["transmission"], vehicle_data["safety_rating"],
            vehicle_data["maintenance_cost"], vehicle_data["after_sales_service"], vehicle_data["financing_options"],
            vehicle_data["insurance_info"], vehicle_data["additional_features"], vehicle_data["warranty"],
            vehicle_data["seller_name"], vehicle_data["seller_contact"], vehicle_data["seller_location"],
            vehicle_data["make_country"], vehicle_data["imported_from"]
        ))

    conn.commit()
    conn.close()
    


import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
from .database.db_config import get_db_connection

# Load the embedding model
embedding_model = SentenceTransformer("all-MiniLM-L6-v2")

# Initialize FAISS index (to be built dynamically)
faiss_index = None
vehicle_data = []  # To store vehicle data for FAISS search

def build_faiss_index():
    """
    Builds a FAISS index from the database table.
    """
    global faiss_index, vehicle_data

    try:
        # Connect to the database and fetch vehicle data
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM vehicles ORDER BY recomendation_score DESC")
        rows = cursor.fetchall()
        conn.close()

        if not rows:
            print("No data found in the vehicles table.")
            return

        # Generate embeddings for all vehicles
        vehicle_texts = [
            f"{row['brand']} {row['model']} {row['type']} {row['category']} {row['price']} {row['year']}"
            for row in rows
        ]
        embeddings = embedding_model.encode(vehicle_texts)

        # Build FAISS index
        dimension = embeddings.shape[1]
        faiss_index = faiss.IndexFlatL2(dimension)
        faiss_index.add(np.array(embeddings).astype("float32"))

        # Store vehicle data for retrieval
        vehicle_data = rows
        print(f"FAISS index built with {len(rows)} entries.")
    except Exception as e:
        print(f"Error building FAISS index: {e}")
        

def semantic_query(query, df=None):
    """
    Performs a semantic query using FAISS or specific logic for predefined queries.
    Returns a single vehicle that best matches the query.
    """
    global faiss_index, vehicle_data

    # Predefined queries
    if "cheapest vehicle" in query.lower():
        # Return the vehicle with the lowest price
        return [min(vehicle_data, key=lambda x: x["price"])]

    if "most expensive vehicle" in query.lower():
        # Return the vehicle with the highest price
        return [max(vehicle_data, key=lambda x: x["price"])]
    
    if "most recommended vehicle" in query.lower():
        # Return the vehicle with the highest recommendation score
        return [max(vehicle_data, key=lambda x: x["recomendation_score"])]

    if "fuel-efficient" in query.lower() or "highest mileage" in query.lower():
        # Return the vehicle with the highest mileage
        filtered_vehicles = [
            vehicle for vehicle in vehicle_data if "mileage" in vehicle and vehicle["mileage"] is not None
        ]
        if not filtered_vehicles:
            return {"status": "error", "message": "No vehicles with mileage data found."}
        return [max(filtered_vehicles, key=lambda x: x["mileage"])]

    if "automatic transmission" in query.lower():
        # Return the first vehicle with automatic transmission
        filtered_vehicles = [vehicle for vehicle in vehicle_data if vehicle["transmission"].lower() == "automatic"]
        if filtered_vehicles:
            return [filtered_vehicles[0]]
        return {"status": "error", "message": "No vehicles with automatic transmission found."}

    if "manual transmission" in query.lower():
        # Return the first vehicle with manual transmission
        filtered_vehicles = [vehicle for vehicle in vehicle_data if vehicle["transmission"].lower() == "manual"]
        if filtered_vehicles:
            return [filtered_vehicles[0]]
        return {"status": "error", "message": "No vehicles with manual transmission found."}

    if "specific brand" in query.lower():
        # Return the first vehicle of the specified brand
        brand = query.split("from")[-1].strip().lower()
        filtered_vehicles = [vehicle for vehicle in vehicle_data if vehicle["brand"].lower() == brand]
        if filtered_vehicles:
            return [filtered_vehicles[0]]
        return {"status": "error", "message": f"No vehicles found for brand '{brand}'."}

    if "price range" in query.lower():
        # Return the first vehicle within the specified price range
        try:
            words = query.lower().split()
            min_price = int(words[words.index("between") + 1])
            max_price = int(words[words.index("and") + 1])
            filtered_vehicles = [
                vehicle for vehicle in vehicle_data if min_price <= vehicle["price"] <= max_price
            ]
            if filtered_vehicles:
                return [filtered_vehicles[0]]
            return {"status": "error", "message": f"No vehicles found in the price range {min_price} to {max_price}."}
        except (ValueError, IndexError):
            return {"status": "error", "message": "Invalid price range format in query."}

    if "fuel type" in query.lower():
        # Return the first vehicle with the specified fuel type
        fuel_type = query.split("fuel type")[-1].strip().lower()
        filtered_vehicles = [vehicle for vehicle in vehicle_data if vehicle["fuel_type"].lower() == fuel_type]
        if filtered_vehicles:
            return [filtered_vehicles[0]]
        return {"status": "error", "message": f"No vehicles found with fuel type '{fuel_type}'."}

    # Default: Perform FAISS semantic search for other queries
    if faiss_index is None:
        build_faiss_index()

    # Embed the query
    query_embedding = embedding_model.encode([query])

    # Perform FAISS search
    distances, indices = faiss_index.search(np.array(query_embedding).astype("float32"), k=1)
    retrieved_data = [vehicle_data[i] for i in indices[0]]

    if not retrieved_data:
        return {"status": "error", "message": "No relevant data found for your query."}

    return [retrieved_data[0]]