#!/usr/bin/env python3
"""
Test script for the LLM-Powered Query Retrieval System
"""

import requests
import json
import time
from typing import Dict, Any

# Configuration
BASE_URL = "http://localhost:8000"
AUTH_TOKEN = "15d8d43a4a6736a9d7c238f8fd1b44c29eaac0098c94a7c6ad802075b77bd355"
HEADERS = {
    "Authorization": f"Bearer {AUTH_TOKEN}",
    "Content-Type": "application/json"
}

def test_health_check():
    """Test the health check endpoint"""
    print("🔍 Testing health check...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            print("✅ Health check passed")
            print(f"Response: {response.json()}")
        else:
            print(f"❌ Health check failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Health check error: {e}")

def test_query_processing(document_url: str, user_query: str) -> Dict[str, Any]:
    """Test the main query processing endpoint"""
    print(f"\n🔍 Testing query: '{user_query}'")
    print(f"📄 Document: {document_url}")
    
    payload = {
        "document_url": document_url,
        "user_query": user_query
    }
    
    try:
        start_time = time.time()
        response = requests.post(
            f"{BASE_URL}/hackrx/run",
            headers=HEADERS,
            json=payload
        )
        processing_time = time.time() - start_time
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Query processed successfully")
            print(f"⏱️  Processing time: {processing_time:.2f}s")
            print(f"🎯 Confidence: {result['matched_clause']['confidence']:.2f}")
            print(f"📍 Location: {result['matched_clause']['location']}")
            print(f"📝 Matched text: {result['matched_clause']['text'][:100]}...")
            print(f"💭 Rationale: {result['decision_rationale']}")
            return result
        else:
            print(f"❌ Query failed: {response.status_code}")
            print(f"Error: {response.text}")
            return {}
            
    except Exception as e:
        print(f"❌ Query error: {e}")
        return {}

def test_statistics():
    """Test the statistics endpoint"""
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

def run_comprehensive_test():
    """Run a comprehensive test with various query types"""
    print("🚀 Starting comprehensive test...")
    
    # Test health check first
    test_health_check()
    
    # Example document URL (you would replace this with a real document)
    document_url = "https://example.com/sample_contract.pdf"
    
    # Test queries for different clause types
    test_queries = [
        "What is the termination clause?",
        "What are the payment terms?",
        "What are the liability limits?",
        "What does the confidentiality clause say?",
        "What are the non-compete restrictions?",
        "What are the intellectual property rights?",
        "What law governs this contract?",
        "How are disputes resolved?",
        "What are the force majeure provisions?"
    ]
    
    results = []
    for query in test_queries:
        result = test_query_processing(document_url, query)
        if result:
            results.append(result)
        time.sleep(1)  # Small delay between requests
    
    # Test statistics
    test_statistics()
    
    # Summary
    print(f"\n📈 Test Summary:")
    print(f"Total queries tested: {len(test_queries)}")
    print(f"Successful responses: {len(results)}")
    if results:
        avg_confidence = sum(r['matched_clause']['confidence'] for r in results) / len(results)
        print(f"Average confidence: {avg_confidence:.3f}")
    
    return results

def test_with_sample_document():
    """Test with a sample document (if available)"""
    print("\n📄 Testing with sample document...")
    
    # This would be a real document URL in practice
    sample_document = "https://example.com/sample_contract.pdf"
    
    # Test a specific query
    result = test_query_processing(sample_document, "What is the termination clause?")
    
    if result:
        print("\n📋 Detailed Result:")
        print(json.dumps(result, indent=2))

def main():
    """Main test function"""
    print("🧪 LLM-Powered Query Retrieval System - Test Suite")
    print("=" * 60)
    
    # Check if server is running
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code != 200:
            print("❌ Server is not responding. Please start the server first:")
            print("   python app.py")
            return
    except:
        print("❌ Cannot connect to server. Please start the server first:")
        print("   python app.py")
        return
    
    # Run tests
    results = run_comprehensive_test()
    
    # Test with sample document
    test_with_sample_document()
    
    print("\n✅ Test suite completed!")

if __name__ == "__main__":
    main() 