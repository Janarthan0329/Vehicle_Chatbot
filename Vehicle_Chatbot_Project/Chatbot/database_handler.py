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