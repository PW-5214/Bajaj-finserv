#!/usr/bin/env python3
"""
Test script for webhook endpoint
"""

import requests
import json
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:8000/api/v1"
HEADERS = {
    "Authorization": "Bearer 15d8d43a4a6736a9d7c238f8fd1b44c29eaac0098c94a7c6ad802075b77bd355",
    "Content-Type": "application/json"
}

def test_webhook_endpoint():
    """Test the webhook endpoint with sample data"""
    print(f"\n🔗 Testing webhook endpoint: POST {BASE_URL}/webhook")
    
    webhook_payload = {
        "documents": "https://hackrx.blob.core.windows.net/assets/policy.pdf?sv=2023-01-03&st=2025-07-04T09%3A11%3A24Z&se=2027-07-05T09%3A11%3A00Z&sr=b&sp=r&sig=N4a9OU0w0QXO6AOIBiu4bpl7AXvEZogeT%2FjUHNO7HzQ%3D",
        "questions": [
            "What is the grace period for premium payment?",
            "What is the waiting period for pre-existing diseases?",
            "Does this policy cover maternity expenses?"
        ],
        "source": "external_system",
        "timestamp": datetime.now().isoformat()
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/webhook",
            headers=HEADERS,
            json=webhook_payload
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Webhook endpoint working correctly")
            print(f"📊 Status: {result.get('status')}")
            print(f"📝 Processed questions: {result.get('processed_questions')}")
            print(f"⏰ Webhook received at: {result.get('webhook_received_at')}")
            
            print("\n📋 Answers:")
            for i, answer in enumerate(result.get('answers', []), 1):
                print(f"{i}. {answer[:100]}...")
                
            return True
        else:
            print(f"❌ Webhook test failed: {response.status_code}")
            print(f"Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Webhook test error: {e}")
        return False

def test_webhook_validation():
    """Test webhook validation with invalid payload"""
    print(f"\n🔍 Testing webhook validation...")
    
    invalid_payload = {
        "documents": "https://example.com/document.pdf",
        # Missing questions array
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/webhook",
            headers=HEADERS,
            json=invalid_payload
        )
        
        if response.status_code == 400:
            print("✅ Webhook validation working correctly")
            print(f"Expected error: {response.json()}")
            return True
        else:
            print(f"❌ Validation test failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Validation test error: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Webhook Endpoint Testing")
    print("=" * 50)
    
    # Test webhook functionality
    webhook_success = test_webhook_endpoint()
    
    # Test validation
    validation_success = test_webhook_validation()
    
    print("\n📊 Test Summary:")
    print(f"✅ Webhook functionality: {'PASS' if webhook_success else 'FAIL'}")
    print(f"✅ Webhook validation: {'PASS' if validation_success else 'FAIL'}")
    
    if webhook_success and validation_success:
        print("\n🎉 All webhook tests passed!")
    else:
        print("\n⚠️ Some webhook tests failed!") 