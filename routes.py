from flask import request, jsonify, render_template_string
from app import app, db
from models import InterviewQuestion
from gpt_service import GPTService
import json

# Initialize GPT service
gpt_service = None

def init_gpt_service():
    """Initialize GPT service with error handling"""
    global gpt_service
    try:
        gpt_service = GPTService()
        return True
    except ValueError as e:
        print(f"Warning: {e}")
        return False

# Try to initialize GPT service
gpt_available = init_gpt_service()

@app.route('/')
def home():
    """Home page with simple UI"""
    html_template = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Interview Question Generator</title>
        <style>
            body { font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }
            .form-group { margin-bottom: 15px; }
            label { display: block; margin-bottom: 5px; font-weight: bold; }
            input, textarea { width: 100%; padding: 8px; margin-bottom: 10px; border: 1px solid #ddd; border-radius: 4px; }
            button { background-color: #007bff; color: white; padding: 10px 20px; border: none; border-radius: 4px; cursor: pointer; }
            button:hover { background-color: #0056b3; }
            .result { margin-top: 20px; padding: 15px; border: 1px solid #ddd; border-radius: 4px; background-color: #f9f9f9; }
            .question { margin-bottom: 10px; padding: 10px; border-left: 4px solid #007bff; background-color: white; }
            .error { color: red; }
            .success { color: green; }
        </style>
    </head>
    <body>
        <h1>Interview Question Generator</h1>
        <p>Generate customized interview questions using AI based on job title and description.</p>
        
        <form id="questionForm">
            <div class="form-group">
                <label for="job_title">Job Title:</label>
                <input type="text" id="job_title" name="job_title" required placeholder="e.g., Software Engineer, Data Scientist">
            </div>
            
            <div class="form-group">
                <label for="job_description">Job Description:</label>
                <textarea id="job_description" name="job_description" rows="6" required 
                          placeholder="Enter the job description including requirements, responsibilities, and skills needed..."></textarea>
            </div>
            
            <div class="form-group">
                <label for="num_questions">Number of Questions (1-15):</label>
                <input type="number" id="num_questions" name="num_questions" min="1" max="15" value="10">
            </div>
            
            <button type="submit">Generate Questions</button>
        </form>
        
        <div id="result" class="result" style="display: none;"></div>
        
        <script>
            document.getElementById('questionForm').addEventListener('submit', async function(e) {
                e.preventDefault();
                
                const formData = new FormData(e.target);
                const data = {
                    job_title: formData.get('job_title'),
                    job_description: formData.get('job_description'),
                    num_questions: parseInt(formData.get('num_questions'))
                };
                
                const resultDiv = document.getElementById('result');
                resultDiv.style.display = 'block';
                resultDiv.innerHTML = '<p>Generating questions...</p>';
                
                try {
                    const response = await fetch('/api/generate-questions', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify(data)
                    });
                    
                    const result = await response.json();
                    
                    if (response.ok) {
                        let html = '<h3 class="success">Generated Questions:</h3>';
                        const questions = JSON.parse(result.questions);
                        questions.forEach((q, index) => {
                            html += `<div class="question">
                                <strong>Q${index + 1}:</strong> ${q.question}
                                <br><small><strong>Type:</strong> ${q.type} | <strong>Difficulty:</strong> ${q.difficulty}</small>
                            </div>`;
                        });
                        html += `<p><small>Results saved with ID: ${result.id}</small></p>`;
                        resultDiv.innerHTML = html;
                    } else {
                        resultDiv.innerHTML = `<p class="error">Error: ${result.error}</p>`;
                    }
                } catch (error) {
                    resultDiv.innerHTML = `<p class="error">Error: ${error.message}</p>`;
                }
            });
        </script>
    </body>
    </html>
    """
    return render_template_string(html_template)

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'gpt_available': gpt_available,
        'database': 'connected'
    })

@app.route('/api/generate-questions', methods=['POST'])
def generate_questions():
    """Generate interview questions based on job title and description"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No JSON data provided'}), 400
        
        job_title = data.get('job_title', '').strip()
        job_description = data.get('job_description', '').strip()
        num_questions = data.get('num_questions', 10)
        
        # Validation
        if not job_title:
            return jsonify({'error': 'Job title is required'}), 400
        
        if not job_description:
            return jsonify({'error': 'Job description is required'}), 400
        
        if not isinstance(num_questions, int) or num_questions < 1 or num_questions > 15:
            return jsonify({'error': 'Number of questions must be between 1 and 15'}), 400
        
        # Generate questions
        if gpt_service:
            questions = gpt_service.generate_interview_questions(job_title, job_description, num_questions)
        else:
            return jsonify({'error': 'GPT service not available. Please check OPENAI_API_KEY'}), 503
        
        # Save to database
        questions_json = json.dumps(questions)
        interview_question = InterviewQuestion(
            job_title=job_title,
            job_description=job_description,
            questions=questions_json
        )
        
        db.session.add(interview_question)
        db.session.commit()
        
        return jsonify({
            'id': interview_question.id,
            'job_title': job_title,
            'job_description': job_description,
            'questions': questions_json,
            'created_at': interview_question.created_at.isoformat()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Internal server error: {str(e)}'}), 500

@app.route('/api/questions', methods=['GET'])
def get_all_questions():
    """Get all generated questions with pagination"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        
        if per_page > 100:
            per_page = 100
        
        questions = InterviewQuestion.query.order_by(InterviewQuestion.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        return jsonify({
            'questions': [q.to_dict() for q in questions.items],
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': questions.total,
                'pages': questions.pages,
                'has_next': questions.has_next,
                'has_prev': questions.has_prev
            }
        })
        
    except Exception as e:
        return jsonify({'error': f'Internal server error: {str(e)}'}), 500

@app.route('/api/questions/<int:question_id>', methods=['GET'])
def get_question_by_id(question_id):
    """Get a specific question by ID"""
    try:
        question = InterviewQuestion.query.get_or_404(question_id)
        return jsonify(question.to_dict())
        
    except Exception as e:
        return jsonify({'error': f'Internal server error: {str(e)}'}), 500

@app.route('/api/questions/<int:question_id>', methods=['DELETE'])
def delete_question(question_id):
    """Delete a specific question by ID"""
    try:
        question = InterviewQuestion.query.get_or_404(question_id)
        db.session.delete(question)
        db.session.commit()
        
        return jsonify({'message': 'Question deleted successfully'})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Internal server error: {str(e)}'}), 500

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return jsonify({'error': 'Internal server error'}), 500