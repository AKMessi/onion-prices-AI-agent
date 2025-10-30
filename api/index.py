import os
import json
import io
from flask import Flask, jsonify, send_from_directory, request, send_file
from dotenv import load_dotenv

API_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(API_DIR)
STATIC_ROOT = os.path.join(PROJECT_ROOT, 'static')

def scrape_onion_prices():
    """
    This is a tool that will be used to easily scrape the prices of onion in sangamner, nashik, sinnar, etc.
    """

    from firecrawl import Firecrawl 
    
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
                "prompt": """
                        Extract the latest available onion prices for the following locations: sangamner, lasalgaon, nashik, sinnar. Also include the date.
                        Structure the output as a JSON object with a 'date' key and a 'locations' key.
                        'locations' should be a list of objects.
                        Each object in the 'locations' list must have a 'location' (string) and 'onionDetails' (list) key.
                        'onionDetails' should be a list of objects, each with 'quality' (string), 'maxPrice' (number), and 'minPrice' (number).

                        Example format:
                        {
                        "date": "DD-MM-YYYY",
                        "locations": [
                            {
                            "location": "Sangamner",
                            "onionDetails": [
                                {"quality": "उन्हाळी", "maxPrice": 2000, "minPrice": 200}
                            ]
                            },
                            {
                            "location": "Lasalgaon",
                            "onionDetails": [
                                {"quality": "उन्हाळी", "maxPrice": 2152, "minPrice": 500}
                            ]
                            }
                        ]
                        }
                        """
                        }],
            only_main_content=False,
            timeout=120000
        )
        
    except Exception as e:
        return f"Error: {e}"
    
    return {"onion_prices": onion_prices.json}

def scrape_green_peas_prices():
    """
    This is a tool that will be used to easily scrape the prices of green peas in sangamner, nashik, sinnar, etc.
    """
    
    from firecrawl import Firecrawl

    load_dotenv()
    api_key = os.getenv("FIRECRAWL_API_KEY")
    if not api_key:
        return "Error: FIRECRAWL_API_KEY environment variable not set."
        
    firecrawl = Firecrawl(api_key=api_key)
    
    try:
        green_peas_prices = firecrawl.scrape(
            "https://www.krushikranti.com/bajarbhav/vatana-bajar-bhav-today",
            formats=[{
                "type": "json",
                "prompt": "Extract the latest available max and min prices and quality of green peas in mumbai and kalyan. Also mention the date in the result."
            }],
            only_main_content=False,
            timeout=120000
        )
        
    except Exception as e:
        return f"Error: {e}"
    
    return {"green_peas_prices": green_peas_prices.json}

def summarize(onion, green_peas):
    """
    This tool is for summarizing the prices of onion and green peas using Gemini 2.5 Flash.
    """
    
    from langchain_google_genai import ChatGoogleGenerativeAI

    combined_data = {
        "onion_prices": onion.get("onion_prices", {}),
        "green_peas_prices": green_peas.get("green_peas_prices", {})
    }

    prompt_template = f"""
        System: You are a helpful assistant whose job is to convert raw market data (in JSON format) into a polite, easy-to-understand spoken Marathi script. The script is for an elderly farmer who needs to hear the prices read aloud.

        Task: Convert the following JSON data, which contains prices for both onions and green peas, into a single, natural-sounding Marathi paragraph.

        JSON Data:
        ```json
        {json.dumps(combined_data, ensure_ascii=False, indent=2)}
        ```

        Critical Rules for the Output:
        1.  Language: Must be 100% in Marathi.
        2.  Start: Begin with a polite greeting for a grandmother and the date.
        3.  Context: Clearly state the prices for *both* commodities (कांदा आणि वाटाणा) and that prices are per quintal (प्रति क्विंटल).
        4.  Body: Read out the prices for onions first, then read out the prices for green peas.
        5.  Format: The *entire* response must be a single block of text. Do NOT use bullet points or markdown.

        Marathi Script:
        """
    
    api_key = os.getenv("GOOGLE_API_KEY")
    llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", api_key=api_key)
    result = llm.invoke(prompt_template)

    return {"marathi_script": result.content}

app = Flask(__name__)

@app.route('/')
def index():
    return send_from_directory(PROJECT_ROOT, 'index.html')

@app.route('/get-market-report', methods=['GET'])
def run_report():
    try:
        
        onion_result = scrape_onion_prices()
        peas_result = scrape_green_peas_prices()
        if "Error" in str(onion_result) or "Error" in str(peas_result):
            raise Exception("Scraping error")

        summary_result = summarize(onion=onion_result, green_peas=peas_result)
        script_text = summary_result.get('marathi_script')
        if not script_text:
            raise Exception("Summarization error")
            
        # send script to frontend
        return jsonify({
            'success': True,
            'script': script_text
        })

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/generate-audio')
def generate_audio_endpoint():

    from gtts import gTTS

    script_text = request.args.get('text')

    if not script_text:
        return "Error: No text provided.", 400
        
    try:
        # create an in memory audio
        audio_buffer = io.BytesIO()
        
        # generate tts and save to buffer
        tts = gTTS(text=script_text, lang='mr', slow=False)
        tts.write_to_fp(audio_buffer)
        
        # rewind the buffer
        audio_buffer.seek(0)
        
        # send the buffer
        return send_file(audio_buffer, mimetype='audio/mpeg')
        
    except Exception as e:
        return f"Error during audio generation: {e}", 500
    
@app.route('/static/<path:filename>')
def serve_static(filename):
    return send_from_directory(STATIC_ROOT, filename)