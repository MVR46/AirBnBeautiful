"""Simple test script to verify API endpoints."""

import requests
import json

BASE_URL = "http://localhost:8000"


def test_search():
    """Test NLP search endpoint."""
    print("\n" + "="*60)
    print("Testing NLP Search")
    print("="*60)
    
    query = "2 guests in Centro under 100 euros with wifi and kitchen"
    print(f"Query: {query}")
    
    response = requests.post(
        f"{BASE_URL}/search",
        json={"query": query}
    )
    
    print(f"Status: {response.status_code}")
    if response.ok:
        data = response.json()
        print(f"\nParsed filters:")
        print(json.dumps(data['parsed_filters'], indent=2))
        print(f"\nFound {len(data['listings'])} listings")
        if data['listings']:
            first = data['listings'][0]
            print(f"\nTop result:")
            print(f"  - {first['title']}")
            print(f"  - €{first['price_per_night']}/night")
            print(f"  - {first['neighborhood']}")
            print(f"  - {len(first['amenities'])} amenities")
    else:
        print(f"Error: {response.text}")


def test_listing_detail():
    """Test listing detail endpoint."""
    print("\n" + "="*60)
    print("Testing Listing Detail")
    print("="*60)
    
    # Get first listing from search
    response = requests.post(
        f"{BASE_URL}/search",
        json={"query": "apartment in Madrid"}
    )
    
    if response.ok and response.json()['listings']:
        listing_id = response.json()['listings'][0]['id']
        print(f"Fetching listing: {listing_id}")
        
        detail_response = requests.get(f"{BASE_URL}/listings/{listing_id}")
        print(f"Status: {detail_response.status_code}")
        
        if detail_response.ok:
            listing = detail_response.json()
            print(f"\nListing: {listing['title']}")
            print(f"Price: €{listing['price_per_night']}/night")
            print(f"Location: {listing['neighborhood']}")
            print(f"Capacity: {listing['guests']} guests, {listing['beds']} beds")


def test_neighborhood_chat():
    """Test RAG neighborhood chat."""
    print("\n" + "="*60)
    print("Testing Neighborhood Chat (RAG)")
    print("="*60)
    
    # Get a listing first
    response = requests.post(
        f"{BASE_URL}/search",
        json={"query": "apartment in Madrid"}
    )
    
    if response.ok and response.json()['listings']:
        listing_id = response.json()['listings'][0]['id']
        neighborhood = response.json()['listings'][0]['neighborhood']
        
        question = "Is it safe at night?"
        print(f"Listing: {listing_id} ({neighborhood})")
        print(f"Question: {question}")
        
        chat_response = requests.post(
            f"{BASE_URL}/neighborhood-chat",
            json={
                "listingId": listing_id,
                "message": question
            }
        )
        
        print(f"Status: {chat_response.status_code}")
        if chat_response.ok:
            print(f"\nReply: {chat_response.json()['reply']}")
        else:
            print(f"Error: {chat_response.text}")


def test_landlord_prefill():
    """Test landlord prefill endpoint."""
    print("\n" + "="*60)
    print("Testing Landlord Prefill")
    print("="*60)
    
    response = requests.get(f"{BASE_URL}/landlord/prefill")
    print(f"Status: {response.status_code}")
    
    if response.ok:
        data = response.json()
        print(f"\nSample listing:")
        print(f"  - {data['title']}")
        print(f"  - {data['neighborhood']}")
        print(f"  - €{data['price_per_night']}/night")
        print(f"  - {len(data['photos'])} selected photos")
        print(f"  - {len(data['all_ready_photos'])} available photos")


def test_price_suggestions():
    """Test price optimization endpoint."""
    print("\n" + "="*60)
    print("Testing Price Suggestions")
    print("="*60)
    
    request_data = {
        "currentAmenities": ["WiFi", "Kitchen"],
        "targetPrice": 120,
        "listingMeta": {
            "guests": 2,
            "beds": 1,
            "neighborhood": "Centro",
            "baths": 1.0
        }
    }
    
    print(f"Current amenities: {request_data['currentAmenities']}")
    print(f"Target price: €{request_data['targetPrice']}")
    
    response = requests.post(
        f"{BASE_URL}/landlord/price-suggestions",
        json=request_data
    )
    
    print(f"Status: {response.status_code}")
    if response.ok:
        data = response.json()
        print(f"\nCurrent estimate: €{data['currentPriceEstimate']:.2f}")
        print(f"Target price: €{data['targetPrice']:.2f}")
        print(f"\nTop 3 feature importances:")
        for feat in data['featureImportance'][:3]:
            print(f"  - {feat['feature']}: {feat['importance']:.3f}")
        print(f"\nRecommended additions:")
        for rec in data['recommendedAdditions'][:3]:
            print(f"  - {rec['amenity']}: +€{rec['estimatedLift']:.2f}")
    else:
        print(f"Error: {response.text}")


def main():
    """Run all tests."""
    print("\n" + "="*60)
    print("AIRBNB ML BACKEND API TESTS")
    print("="*60)
    print(f"Base URL: {BASE_URL}")
    
    try:
        # Health check
        response = requests.get(BASE_URL)
        if not response.ok:
            print("ERROR: Server not running!")
            print("Start the server with: uvicorn main:app --reload")
            return
        
        print("✓ Server is running")
        
        # Run tests
        test_search()
        test_listing_detail()
        test_neighborhood_chat()
        test_landlord_prefill()
        test_price_suggestions()
        
        print("\n" + "="*60)
        print("ALL TESTS COMPLETED")
        print("="*60 + "\n")
        
    except requests.exceptions.ConnectionError:
        print("\nERROR: Cannot connect to server!")
        print("Start the server with: uvicorn main:app --reload")


if __name__ == "__main__":
    main()

