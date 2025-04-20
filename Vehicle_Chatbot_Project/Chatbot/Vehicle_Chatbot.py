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
    results = vector_store.similarity_search(query, k=3)
    context = "\n".join([doc.page_content for doc in results])

    full_prompt = f"""
You are a helpful vehicle assistant. Based on the provided context, answer the user's question in a clear, organized, and structured format.

Context:
{context}

User Question:
{query}

Please format your response using the following structure:

**Overview**: A brief summary of matching vehicles (e.g., total count, types/models).
**Specifications**:
For each vehicle, list its details using bullet points:
- Brand
- Model
- Year
- Fuel Type
- Engine Capacity
- Transmission
- Safety Rating
- Maintenance Cost
- After Sales Service
- Financing Options
- Insurance Info
- Additional Features
- Warranty
- Seller: name, contact, location
- Make Country
- Imported From

**Price**: List prices per model.

**Seller Information**: Summarize seller details like:
- Name
- Contact Number
- Location

**Important Notes**:
- Use bold section headers.
- Separate each vehicle clearly.
- Use bullet points for easy readability.
- Don’t include raw data from context.
- Ensure clarity and brevity.

Your response should be as close as possible to this structure.
"""

    # Tokenize the input
    inputs = tokenizer(full_prompt, return_tensors="pt", max_length=512, truncation=True)

    # Generate response
    outputs = model.generate(inputs.input_ids, max_length=1024, num_beams=5, early_stopping=True)

    # Decode the response
    response = tokenizer.decode(outputs[0], skip_special_tokens=True)
    return response.strip()




 

def query_vehicle_data(query):
    """
    Django view function to handle vehicle-related queries.
    Converts structured markdown-style response to HTML for pretty frontend rendering.
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
            raw_response = common_responses[query_lower]
        else:
            # Handle RAG-based query
            raw_response = handle_rag_query(query)

        # Convert structured markdown-style text to HTML
        html_response = markdown2.markdown(raw_response)

        return {"status": "success", "response": html_response}

    except Exception as e:
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