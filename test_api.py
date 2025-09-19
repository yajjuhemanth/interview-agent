#!/usr/bin/env python3
"""
Simple test script for Interview Agent API
"""

import requests
import json
import time

BASE_URL = "http://localhost:5000"

def test_health_check():
    """Test the health check endpoint"""
    print("Testing health check...")
    try:
        response = requests.get(f"{BASE_URL}/api/health")
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_generate_questions():
    """Test question generation"""
    print("\nTesting question generation...")
    try:
        data = {
            "job_title": "Python Developer",
            "job_description": "We need a Python developer with Flask experience to build REST APIs",
            "num_questions": 5
        }
        
        response = requests.post(
            f"{BASE_URL}/api/generate-questions",
            headers={"Content-Type": "application/json"},
            json=data
        )
        
        print(f"Status: {response.status_code}")
        if response.status_code == 201:
            result = response.json()
            print(f"Generated questions for: {result['job_title']}")
            questions = json.loads(result['questions'])
            print(f"Number of questions: {len(questions)}")
            for i, q in enumerate(questions[:3]):  # Show first 3 questions
                print(f"  Q{i+1}: {q['question'][:60]}...")
            return result['id']  # Return the ID for further testing
        else:
            print(f"Error: {response.json()}")
            return None
    except Exception as e:
        print(f"Error: {e}")
        return None

def test_get_questions():
    """Test getting all questions"""
    print("\nTesting get all questions...")
    try:
        response = requests.get(f"{BASE_URL}/api/questions?page=1&per_page=5")
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"Total questions: {result['pagination']['total']}")
            print(f"Showing {len(result['questions'])} questions")
            return True
        else:
            print(f"Error: {response.json()}")
            return False
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_get_question_by_id(question_id):
    """Test getting a specific question by ID"""
    if not question_id:
        print("\nSkipping get question by ID test (no question ID)")
        return False
        
    print(f"\nTesting get question by ID: {question_id}")
    try:
        response = requests.get(f"{BASE_URL}/api/questions/{question_id}")
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"Question found: {result['job_title']}")
            return True
        else:
            print(f"Error: {response.json()}")
            return False
    except Exception as e:
        print(f"Error: {e}")
        return False

def main():
    """Run all tests"""
    print("🧪 Starting Interview Agent API Tests")
    print("=" * 50)
    
    # Test health check
    if not test_health_check():
        print("❌ Health check failed. Make sure the server is running.")
        return
    
    print("✅ Health check passed")
    
    # Test question generation
    question_id = test_generate_questions()
    if question_id:
        print("✅ Question generation passed")
    else:
        print("❌ Question generation failed")
    
    # Test getting all questions
    if test_get_questions():
        print("✅ Get all questions passed")
    else:
        print("❌ Get all questions failed")
    
    # Test getting specific question
    if test_get_question_by_id(question_id):
        print("✅ Get question by ID passed")
    else:
        print("❌ Get question by ID failed")
    
    print("\n🎉 Test suite completed!")

if __name__ == "__main__":
    main()