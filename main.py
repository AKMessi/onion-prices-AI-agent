import os
from firecrawl import Firecrawl
from langchain_google_genai import GoogleGenerativeAI
from langchain.tools import tool
from dotenv import load_dotenv

@tool
def scrape_onion_prices():
    """
    This is a tool that will be used to easily scrape the prices of onion in sangamner, nashik, sinnar, etc.
    """
    load_dotenv()
    api_key = os.getenv("FIRECRAWL_API_KEY")
    if not api_key:
        return "Error: FIRECRAWL_API_KEY environment variable not set."
        
    firecrawl = Firecrawl(api_key=api_key)
    
    try:
        onion_prices = firecrawl.scrape(
            "https://www.krushikranti.com/bajarbhav/kanda-bajar-bhav-today",
            formats=[{
                "type": "json",
                "prompt": "Extract the latest available max and min prices and quality (ex. unhali, laal kanda, etc.) of onion in sangamner, lasalgaon, nashik, sinnar. Also mention the date in the result."
            }],
            only_main_content=False,
            timeout=120000
        )
        
    except Exception as e:
        return f"Error: {e}"
    
    return {"onion_prices": onion_prices}

if __name__ == "__main__":
    result = scrape_onion_prices("")
    print(result)