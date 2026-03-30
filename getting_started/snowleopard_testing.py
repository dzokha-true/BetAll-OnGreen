from snowleopard import SnowLeopardClient
from dotenv import load_dotenv
import os

load_dotenv()  # Load environment variables from .env file
api_key = os.getenv("SNOW_LEOPARD_API_KEY")
datafile_id = os.getenv("SNOW_LEOPARD_DATAFILE_ID")
# Replace these with your real values from the dashboard
client = SnowLeopardClient(api_key=api_key)

response = client.retrieve(
    datafile_id=datafile_id, 
    user_query="what is the average price of META stock?"
)

print(response.data)