#!/usr/bin/env python3
"""
Demo script to showcase the Interview Agent functionality
This script demonstrates the core features without requiring database setup
"""

import json
import sys
import os

# Add current directory to path to import modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def demo_gpt_service():
    """Demonstrate GPT service functionality with mock data"""
    print("🤖 Interview Agent Demo")
    print("=" * 50)
    
    # Mock GPT service for demo purposes
    class MockGPTService:
        def generate_interview_questions(self, job_title, job_description, num_questions=10):
            """Generate mock interview questions"""
            base_questions = [
                {"question": f"Can you tell me about your experience with {job_title.lower()} roles?", "type": "experience", "difficulty": "easy"},
                {"question": f"What specific skills make you a good fit for this {job_title} position?", "type": "technical", "difficulty": "medium"},
                {"question": "Describe a challenging project you worked on and how you overcame obstacles.", "type": "behavioral", "difficulty": "medium"},
                {"question": "How do you stay updated with the latest technologies and industry trends?", "type": "behavioral", "difficulty": "easy"},
                {"question": f"Given the job requirements, how would you approach solving complex problems in this {job_title} role?", "type": "situational", "difficulty": "hard"},
                {"question": "Tell me about a time when you had to work with a difficult team member.", "type": "behavioral", "difficulty": "medium"},
                {"question": "What are your salary expectations for this position?", "type": "general", "difficulty": "easy"},
                {"question": "How do you prioritize tasks when working on multiple projects simultaneously?", "type": "situational", "difficulty": "medium"},
                {"question": "What questions do you have about our company culture and this role?", "type": "general", "difficulty": "easy"},
                {"question": f"Can you walk me through how you would design a solution for a typical {job_title.lower()} challenge?", "type": "technical", "difficulty": "hard"}
            ]
            
            # Customize questions based on job description keywords
            if "python" in job_description.lower():
                base_questions.append({"question": "What Python frameworks have you worked with and which do you prefer?", "type": "technical", "difficulty": "medium"})
            if "api" in job_description.lower():
                base_questions.append({"question": "How do you approach API design and what best practices do you follow?", "type": "technical", "difficulty": "medium"})
            if "database" in job_description.lower():
                base_questions.append({"question": "What database technologies have you used and how do you optimize queries?", "type": "technical", "difficulty": "medium"})
            
            return base_questions[:num_questions]
    
    # Demo data
    job_title = "Senior Software Engineer"
    job_description = """
    We are seeking a Senior Software Engineer to join our dynamic team. The ideal candidate will have:
    - 5+ years of experience in Python development
    - Strong experience with Flask/Django frameworks
    - Experience with REST API design and implementation
    - Knowledge of database design and optimization
    - Experience with cloud platforms (AWS/GCP/Azure)
    - Strong problem-solving skills and ability to work in an agile environment
    """
    
    print(f"📋 Job Title: {job_title}")
    print(f"📝 Job Description: {job_description.strip()}")
    print()
    
    # Generate questions
    mock_service = MockGPTService()
    questions = mock_service.generate_interview_questions(job_title, job_description, 8)
    
    print(f"🔮 Generated {len(questions)} Interview Questions:")
    print("=" * 50)
    
    for i, q in enumerate(questions, 1):
        print(f"\n{i}. {q['question']}")
        print(f"   Type: {q['type'].title()} | Difficulty: {q['difficulty'].title()}")
    
    print("\n" + "=" * 50)
    print("✅ Demo completed successfully!")
    print("\nTo use the full application:")
    print("1. Set up your environment variables (.env file)")
    print("2. Install dependencies: pip install -r requirements.txt")
    print("3. Set up database: python setup_db.py")
    print("4. Run application: python app.py")
    print("5. Access web interface: http://localhost:5000")
    print("6. Test API: python test_api.py")

def demo_api_structure():
    """Show the API structure and example responses"""
    print("\n🌐 API Structure Demo")
    print("=" * 50)
    
    api_examples = {
        "POST /api/generate-questions": {
            "description": "Generate interview questions",
            "request": {
                "job_title": "Data Scientist",
                "job_description": "Looking for a data scientist with Python and ML experience",
                "num_questions": 5
            },
            "response": {
                "id": 1,
                "job_title": "Data Scientist",
                "questions": "[{\"question\": \"What ML algorithms have you implemented?\", \"type\": \"technical\", \"difficulty\": \"medium\"}]",
                "created_at": "2023-12-01T10:00:00"
            }
        },
        "GET /api/questions": {
            "description": "Get all questions with pagination",
            "response": {
                "questions": [{"id": 1, "job_title": "Data Scientist", "created_at": "2023-12-01T10:00:00"}],
                "pagination": {"page": 1, "per_page": 10, "total": 1, "pages": 1}
            }
        },
        "GET /api/health": {
            "description": "Health check endpoint",
            "response": {
                "status": "healthy",
                "gpt_available": True,
                "database": "connected"
            }
        }
    }
    
    for endpoint, data in api_examples.items():
        print(f"\n{endpoint}")
        print(f"Description: {data['description']}")
        if 'request' in data:
            print("Request Example:")
            print(json.dumps(data['request'], indent=2))
        print("Response Example:")
        print(json.dumps(data['response'], indent=2))
        print("-" * 30)

if __name__ == "__main__":
    demo_gpt_service()
    demo_api_structure()