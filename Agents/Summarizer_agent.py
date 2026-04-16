import requests
import os
import uuid

def get_summarized(news):
    try:
        api_key = 'sk-UaS7kGClzFy6TwO-mzUO_FgkCSv5xsUkceoxEmfNFzQ'
        url = "http://localhost:7860/api/v1/run/b003e1e2-de2c-43f2-bc5e-0c641a8b2ea8"
        headers = {"x-api-key": api_key}
        payload = {
            "output_type": "chat",
            "input_type": "text",
            "input_value": " ".join(news) if isinstance(news, list) else news
        }
        response = requests.post(url, json=payload,headers=headers)
        response.raise_for_status()
        data = response.json()
        summary = data["outputs"][0]["outputs"][0]["results"]["message"]["text"]
        return summary
    except Exception as e:
        print("Error:", e)
        return "⚠️ Could not generate summary"
