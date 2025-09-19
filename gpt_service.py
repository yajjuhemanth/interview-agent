from openai import OpenAI
import os
import json
from typing import List, Dict

class GPTService:
    """Service for generating interview questions using OpenAI GPT"""
    
    def __init__(self):
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable is required")
        self.client = OpenAI(api_key=api_key)
    
    def generate_interview_questions(self, job_title: str, job_description: str, num_questions: int = 10) -> List[Dict[str, str]]:
        """
        Generate interview questions based on job title and description
        
        Args:
            job_title: The job title
            job_description: The job description
            num_questions: Number of questions to generate (default: 10)
        
        Returns:
            List of dictionaries containing questions and their types
        """
        prompt = self._create_prompt(job_title, job_description, num_questions)
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are an expert HR interviewer who creates comprehensive and relevant interview questions."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1500,
                temperature=0.7
            )
            
            content = response.choices[0].message.content
            questions = self._parse_questions(content)
            return questions
            
        except Exception as e:
            print(f"Error generating questions: {str(e)}")
            return self._get_fallback_questions()
    
    def _create_prompt(self, job_title: str, job_description: str, num_questions: int) -> str:
        """Create a prompt for GPT to generate interview questions"""
        return f"""
Generate {num_questions} comprehensive interview questions for the following position:

Job Title: {job_title}
Job Description: {job_description}

Please provide a mix of question types including:
- Technical skills questions
- Behavioral questions  
- Situational questions
- Experience-based questions

Format your response as a JSON array where each question is an object with:
- "question": the actual question text
- "type": the type of question (technical, behavioral, situational, experience)
- "difficulty": difficulty level (easy, medium, hard)

Example format:
[
    {{"question": "Can you describe your experience with...", "type": "experience", "difficulty": "medium"}},
    {{"question": "How would you handle a situation where...", "type": "situational", "difficulty": "hard"}}
]
"""
    
    def _parse_questions(self, content: str) -> List[Dict[str, str]]:
        """Parse the GPT response to extract questions"""
        try:
            # Try to find JSON in the response
            start_idx = content.find('[')
            end_idx = content.rfind(']') + 1
            
            if start_idx != -1 and end_idx != -1:
                json_str = content[start_idx:end_idx]
                questions = json.loads(json_str)
                return questions
            else:
                # Fallback: parse line by line
                return self._parse_questions_fallback(content)
                
        except json.JSONDecodeError:
            return self._parse_questions_fallback(content)
    
    def _parse_questions_fallback(self, content: str) -> List[Dict[str, str]]:
        """Fallback method to parse questions if JSON parsing fails"""
        lines = content.split('\n')
        questions = []
        
        for line in lines:
            line = line.strip()
            if line and ('?' in line or line.startswith(('1.', '2.', '3.', '4.', '5.', '6.', '7.', '8.', '9.', '10.'))):
                # Clean up the line
                if line[0].isdigit():
                    line = line.split('.', 1)[1].strip()
                
                questions.append({
                    "question": line,
                    "type": "general",
                    "difficulty": "medium"
                })
        
        return questions[:10]  # Limit to 10 questions
    
    def _get_fallback_questions(self) -> List[Dict[str, str]]:
        """Provide fallback questions if GPT fails"""
        return [
            {"question": "Tell me about yourself and your background.", "type": "behavioral", "difficulty": "easy"},
            {"question": "Why are you interested in this position?", "type": "behavioral", "difficulty": "easy"},
            {"question": "What are your greatest strengths?", "type": "behavioral", "difficulty": "medium"},
            {"question": "Describe a challenging project you worked on.", "type": "experience", "difficulty": "medium"},
            {"question": "How do you handle working under pressure?", "type": "situational", "difficulty": "medium"},
            {"question": "Where do you see yourself in 5 years?", "type": "behavioral", "difficulty": "easy"},
            {"question": "What motivates you in your work?", "type": "behavioral", "difficulty": "medium"},
            {"question": "Describe a time when you had to learn something new quickly.", "type": "experience", "difficulty": "medium"},
            {"question": "How do you prioritize tasks when you have multiple deadlines?", "type": "situational", "difficulty": "medium"},
            {"question": "Do you have any questions for us?", "type": "general", "difficulty": "easy"}
        ]