import os
from dotenv import load_dotenv
from snowleopard import SnowLeopardClient

load_dotenv()

def query_market_data(user_query: str):
    """
    Takes a frontend prompt, queries Snow Leopard, 
    and returns a clean dictionary for the UI.
    """
    api_key = os.getenv("SNOW_LEOPARD_API_KEY")
    datafile_id = os.getenv("SNOW_LEOPARD_DATAFILE_ID_TICKER")
    
    client = SnowLeopardClient(api_key=api_key)
    
    try:
        # Execute the retrieve call
        response = client.retrieve(
            datafile_id=datafile_id, 
            user_query=user_query
        )
        
        # We package the response for the frontend
        # Most queries return 1 schema result, so we take response.data[0]
        if response.data:
            result = response.data[0]
            return {
                "status": "success",
                "query": result.query,
                "explanation": result.querySummary.get('non_technical_explanation', ""),
                "technical_details": result.querySummary.get('technical_details', ""),
                "data": result.rows,  # This is the list of dicts for your table
            }
        return {"status": "error", "message": "No data found"}

    except Exception as e:
        return {"status": "error", "message": str(e)}

# --- Example of how the Orchestrator uses this ---
if __name__ == "__main__":
    # This string would come from your frontend text box
    frontend_prompt = "?"
    
    structured_results = query_market_data(frontend_prompt)
    
    if structured_results["status"] == "success":
        print(f"SQL used: {structured_results['query']}")
        print(f"AI Summary: {structured_results['explanation']}")
        # This 'data' object goes straight into a Frontend Table or Dataframe
        print(f"Rows: {structured_results['data']}")