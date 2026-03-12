# ArticleHubAPI

A FastAPI application with MongoDB for article management.

## Tech Stack

- **FastAPI** - Modern, fast web framework for building APIs
- **MongoDB** - NoSQL database for data storage
- **Docker** - Containerization for easy deployment

## Quick Start

Make sure you're in the root folder of the project.

### 1. Build and Run with Docker

```bash
docker compose build
docker compose up -d
```

The application will be available at `http://localhost:8000`

### 2. API Documentation

Visit `http://localhost:8000/docs` for interactive API documentation (Swagger UI)

## Running Tests

```bash
# Start the containers first
docker compose up -d

# Run all tests with verbose output
docker compose exec api pytest -v

# Run specific test file
docker compose exec api pytest tests/auth/test_register.py -v

# Run specific test
docker compose exec api pytest tests/auth/test_register.py::test_register_user_success -v