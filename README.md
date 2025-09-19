# Interview Agent

Agent-based Interview Question Generator using Flask, MySQL, and OpenAI GPT. This application generates customized interview questions based on job titles and descriptions, stores them in a MySQL database, and provides both API and web interface access.

## Features

- 🤖 **AI-Powered Question Generation**: Uses OpenAI GPT to generate relevant interview questions
- 🗄️ **Database Storage**: Stores generated questions in MySQL database
- 🌐 **RESTful API**: Clean API endpoints for integration
- 🖥️ **Simple Web UI**: Basic web interface for testing
- 📝 **Postman Ready**: Includes Postman collection for API testing
- 🔄 **CORS Enabled**: Ready for frontend integration
- 📊 **Pagination Support**: Efficient data retrieval with pagination

## Technology Stack

- **Backend**: Flask (Python)
- **Database**: MySQL
- **AI Service**: OpenAI GPT-3.5-turbo
- **Frontend**: Simple HTML/CSS/JavaScript (included)
- **API Testing**: Postman collection provided

## Prerequisites

- Python 3.8+
- MySQL 5.7+ or MySQL 8.0+
- OpenAI API Key

## Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yajjuhemanth/interview-agent.git
   cd interview-agent
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   cp .env.example .env
   ```
   
   Edit `.env` file with your configuration:
   ```env
   OPENAI_API_KEY=your_openai_api_key_here
   MYSQL_HOST=localhost
   MYSQL_USER=root
   MYSQL_PASSWORD=your_password
   MYSQL_DATABASE=interview_agent
   FLASK_ENV=development
   FLASK_DEBUG=True
   ```

5. **Set up the database**
   ```bash
   python setup_db.py
   ```

6. **Run the application**
   ```bash
   python app.py
   ```

The application will be available at `http://localhost:5000`

## API Endpoints

### Base URL: `http://localhost:5000`

### 1. Health Check
- **GET** `/api/health`
- **Description**: Check if the API is running and GPT service is available
- **Response**: 
  ```json
  {
    "status": "healthy",
    "gpt_available": true,
    "database": "connected"
  }
  ```

### 2. Generate Questions
- **POST** `/api/generate-questions`
- **Description**: Generate interview questions based on job title and description
- **Request Body**:
  ```json
  {
    "job_title": "Software Engineer",
    "job_description": "Looking for a Python developer with Flask experience...",
    "num_questions": 10
  }
  ```
- **Response**:
  ```json
  {
    "id": 1,
    "job_title": "Software Engineer",
    "job_description": "Looking for a Python developer...",
    "questions": "[{\"question\": \"...\", \"type\": \"technical\", \"difficulty\": \"medium\"}]",
    "created_at": "2023-12-01T10:00:00"
  }
  ```

### 3. Get All Questions
- **GET** `/api/questions?page=1&per_page=10`
- **Description**: Get all generated questions with pagination
- **Response**:
  ```json
  {
    "questions": [...],
    "pagination": {
      "page": 1,
      "per_page": 10,
      "total": 25,
      "pages": 3,
      "has_next": true,
      "has_prev": false
    }
  }
  ```

### 4. Get Question by ID
- **GET** `/api/questions/{id}`
- **Description**: Get a specific question by ID

### 5. Delete Question
- **DELETE** `/api/questions/{id}`
- **Description**: Delete a specific question by ID

## Usage

### Web Interface
1. Open `http://localhost:5000` in your browser
2. Enter job title and description
3. Specify number of questions (1-15)
4. Click "Generate Questions"
5. View generated questions with their types and difficulty levels

### API Usage
Import the Postman collection (`postman_collection.json`) to test all API endpoints, or use curl:

```bash
# Generate questions
curl -X POST http://localhost:5000/api/generate-questions \
  -H "Content-Type: application/json" \
  -d '{
    "job_title": "Data Scientist",
    "job_description": "Looking for someone with Python, ML, and statistics background",
    "num_questions": 8
  }'

# Get all questions
curl http://localhost:5000/api/questions?page=1&per_page=5
```

## Project Structure

```
interview-agent/
├── app.py                    # Main Flask application
├── models.py                 # Database models
├── routes.py                 # API routes and web interface
├── gpt_service.py           # OpenAI GPT integration
├── setup_db.py             # Database setup script
├── requirements.txt         # Python dependencies
├── postman_collection.json  # Postman API collection
├── .env.example            # Environment variables template
├── .gitignore              # Git ignore file
└── README.md               # This file
```

## Database Schema

### `interview_questions` table
- `id` (INT, Primary Key): Unique identifier
- `job_title` (VARCHAR(255)): Job title
- `job_description` (TEXT): Job description
- `questions` (TEXT): JSON string of generated questions
- `created_at` (DATETIME): Creation timestamp

## Question Types Generated

The AI generates various types of questions:
- **Technical**: Skills-specific questions
- **Behavioral**: Past behavior and personality questions
- **Situational**: Hypothetical scenario questions
- **Experience**: Work history and project questions

Each question includes:
- Question text
- Type (technical, behavioral, situational, experience)
- Difficulty level (easy, medium, hard)

## Error Handling

The application includes comprehensive error handling:
- Input validation
- Database connection errors
- OpenAI API errors
- Graceful fallback to default questions when GPT is unavailable

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is open source and available under the [MIT License](LICENSE).

## Support

For issues and questions:
1. Check the existing issues on GitHub
2. Create a new issue with detailed information
3. Include logs and environment details

## Future Enhancements

- [ ] React/Flutter frontend
- [ ] User authentication
- [ ] Question categories and tags
- [ ] Export questions to PDF/Word
- [ ] Question difficulty assessment
- [ ] Interview scheduling integration
