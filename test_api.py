#!/usr/bin/env python3
"""
Simple test script for the LLM-Powered Query Retrieval System API
"""

import requests
import json

# Configuration
BASE_URL = "http://localhost:8001"
AUTH_TOKEN = "15d8d43a4a6736a9d7c238f8fd1b44c29eaac0098c94a7c6ad802075b77bd355"
HEADERS = {
    "Authorization": f"Bearer {AUTH_TOKEN}",
    "Content-Type": "application/json"
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

def test_query(query_text):
    """Test the main query endpoint"""
    print(f"\n🔍 Testing query: '{query_text}'")
    
    payload = {
        "document_url": "https://example.com/contract.pdf",
        "user_query": query_text
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
            print(f"🎯 Confidence: {result['matched_clause']['confidence']:.2f}")
            print(f"📍 Location: {result['matched_clause']['location']}")
            print(f"📝 Matched text: {result['matched_clause']['text'][:100]}...")
            print(f"💭 Rationale: {result['decision_rationale']}")
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
    print("🧪 LLM-Powered Query Retrieval System - API Test")
    print("=" * 60)
    
    # Test health check
    test_health()
    
    # Test various queries
    test_queries = [
        "What is the termination clause?",
        "What are the payment terms?",
        "What does the confidentiality clause say?",
        "What are the liability limits?",
        "What are the non-compete restrictions?",
        "What are the intellectual property rights?",
        "How are disputes resolved?",
        "What are the force majeure provisions?",
        "What law governs this contract?"
    ]
    
    results = []
    for query in test_queries:
        result = test_query(query)
        if result:
            results.append(result)
    
    # Test statistics
    test_statistics()
    
    # Summary
    print(f"\n📈 Test Summary:")
    print(f"Total queries tested: {len(test_queries)}")
    print(f"Successful responses: {len(results)}")
    if results:
        avg_confidence = sum(r['matched_clause']['confidence'] for r in results) / len(results)
        print(f"Average confidence: {avg_confidence:.3f}")
    
    print("\n✅ API test completed!")

if __name__ == "__main__":
    main() 