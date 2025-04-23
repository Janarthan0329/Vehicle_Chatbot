import pandas as pd
from sentence_transformers import SentenceTransformer
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import FAISS
from langchain.schema import Document
from langchain.llms import Ollama
import faiss
import numpy as np
import markdown2 
import logging
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer

# Configure logger
logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(),
    ]
)

# Load Excel file
df = pd.read_excel("../vehicles_augmented.xlsx")
df.dropna(inplace=True)

# Convert each row to a formatted text chunk
chunks = []
for _, row in df.iterrows():
    text = f"""
    ID: {row['id']}
    Brand: {row['brand']}
    Model: {row['model']}
    Type: {row['type']}
    Category: {row['category']}
    Price: {row['price']}
    Year: {row['year']}
    Fuel Type: {row['fuel_type']}
    Mileage: {row['mileage']}
    Engine Capacity: {row['engine_capacity']}
    Fuel Tank Capacity: {row['fuel_tank_capacity']}
    Seat Capacity: {row['seat_capacity']}
    Transmission: {row['transmission']}
    Safety Rating: {row['safety_rating']}
    Maintenance Cost: {row['maintenance_cost']}
    After Sales Service: {row['after_sales_service']}
    Financing Options: {row['financing_options']}
    Insurance Info: {row['insurance_info']}
    Additional Features: {row['additional_features']}
    Warranty: {row['warranty']}
    Seller: {row['seller_name']} - {row['seller_contact']} - {row['seller_location']}
    Make Country: {row['make_country']}
    Imported From: {row['imported_from']}
    """
    chunks.append(text)

# Initialize the embedding model using LangChain's HuggingFaceEmbeddings
embedding_model = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

# Create FAISS vector store
docs = [Document(page_content=chunk) for chunk in chunks]
vector_store = FAISS.from_documents(docs, embedding=embedding_model)

# # Initialize the LLM model
# llm = Ollama(model="llama2")

# Load Flan-T5 model and tokenizer
model_name = "google/flan-t5-base"  
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForSeq2SeqLM.from_pretrained(model_name)



# Query Handling
def handle_rag_query(query):
    """
    Handles the user's query by guiding them through a structured communication flow,
    dynamically responding with relevant data from the dataset, and performing similarity searches.
    """
    try:
        logger.info(f"Received query: {query}")
        query_lower = query.strip().lower()

        # Step 1: User Initiation
        if "buy a vehicle" in query_lower or "vehicle category" in query_lower:
            return {
                "status": "success",
                "response": "Which brand are you interested in?"
            }

        # Step 2: Ask Brand, model, Type, Category
        if "brand" in query_lower:
            brands = df['brand'].unique().tolist()
            return {
                "status": "success",
                "response": f"Available brands are: {', '.join(brands)}. What model do you prefer?"
            }
            
        if "model" in query_lower:
            models = df['model'].unique().tolist()
            return {
                "status": "success",
                "response": f"Available models are: {', '.join(models)}. What type of vehicle are you looking for? (e.g., sedan, SUV, hatchback)"
            }
            
        if "type" in query_lower:
            types = df['type'].unique().tolist()
            return {
                "status": "success",
                "response": f"Available types are: {', '.join(types)}. What category do you prefer? (e.g., luxury, economy, sports)"
            }
            
        if "category" in query_lower:
            categories = df['category'].unique().tolist()
            return {
                "status": "success",
                "response": f"Available categories are: {', '.join(categories)}. What is your preferred fuel type?"
            }
            
        # Step 3: Ask Fuel Type
        if "fuel_type" in query_lower:
            fuel_types = df['fuel_type'].unique().tolist()
            return {
                "status": "success",
                "response": f"Available fuel types are: {', '.join(fuel_types)}. What is your budget range?"
            }

        # Step 4: Ask Budget
        if "budget" in query_lower:
            try:
                price_limit = int(query_lower.split("budget")[-1].strip().split()[0].replace("$", "").replace(",", ""))
                filtered_df = df[df["price"] <= price_limit]
                if filtered_df.empty:
                    return {
                        "status": "success",
                        "response": "No vehicles match your budget. Would you like to adjust your criteria?"
                    }

                vehicles = []
                for _, row in filtered_df.iterrows():
                    vehicles.append({
                        "Vehicle": f"{row['brand']} {row['model']} {row['type']} {row['category']}",
                        "Price": row['price'],
                        "Year": row['year'],
                        "Fuel Type": row['fuel_type'],
                        "Mileage": row['mileage']
                    })

                return {
                    "status": "success",
                    "response": "Here are some vehicles matching your preferences:",
                    "vehicles": vehicles[:10]  # Limit to 10 results
                }
            except ValueError:
                return {
                    "status": "error",
                    "response": "Invalid budget format. Please provide a valid number."
                }

        # Step 5: Ask if More Details Needed
        if "more details" in query_lower:
            try:
                # Prompt user to provide details in the correct format
                if "details for" in query_lower:
                    inputs = query_lower.split("details for")[-1].strip().lower().split(",")
                    if len(inputs) == 4:
                        brand, model, vehicle_type, category = [i.strip() for i in inputs]
                        # Filter the DataFrame for the specific vehicle
                        vehicle = df[
                            (df['brand'].str.lower() == brand) &
                            (df['model'].str.lower() == model) &
                            (df['type'].str.lower() == vehicle_type) &
                            (df['category'].str.lower() == category)
                        ].to_dict('records')
                        
                        if vehicle:
                            logger.info(f"Returning vehicle details: {vehicle[0]}")
                            return {
                                "status": "success",
                                "response": "Here is the detailed information for the selected vehicle:",
                                "vehicle_details": vehicle[0]  # Return the first matching record
                            }
                        else:
                            return {
                                "status": "error",
                                "response": "No vehicle found matching the provided details. Please check your input."
                            }
                    else:
                        return {
                            "status": "error",
                            "response": "Invalid input format. Please provide details in the format: brand, model, type, category."
                        }
                else:
                    return {
                        "status": "success",
                        "response": "Please provide the vehicle name (brand, model, type, category) for detailed information."
                    }
            except Exception as e:
                logger.error(f"Error in 'more details' query: {str(e)}")
                return {
                    "status": "error",
                    "response": "An error occurred while processing your request. Please try again."
                }


        # Step 7: Ask Next Action
        if "next action" in query_lower:
            return {
                "status": "success",
                "response": "Would you like to contact the seller, schedule a test drive, or get financing information?"
            }

        # Handle filtering queries
        if "show me" in query_lower or "filter" in query_lower:
            filters = {}
            if "under" in query_lower:
                try:
                    price_limit = int(query_lower.split("under")[-1].strip().split()[0].replace("$", "").replace(",", ""))
                    filters["price"] = lambda x: x <= price_limit
                except ValueError:
                    return {"status": "error", "message": "Invalid price format in the query."}

            if "year" in query_lower:
                try:
                    year_limit = int(query_lower.split("year")[-1].strip().split()[0])
                    filters["year"] = lambda x: x >= year_limit
                except ValueError:
                    return {"status": "error", "message": "Invalid year format in the query."}
                
            if "mileage" in query_lower:
                try:
                    mileage_limit = int(query_lower.split("mileage")[-1].strip().split()[0])
                    filters["mileage"] = lambda x: x >= mileage_limit
                except ValueError:
                    return {"status": "error", "message": "Invalid mileage format in the query."}
                
            

            # Apply filters to the dataset
            filtered_df = df
            for column, condition in filters.items():
                if column in filtered_df.columns:
                    filtered_df = filtered_df[filtered_df[column].apply(condition)]

            # Format the filtered data
            vehicles = []
            for _, row in filtered_df.iterrows():
                vehicles.append({
                    "Vehicle": f"{row['brand']} {row['model']} {row['type']} {row['category']}",
                    "Price": row['price'],
                    "Year": row['year'],
                    "Fuel Type": row['fuel_type'],
                    "Mileage": row['mileage']
                })

            if not vehicles:
                return {"status": "success", "response": "No vehicles match your filters."}

            return {
                "status": "success",
                "response": "Here are some vehicles that match your filters:",
                "vehicles": vehicles[:10]  # Limit to 10 results
            }

        # Perform similarity search for other queries
        results = vector_store.similarity_search(query, k=3)
        if not results:
            return {"status": "error", "message": "No relevant results found. Please refine your query."}

        vehicles = []
        for doc in results:
            vehicle_data = {}
            for line in doc.page_content.split("\n"):
                if ": " in line:
                    key, value = line.split(": ", 1)
                    vehicle_data[key.strip()] = value.strip()

            vehicles.append({
                "Vehicle": f"{vehicle_data.get('Brand', 'N/A')} {vehicle_data.get('Model', 'N/A')} {vehicle_data.get('Type', 'N/A')} {vehicle_data.get('Category', 'N/A')}",
                "Price": vehicle_data.get("Price", "N/A"),
                "Year": vehicle_data.get("Year", "N/A"),
                "Fuel Type": vehicle_data.get("Fuel Type", "N/A"),
                "Mileage": vehicle_data.get("Mileage", "N/A"),
            })

        return {
            "status": "success",
            "response": "Here are some vehicles that match your query:",
            "vehicles": vehicles[:10]
        }

    except Exception as e:
        logger.error(f"Error in handle_rag_query: {str(e)}")
        return {"status": "error", "message": "An error occurred while processing your query. Please try again."}
    
    
    
    

def query_vehicle_data(query):
    """
    Django view function to handle vehicle-related queries.
    Returns structured JSON data for frontend rendering.
    """
    try:
        # Predefined responses for common greetings
        common_responses = {
            # Greetings
            "hi": "Hello! Welcome to the Vehicle Chatbot. How can I assist you today?",
            "hello": "Hi there! Welcome to the Vehicle Chatbot. How can I help you?",
            "hey": "Hey! Looking for a vehicle? I’m here to help!",
            "good morning": "Good morning! How can I assist you with your vehicle needs?",
            "good afternoon": "Good afternoon! Ready to explore some vehicles?",
            "good evening": "Good evening! How can I help you with vehicle options?",
            "welcome": "Welcome to the Vehicle Chatbot! Feel free to ask me about any car or service.",

            # Gratitude
            "thank you": "You're very welcome! Let me know if you have more questions.",
            "thanks": "Anytime! I'm here to help with your vehicle needs.",

            # Farewell
            "bye": "Goodbye! Have a great day and drive safe!",
            "see you": "See you soon! Reach out if you need help with vehicles again.",
            "goodbye": "Goodbye! Wishing you the best on your vehicle journey.",

            # Identity / Bot Role
            "who are you": "I’m your friendly vehicle assistant! I can help you find, compare, and understand cars.",
            "what can you do": "I can help you find vehicles, compare models, estimate prices or EMI, and give specs, features, and seller info!",
            "help": "You can ask me things like:\n- Compare two vehicles\n- Show fuel-efficient cars\n- Price of Toyota Aqua\n- EMI for a car\nTry one!",

            # Miscellaneous
            "how are you": "I'm great! Always ready to help you find your perfect ride 🚗",
            "are you a bot": "Yes, I’m an AI-powered chatbot built to assist with all your vehicle-related questions.",
            "do you sell cars": "I don't sell cars myself, but I can show you detailed listings, prices, features, and seller info.",
            "available cars": "Yes! You can ask me about available cars by brand, year, fuel type, or budget.",
            "need to bye a car": "I can help you with that! Just tell me what you're looking for, and I'll find the best options for you.",
            "i need a bike": "I can help you with that! Just tell me what you're looking for, and I'll find the best options for you.",
        }


        # Normalize the input
        query_lower = query.strip().lower()

        # Handle predefined greetings
        if query_lower in common_responses:
            return {"status": "success", "response": common_responses[query_lower]}

        # Handle RAG-based query
        logger.info(f"Processing query: {query}")
        result = handle_rag_query(query)
        logger.info(f"Query result: {result}")

        # Return the structured response
        return result

    except Exception as e:
        logger.error(f"Error in query_vehicle_data: {str(e)}")
        return {"status": "error", "message": str(e)}








def get_vehicle_table_data():
    """
    Fetches vehicle data and formats it for table display.
    """
    try:
        # Debug: Log the DataFrame
        logger.info("Attempting to load vehicle data from Excel file.")
        logger.info(f"File path: ../vehicles_augmented.xlsx")
        
        # Check if DataFrame is loaded correctly
        if df.empty:
            logger.error("The DataFrame is empty. Please check the Excel file.")
            return {"status": "error", "message": "The vehicle data file is empty or invalid."}
        
        vehicles = []
        for _, row in df.iterrows():
            vehicle = {
                "ID": row.get("id", "N/A"),
                "Brand": row.get("brand", "N/A"),
                "Model": row.get("model", "N/A"),
                "Category": row.get("category", "N/A"),
                "Year": row.get("year", "N/A"),
                "Fuel Type": row.get("fuel_type", "N/A"),
                "Price": row.get("price", "N/A"),
            }
            vehicles.append(vehicle)
        
        logger.info(f"Loaded {len(vehicles)} vehicles.")
        return {"status": "success", "vehicles": vehicles}
    except FileNotFoundError as e:
        logger.error(f"File not found: {str(e)}")
        return {"status": "error", "message": "The vehicle data file was not found."}
    except Exception as e:
        logger.error(f"Error in get_vehicle_table_data: {str(e)}")
        return {"status": "error", "message": "An error occurred while fetching vehicle data."}