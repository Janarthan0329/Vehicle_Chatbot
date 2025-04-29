import pandas as pd
from .database_handler import  store_vehicle

user_state = {}

def handle_interaction(query, user_id, df):
    global user_state

    # Check if the user wants to start over
    if query.strip().lower() == "start over":
        return reset_interaction(user_id)
    
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
        return {"status": "success", "response": "Thanks! And how many seats do you need? (e.g., bike - 1 or 2, Car - 3, 4, 5, 6, 7)"}

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
                    "response": "No vehicles match your preferences. Please adjust your criteria. (brand, fuel type, or seat capacity)"
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


    # Step 10: Installment months
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
    
    
    
    # Step 11: Choose a vehicle
    if state["step"] == 12:
        if query.lower() == "✅ choose a vehicle":
            state["step"] += 1
            return {"status": "success", "response": "Please provide your final vehicle choice to buy (e.g., 'Honda BR-V VTi-S')."}


    # Step 12: Seller info
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
        state["selected_vehicle"] = seller_info  # Save vehicle info in state
        state["step"] += 1  # Move to the next step
        return {"status": "success", "response": response}


    # Step 14: Recommendation feedback stored in the database
    if state["step"] == 14:
        if query.strip().lower() == "yes":
            # Path to the Excel file
            excel_file_path = "./Chatbot/data/vehicles_augmented.xlsx"

            # Get the selected vehicle name
            selected_vehicle_name = state.get("selected_vehicle", {}).get("Vehicle Name")
            if selected_vehicle_name:
                store_vehicle(selected_vehicle_name, excel_file_path)
                return {"status": "success", "response": "Thank you for your recommendation! The score has been updated."}
            else:
                return {"status": "error", "response": "No vehicle selected to recommend."}

        return {"status": "success", "response": "Thank you for your feedback!"}



    # Load the Flan-T5 model and tokenizer
    model_name = "google/flan-t5-base"
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForSeq2SeqLM.from_pretrained(model_name)

    # Step 15: Handle "recommend me" and semantic queries
    if state["step"] == 15:
        if query.strip().lower() == "recommend me":
            # Respond to "recommend me" command
            return {"status": "success", "response": "Ask me questions related to recommendations."}
        
        # Perform semantic query
        retrieved_data = semantic_query(query, df)

        if not retrieved_data:
            return {"status": "error", "response": "No relevant data found for your query."}

        # Build prompt for the LLM
        prompt = "You are a vehicle recommendation assistant. Answer the user's question based on the following data:\n\n"
        for i, item in enumerate(retrieved_data):
            prompt += f"Vehicle {i+1}: {item}\n"
        prompt += f"\nUser's question: {query}\nAnswer:"

        # Generate response using Flan-T5
        inputs = tokenizer(prompt, return_tensors="pt", max_length=512, truncation=True)
        outputs = model.generate(inputs.input_ids, max_length=150, num_beams=2, early_stopping=True)
        answer = tokenizer.decode(outputs[0], skip_special_tokens=True)

        return {"status": "success", "response": answer, "retrieved_data": retrieved_data}
    


def reset_interaction(user_id):
    """
    Resets the interaction flow for the given user ID.
    """
    global user_state
    if user_id in user_state:
        user_state[user_id] = {"step": 0, "preferences": {}}
    return {"status": "success", "response": "Just Say Hi to start over!"}