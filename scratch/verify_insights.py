import requests
import json

def test_insights():
    url = "http://localhost:8000/api/predict"
    payload = {
        "area": 1500,
        "rooms": 3,
        "location": "Mumbai",
        "age": 2
    }
    
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
        data = response.json()
        
        print(f"Prediction for {payload['location']}: {data['formatted_price']}")
        print("\nAI Insights:")
        insights = data.get("insights")
        if insights:
            print(f"- Market Score: {insights['market_score']}")
            print(f"- Investment Rating: {insights['investment_rating']} stars")
            print(f"- Market Comparison: {insights['market_comparison']}")
            print(f"- Feature Impact: {insights['feature_impact']}")
            print(f"- Narrative: {insights['narrative']}")
        else:
            print("ERROR: No insights found in response!")
            
    except Exception as e:
        print(f"Request failed: {e}")

if __name__ == "__main__":
    test_insights()
