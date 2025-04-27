def recommend_vehicle(preferences, df):
    """
    Recommends vehicles based on user preferences.
    """
    try:
        # Validate preferences
        if not all(key in preferences for key in ["vehicle_type", "brand", "fuel_type", "seats"]):
            return {"status": "error", "message": "Missing required preferences: vehicle_type, brand, or fuel_type."}

        # Apply filters
        filtered_df = df[
            (df["type"].str.lower() == preferences["vehicle_type"].lower()) &
            (df["brand"].str.lower() == preferences["brand"].lower()) &
            (df["fuel_type"].str.lower() == preferences["fuel_type"].lower()) &
            (df["seat_capacity"] >= preferences["seats"])
        ]

        if filtered_df.empty:
            return {"status": "success", "response": "No vehicles match your preferences. Would you like to adjust your criteria?"}

        # Format recommendations
        vehicles = []
        for _, row in filtered_df.iterrows():
            vehicles.append({
                "Vehicle": f"{row['brand']} {row['model']} {row['type']} {row['category']}",
                "Price": f"Rs. {row['price']:,}",
                "Year": row['year'],
                "Fuel Type": row['fuel_type'],
                "Seats": row['seat_capacity'],
                "Mileage": f"{row['mileage']} km/l",
                "Transmission": row['transmission']
            })

        return {
            "status": "success",
            "response": "Here are some vehicles matching your preferences:",
            "vehicles": vehicles[:10]  
        }
    except Exception as e:
        return {"status": "error", "message": f"Error in recommendation engine: {str(e)}"} 
    
    
    
    
    
def compare(vehicle1, vehicle2, df):
    """
    Compares two vehicles based on their specifications.
    """
    try:
        # Create a vehicle_name column for comparison
        df["vehicle_name"] = (df["brand"] + " " + df["model"] + " " + df["type"] + " " + df["category"]).str.lower()

        # Filter the DataFrame for the two vehicles
        vehicle1_data = df[df["vehicle_name"] == vehicle1.lower()]
        vehicle2_data = df[df["vehicle_name"] == vehicle2.lower()]

        if vehicle1_data.empty or vehicle2_data.empty:
            missing = []
            if vehicle1_data.empty:
                missing.append(vehicle1)
            if vehicle2_data.empty:
                missing.append(vehicle2)
            return {"status": "error", "message": f"Vehicle(s) not found: {', '.join(missing)}"}

        # Convert the data to dictionaries
        vehicle1_data = vehicle1_data.iloc[0].to_dict()
        vehicle2_data = vehicle2_data.iloc[0].to_dict()

        # Prepare the comparison table
        comparison = {
            "Feature": ["Brand", "Model", "Type", "Category", "Price", "Engine Capacity", "Transmission", "Fuel Tank Capacity", "Safety Rating", "Year", "Fuel Type", "Seats", "Mileage"],
            vehicle1: [
                vehicle1_data.get("brand", "N/A"),
                vehicle1_data.get("model", "N/A"),
                vehicle1_data.get("type", "N/A"),
                vehicle1_data.get("category", "N/A"),
                f"Rs. {vehicle1_data.get('price', 'N/A'):,}",
                vehicle1_data.get("engine_capacity", "N/A"),
                vehicle1_data.get("transmission", "N/A"),
                vehicle1_data.get("fuel_tank_capacity", "N/A"),
                vehicle1_data.get("safety_rating", "N/A"),
                vehicle1_data.get("year", "N/A"),
                vehicle1_data.get("fuel_type", "N/A"),
                vehicle1_data.get("seat_capacity", "N/A"),
                f"{vehicle1_data.get('mileage', 'N/A')} km/l"
            ],
            vehicle2: [
                vehicle2_data.get("brand", "N/A"),
                vehicle2_data.get("model", "N/A"),
                vehicle2_data.get("type", "N/A"),
                vehicle2_data.get("category", "N/A"),
                f"Rs. {vehicle2_data.get('price', 'N/A'):,}",
                vehicle2_data.get("engine_capacity", "N/A"),
                vehicle2_data.get("transmission", "N/A"),
                vehicle2_data.get("fuel_tank_capacity", "N/A"),
                vehicle2_data.get("safety_rating", "N/A"),
                vehicle2_data.get("year", "N/A"),
                vehicle2_data.get("fuel_type", "N/A"),
                vehicle2_data.get("seat_capacity", "N/A"),
                f"{vehicle2_data.get('mileage', 'N/A')} km/l"
            ],
        }
        return {
            "status": "success", 
            "comparison": comparison,
            "next_options": ["📊 View Specifications"]
        }
    except Exception as e:
        return {"status": "error", "message": f"Error comparing vehicles: {str(e)}"}
    
    



def get_vehicle_specifications(vehicle_name, df):
    """
    Fetches all specifications for a given vehicle.
    """
    try:
        # Create a vehicle_name column for matching
        df["vehicle_name"] = (df["brand"] + " " + df["model"] + " " + df["type"] + " " + df["category"]).str.lower()

        # Filter the DataFrame for the given vehicle
        vehicle_data = df[df["vehicle_name"] == vehicle_name.lower()]

        if vehicle_data.empty:
            return {"status": "error", "message": f"Vehicle not found: {vehicle_name}"}

        # Convert the data to a dictionary
        vehicle_data = vehicle_data.iloc[0].to_dict()

        # Prepare the specifications
        specifications = {
            "Brand": vehicle_data.get("brand", "N/A"),
            "Model": vehicle_data.get("model", "N/A"),
            "Type": vehicle_data.get("type", "N/A"),
            "Category": vehicle_data.get("category", "N/A"),
            "Price": f"Rs. {vehicle_data.get('price', 'N/A'):,}",
            "Engine Capacity": vehicle_data.get("engine_capacity", "N/A"),
            "Transmission": vehicle_data.get("transmission", "N/A"),
            "Fuel Tank Capacity": vehicle_data.get("fuel_tank_capacity", "N/A"),
            "Safety Rating": vehicle_data.get("safety_rating", "N/A"),
            "Year": vehicle_data.get("year", "N/A"),
            "Fuel Type": vehicle_data.get("fuel_type", "N/A"),
            "Seats": vehicle_data.get("seat_capacity", "N/A"),
            "Mileage": f"{vehicle_data.get('mileage', 'N/A')} km/l"
        }

        return {
            "status": "success", 
            "specifications": specifications,
            "next_options": ["💰 Financial Options"] 
        }
    except Exception as e:
        return {"status": "error", "message": f"Error fetching vehicle specifications: {str(e)}"}
    
    
    
def calculate_finance_details(vehicle_name, installment_months, df):
    """
    Calculates finance details for a given vehicle and installment months.
    """
    try:
        # Create a vehicle_name column for matching
        df["vehicle_name"] = (df["brand"] + " " + df["model"] + " " + df["type"] + " " + df["category"]).str.lower()

        # Filter the DataFrame for the given vehicle
        vehicle_data = df[df["vehicle_name"] == vehicle_name.lower()]

        if vehicle_data.empty:
            return {"status": "error", "message": f"Vehicle not found: {vehicle_name}"}

        # Get the price of the vehicle
        vehicle_data = vehicle_data.iloc[0].to_dict()
        price = vehicle_data.get("price", 0)

        # Calculate finance details
        tax = round(0.05 * price, 2)
        actual_price = round(price + tax, 2)
        downpayment = round(actual_price / 2, 2)
        monthly_amount = round((actual_price - downpayment) / installment_months, 2)
        interest = round(0.009 * monthly_amount, 2)
        monthly_payment = round(monthly_amount + interest, 2)

        # Format values as Rs. xxx,xxx,xxx.00
        finance_details = {
            "Vehicle Name": vehicle_name,
            "Price": f"Rs. {price:,.2f}",
            "Tax (5%)": f"Rs. {tax:,.2f}",
            "Actual Price": f"Rs. {actual_price:,.2f}",
            "Downpayment (50%)": f"Rs. {downpayment:,.2f}",
            "Installment Months": installment_months,
            "Monthly Amount": f"Rs. {monthly_amount:,.2f}",
            "Interest (0.09%)": f"Rs. {interest:,.2f}",
            "Monthly Payment": f"Rs. {monthly_payment:,.2f}"
        }

        return {
            "status": "success", 
            "finance_details": finance_details,
            "next_options": ["✅ Choose a Vehicle"]
        }
    except Exception as e:
        return {"status": "error", "message": f"Error calculating finance details: {str(e)}"}
    





def get_seller_info(vehicle_name, df):
    """
    Fetches seller information for a given vehicle.
    """
    try:
        # Create a vehicle_name column for matching
        df["vehicle_name"] = (df["brand"] + " " + df["model"] + " " + df["type"] + " " + df["category"]).str.lower()

        # Filter the DataFrame for the given vehicle
        vehicle_data = df[df["vehicle_name"] == vehicle_name.lower()]

        if vehicle_data.empty:
            return {"status": "error", "message": f"Vehicle not found: {vehicle_name}"}

        # Get seller information
        vehicle_data = vehicle_data.iloc[0].to_dict()
        seller_name = vehicle_data.get("seller_name", "N/A")
        seller_email = f"{seller_name.replace(' ', '').lower()}@gmail.com" 
        
        seller_info = {
            "Vehicle Name": f"{vehicle_data.get('brand', 'N/A')} {vehicle_data.get('model', 'N/A')} {vehicle_data.get('type', 'N/A')}",
            "Dealer": seller_name,
            "Phone": vehicle_data.get("seller_contact", "N/A"),
            "Email": seller_email,
            "Location": vehicle_data.get("seller_location", "N/A")
        }

        return {"status": "success", "seller_info": seller_info}
    except Exception as e:
        return {"status": "error", "message": f"Error fetching seller information: {str(e)}"}