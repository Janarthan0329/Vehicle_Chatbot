import os
import pandas as pd

def load_vehicle_data(filepath):
    """
    Loads vehicle data from an Excel file.
    """
    try:
        # Get the absolute path
        base_dir = os.path.dirname(os.path.abspath(__file__)) 
        absolute_path = os.path.join(base_dir, filepath)

        # Debugging: Print the absolute path
        print(f"Attempting to load file from: {absolute_path}")

        # Load the Excel file
        df = pd.read_excel(absolute_path)
        df.dropna(inplace=True)
        return df
    except FileNotFoundError:
        raise FileNotFoundError(f"File not found: {absolute_path}")
    except Exception as e:
        raise Exception(f"Error loading vehicle data: {str(e)}")