import pandas as pd

user_state = {}

def handle_interaction(query, user_id, df):
    global user_state

    # Initialize user state if not present
    if user_id not in user_state:
        user_state[user_id] = {"step": 0, "preferences": {}}

    state = user_state[user_id]

    # Step 1: Ask for vehicle type
    if state["step"] == 0:
        state["step"] += 1
        return {"status": "success", "response": "Hi there! 👋 What type of vehicle are you looking for? (e.g., Car, Bike, SUV)"}

    # Step 2: Capture vehicle type and ask for brand
    if state["step"] == 1:
        state["preferences"]["vehicle_type"] = query.strip()
        state["step"] += 1
        return {"status": "success", "response": "Great! Please type the brand you're interested in."}

    # Step 3: Capture brand and ask for fuel type
    if state["step"] == 2:
        state["preferences"]["brand"] = query.strip()
        state["step"] += 1
        return {"status": "success", "response": "Nice choice. What fuel type do you prefer? (e.g., Petrol, Diesel, Hybrid, Electric)"}

    # Step 4: Capture fuel type and ask for seat capacity
    if state["step"] == 3:
        state["preferences"]["fuel_type"] = query.strip()
        state["step"] += 1
        return {"status": "success", "response": "Thanks! And how many seats do you need?"}

    # Step 5: Capture seat capacity and recommend vehicles
    if state["step"] == 4:
        try:
            state["preferences"]["seats"] = int(query.strip())
            preferences = state["preferences"]

            # Normalize dataset columns
            df["type"] = df["type"].str.strip().str.lower()
            df["brand"] = df["brand"].str.strip().str.lower()
            df["fuel_type"] = df["fuel_type"].str.strip().str.lower()
            df["seat_capacity"] = pd.to_numeric(df["seat_capacity"], errors="coerce")

            # Mapping user input to dataset values
            vehicle_type_mapping = {
                "car": ["sedan", "hatchback", "suv", "coupe", "family"],
                "luxury car": ["luxury sedan", "executive", "luxury suv"],
                "bike": ["sports", "motorbike", "scooter"],
                "lorry": ["cooler truck", "truck", "mini truck", "heavy truck"],
                "suv": ["truck", "suv", "family"],
                "truck": ["truck", "pickup"]
            }
            mapped_types = vehicle_type_mapping.get(preferences["vehicle_type"].strip().lower(), [])

            if not mapped_types:
                return {
                    "status": "error",
                    "response": "Sorry, I couldn't understand the vehicle type. Please specify a valid type (e.g., Car, Bike, SUV, Truck)."
                }

            # Filter dataset based on preferences
            filtered_df = df[
                (df["type"].isin(mapped_types)) &
                (df["brand"] == preferences["brand"].strip().lower()) &
                (df["fuel_type"] == preferences["fuel_type"].strip().lower()) &
                (df["seat_capacity"].fillna(0).astype(int) == preferences["seats"])
            ]

            if filtered_df.empty:
                return {
                    "status": "success",
                    "response": "No vehicles match your preferences. Would you like to adjust your criteria?"
                }

            vehicles = []
            for _, row in filtered_df.iterrows():
                vehicles.append({
                    "Vehicle": f"{row['brand']} {row['model']} {row['type']} {row['category']}",
                    "Price": row['price'],
                    "Year": row['year'],
                    "Fuel Type": row['fuel_type'],
                    "Seats": row['seat_capacity'],
                    "Mileage": row['mileage'],
                    "Transmission": row['transmission']
                })

            state["step"] += 1
            state["vehicles"] = vehicles
            return {
                "status": "success",
                "response": "Awesome! Here are some vehicles that match your choices:",
                "vehicles": vehicles[:10],
                "next_options": ["🔍 Compare Vehicles"]
            }
        except ValueError:
            return {"status": "error", "response": "Invalid seat capacity. Please provide a valid number."}

    # Step 6: Compare vehicles
    if state["step"] == 5:
        if query.lower() == "🔍 compare vehicles":
            state["step"] += 1
            return {"status": "success", "response": "Please specify the two vehicles you'd like to compare (e.g., 'Toyota Corolla Sedan and Honda Civic Sedan')."}

    # Step 7: Process vehicle comparison
    if state["step"] == 6:
        vehicles_to_compare = query.lower().split(" and ")
        if len(vehicles_to_compare) != 2:
            return {
                "status": "error",
                "response": "Please provide exactly two vehicle names separated by 'and' keyword (e.g., 'Toyota Corolla Sedan and Honda Civic Sedan')."
            }

        vehicle1, vehicle2 = [v.strip() for v in vehicles_to_compare]
        comparison_result = compare(vehicle1, vehicle2, df)

        if comparison_result["status"] == "error":
            return {"status": "error", "response": comparison_result["message"]}

        comparison_table = comparison_result["comparison"]
        response = "Here's the comparison between the two vehicles:\n"
        for feature, v1, v2 in zip(
            comparison_table.get("Feature", []),
            comparison_table.get(vehicle1, []),
            comparison_table.get(vehicle2, [])
        ):
            response += f"- {feature}: {vehicle1} = {v1}, {vehicle2} = {v2}\n"

        state["step"] += 1
        return {
            "status": "success", 
            "response": response,
            "next_options": ["📊 View Specifications"]
        }

    # Default response if no step matches
    return {"status": "error", "response": "Invalid step in the interaction flow."}




    # Step 8: View specifications
    if state["step"] == 7:
        if query.lower() == "📊 view specifications":
            state["step"] += 1
            return {"status": "success", "response": "Please provide the vehicle name (e.g., 'Toyota Camry SUV Van')."}

    if state["step"] == 8:
        vehicle_name = query.strip()
        result = get_vehicle_specifications(vehicle_name, df)

        if result["status"] == "error":
            return {"status": "error", "response": result["message"]}

        specifications = result["specifications"]
        response = "Here are the specifications for the selected vehicle:\n"
        for key, value in specifications.items():
            response += f"- {key}: {value}\n"

        return {
            "status": "success", 
            "response": response,
            "next_options": ["💰 Financial Options"]
        }
    
    
    # Step 9: Financial options
    if state["step"] == 9:
        if query.lower() == "💰 financial options":
            state["step"] += 1
            return {"status": "success", "response": "Please provide the vehicle name (e.g., 'Toyota Camry SUV Van')."}

    if state["step"] == 10:
        vehicle_name = query.strip()
        state["vehicle_name"] = vehicle_name  # Save vehicle name in state
        state["step"] += 1
        return {"status": "success", "response": "Please provide the installment months (e.g., 12, 24, 36, 48)."}

    if state["step"] == 11:
        try:
            installment_months = int(query.strip())
            if installment_months not in [12, 24, 36, 48]:
                return {"status": "error", "response": "Invalid installment months. Please choose from 12, 24, 36, or 48."}

            vehicle_name = state.get("vehicle_name")
            result = calculate_finance_details(vehicle_name, installment_months, df)

            if result["status"] == "error":
                return {"status": "error", "response": result["message"]}

            finance_details = result["finance_details"]
            response = "Here are the finance details for the selected vehicle:\n"
            for key, value in finance_details.items():
                response += f"- {key}: {value}\n"

            return {
                "status": "success", 
                "response": response,
                "next_options": ["✅ Choose a Vehicle"]
            }
        
        except ValueError:
            return {"status": "error", "response": "Invalid input. Please provide a valid number for installment months."}
    
    
    if state["step"] == 12:
        if query.lower() == "✅ choose a vehicle":
            state["step"] += 1
            return {"status": "success", "response": "Please provide your final vehicle choice to buy (e.g., 'Honda BR-V VTi-S')."}

    if state["step"] == 13:
        vehicle_name = query.strip()
        result = get_seller_info(vehicle_name, df)

        if result["status"] == "error":
            return {"status": "error", "response": result["message"]}

        seller_info = result["seller_info"]
        response = (
            f"You’ve selected: {seller_info['Vehicle Name']}\n"
            f"Seller Info:\n"
            f"Dealer: {seller_info['Dealer']}\n"
            f"Phone: {seller_info['Phone']}\n"
            f"Email: {seller_info['Email']}\n"
            f"Location: {seller_info['Location']}\n"
            f"Would you recommend this vehicle to others?\n"
            f"Yes or No"
        )
        return {"status": "success", "response": response}