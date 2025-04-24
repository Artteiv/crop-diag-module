# Crop Diagnosis Knowledge Graph Module

A powerful tool for querying crop diagnosis knowledge graphs using LangChain and Neo4j. This module provides an API interface to interact with a knowledge graph containing agricultural and crop disease information.

## Features

- Natural language querying of crop diagnosis knowledge graph
- Integration with LangChain for intelligent query processing
- Neo4j database backend for efficient graph operations
- RESTful API interface
- Environment-based configuration

## Prerequisites

- Python 3.8+
- Neo4j Database (version 5.x)
- OpenAI API key (for LangChain integration)

## Installation

1. Clone the repository:
```bash
git clone [repository-url]
cd crop-diag-module
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Configuration

1. Create a `.env` file in the project root:
```bash
cp .env.example .env
```

2. Edit the `.env` file with your configuration:
```env
# Neo4j Configuration
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=your_password

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
DEBUG=True

# LangChain Configuration
OPENAI_API_KEY=your_openai_api_key
```

Replace the following values:
- `NEO4J_URI`: Your Neo4j database URI
- `NEO4J_USER`: Neo4j username
- `NEO4J_PASSWORD`: Neo4j password
- `OPENAI_API_KEY`: Your OpenAI API key

## Running the Application

1. Start the FastAPI server:
```bash
uvicorn app.main:app --reload
```

2. Access the API documentation:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## API Usage

### Query the Knowledge Graph

```bash
curl -X POST "http://localhost:8000/api/query" \
     -H "Content-Type: application/json" \
     -d '{"question": "What are the symptoms of rice blast disease?"}'
```

## Project Structure

```
crop-diag-module/
├── app/
│   ├── api/          # API routes and endpoints
│   ├── core/         # Core functionality
│   ├── models/       # Data models
│   └── utils/        # Utility functions
├── KG/               # Knowledge Graph data
├── tests/            # Test cases
├── requirements.txt  # Project dependencies
└── .env             # Environment configuration
```

## Development

### Running Tests

```bash
pytest tests/
```

### Code Style

This project follows PEP 8 style guidelines. Use the following command to check code style:

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

uvicorn app.main:app --reload
```

## License

[Add your license information here]

## Contributing

[Add contribution guidelines here]
