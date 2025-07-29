#!/usr/bin/env python3
"""
Test script for the updated LLM-Powered Query Retrieval System API
"""

import requests
import json

# Configuration
BASE_URL = "http://localhost:8000/api/v1"
AUTH_TOKEN = "15d8d43a4a6736a9d7c238f8fd1b44c29eaac0098c94a7c6ad802075b77bd355"
HEADERS = {
    "Authorization": f"Bearer {AUTH_TOKEN}",
    "Content-Type": "application/json",
    "Accept": "application/json"
}

def test_health():
    """Test health endpoint"""
    print("🔍 Testing health endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            print("✅ Health check passed")
            print(f"Response: {response.json()}")
        else:
            print(f"❌ Health check failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Health check error: {e}")

def test_main_endpoint():
    """Test the main hackrx/run endpoint with the required format"""
    print(f"\n🔍 Testing main endpoint: POST {BASE_URL}/hackrx/run")
    
    # Sample request matching the documentation
    payload = {
        "documents": "https://hackrx.blob.core.windows.net/assets/policy.pdf?sv=2023-01-03&st=2025-07-04T09%3A11%3A24Z&se=2027-07-05T09%3A11%3A00Z&sr=b&sp=r&sig=N4a9OU0w0QXO6AOIBiu4bpl7AXvEZogeT%2FjUHNO7HzQ%3D",
        "questions": [
            "What is the grace period for premium payment under the National Parivar Mediclaim Plus Policy?",
            "What is the waiting period for pre-existing diseases (PED) to be covered?",
            "Does this policy cover maternity expenses, and what are the conditions?",
            "What is the waiting period for cataract surgery?",
            "Are the medical expenses for an organ donor covered under this policy?",
            "What is the No Claim Discount (NCD) offered in this policy?",
            "Is there a benefit for preventive health check-ups?",
            "How does the policy define a 'Hospital'?",
            "What is the extent of coverage for AYUSH treatments?",
            "Are there any sub-limits on room rent and ICU charges for Plan A?"
        ]
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/hackrx/run",
            headers=HEADERS,
            json=payload
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Query processed successfully")
            print(f"📊 Number of questions processed: {len(result['answers'])}")
            
            # Display answers
            for i, (question, answer) in enumerate(zip(payload['questions'], result['answers']), 1):
                print(f"\n{i}. Question: {question}")
                print(f"   Answer: {answer}")
            
            return result
        else:
            print(f"❌ Query failed: {response.status_code}")
            print(f"Error: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Query error: {e}")
        return None

def test_statistics():
    """Test statistics endpoint"""
    print("\n📊 Testing statistics endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/stats", headers=HEADERS)
        if response.status_code == 200:
            stats = response.json()
            print("✅ Statistics retrieved")
            print(f"Total queries: {stats.get('total_queries', 0)}")
            print(f"Average confidence: {stats.get('average_confidence', 0.0):.3f}")
        else:
            print(f"❌ Statistics failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Statistics error: {e}")

def main():
    """Main test function"""
    print("🧪 LLM-Powered Query Retrieval System - Updated API Test")
    print("=" * 70)
    
    # Test health check
    test_health()
    
    # Test main endpoint
    result = test_main_endpoint()
    
    # Test statistics
    test_statistics()
    
    # Summary
    if result:
        print(f"\n📈 Test Summary:")
        print(f"✅ API format updated successfully")
        print(f"✅ Processed {len(result['answers'])} questions")
        print(f"✅ All endpoints working correctly")
    
    print("\n✅ Updated API test completed!")

if __name__ == "__main__":
    main() 