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
    Handles the user's query by understanding the question, accessing the dataset,
    processing the data, and returning structured data.
    """
    try:
        # Step 1: Log the query for debugging
        logger.info(f"Received query: {query}")

        # Step 2: Perform similarity search in the FAISS vector store
        results = vector_store.similarity_search(query, k=3)
        if not results:
            logger.warning("No relevant results found in the dataset.")
            return {"status": "error", "message": "No relevant information found for your query."}

        # Step 3: Extract relevant context from the results
        vehicles = []
        for doc in results:
            # Parse the document content into a dictionary
            vehicle_data = {}
            for line in doc.page_content.split("\n"):
                if ": " in line:
                    key, value = line.split(": ", 1)
                    vehicle_data[key.strip()] = value.strip()

            # Add the vehicle data to the list
            vehicles.append({
                "name": f"{vehicle_data.get('Brand', 'N/A')} {vehicle_data.get('Model', 'N/A')} {vehicle_data.get('Type', 'N/A')} {vehicle_data.get('Category', 'N/A')}",
                "details": {
                    "Brand": vehicle_data.get("Brand", "N/A"),
                    "Model": vehicle_data.get("Model", "N/A"),
                    "Year": vehicle_data.get("Year", "N/A"),
                    "Fuel Type": vehicle_data.get("Fuel Type", "N/A"),
                    "Engine Capacity": vehicle_data.get("Engine Capacity", "N/A"),
                    "Transmission": vehicle_data.get("Transmission", "N/A"),
                    "Safety Rating": vehicle_data.get("Safety Rating", "N/A"),
                    "Price": vehicle_data.get("Price", "N/A"),
                    "Mileage": vehicle_data.get("Mileage", "N/A"),
                    "Additional Features": vehicle_data.get("Additional Features", "N/A"),
                }
            })

        # Return the structured data
        return {"status": "success", "vehicles": vehicles}

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
            "hi": "Hello! Welcome to the Vehicle Chatbot. How can I assist you today?",
            "hello": "Hi there! Welcome to the Vehicle Chatbot. How can I help you?",
            "welcome": "Welcome to the Vehicle Chatbot! Feel free to ask me about vehicles.",
        }

        # Normalize the input
        query_lower = query.strip().lower()

        # Handle predefined greetings
        if query_lower in common_responses:
            return {"status": "success", "response": common_responses[query_lower]}

        # Handle RAG-based query
        result = handle_rag_query(query)

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