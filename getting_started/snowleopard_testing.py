from snowleopard import SnowLeopardClient
from dotenv import load_dotenv
import os

load_dotenv()

api_key = os.getenv("SNOW_LEOPARD_API_KEY")
datafile_id = os.getenv("SNOW_LEOPARD_DATAFILE_ID")

client = SnowLeopardClient(api_key=api_key)

# 1. Using .retrieve() specifically for structured data
response = client.retrieve(
    datafile_id=datafile_id, 
    user_query="what is the average price of META stock?"
)

# 2. Accessing the results
# response.data is a list of SchemaData objects
for result in response.data:
    print(f"--- Query Result for {result.schemaId} ---")
    print(f"SQL Generated: {result.query}")
    print(f"Technical Summary: {result.querySummary['technical_details']}")
    print(f"Data Rows: {result.rows}")
    print("-" * 30)