import logging
from .interaction_flow import handle_interaction
from .recomendation_engine import recommend_vehicle
from .utils import load_vehicle_data

# Configure logger
logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler()],
)

# Load vehicle data
df = load_vehicle_data("./data/vehicles_augmented.xlsx")

# Main query handler
def query_vehicle_data(query, user_id):
    """
    Handles user queries and routes them to the appropriate function.
    """
    try:
        # Route query to interaction flow
        response = handle_interaction(query, user_id, df)
        logger.info(f"Response from handle_interaction: {response}")
        return response
    except Exception as e:
        logger.error(f"Error in query_vehicle_data: {str(e)}")
        return {"status": "error", "message": "An error occurred while processing your query."}