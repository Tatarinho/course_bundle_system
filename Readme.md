# Course Bundle System

This application calculates resource bundle quotes for teachers using FastAPI.

## Requirements

- Python 3.10 (Python 3.13+ is recommended)
- [Poetry](https://python-poetry.org/) for dependency management

## Installing Dependencies

Using Poetry, install all required packages by running:

~~~bash
poetry install
~~~

## Running the Application

Start the FastAPI application by executing:

~~~bash
poetry run uvicorn main:app --reload
~~~

## API Documentation

Once the application is running, you can access the API documentation at:

- **Swagger UI**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)  
- **ReDoc**: [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)

## Endpoints

### POST /quotes

**Description**: Calculates quotes for teachers based on the topics they request.  
**Request Body**: A JSON object of type `TeacherRequest` containing a dictionary of topics and their respective resource counts.  
**Response**: A list of `Quote` objects, where each object includes the provider's name and the calculated price.

**Example Request**:
~~~json
{
  "topics": {
    "reading": 20,
    "math": 50,
    "science": 30,
    "history": 15,
    "art": 10
  }
}
~~~

## Testing

To run the unit tests, use the following command:

~~~bash
poetry run pytest
~~~
