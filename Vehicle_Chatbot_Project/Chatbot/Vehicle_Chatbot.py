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