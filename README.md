# SocialNetworkFastAPI
___

💻 SocialNetworkFastAPI is a simple RESTful API using FastAPI for a social networking application.

## Features
- [X] There are JWT authentication and registration
- [X] There are ability to signup and login
- [X] There are ability to create, edit, delete and view posts
- [X] There are ability to like and dislike other users’ posts but not your own 
- [X] There are a UI Documentation (Swagger) for API

## Installation
1. Clone the repository: 
```
git clone https://github.com/ONEPANTSU/SocialNetworkFastAPI.git
```
2. Install the requirements:
```
pip install -r requirements.txt
```
3. Run the PostgreSQL Server
4. Create database for this project
5. Create environment file `.env` with your settings in the root directory. Example:
```python
DB_HOST=localhost
DB_PORT=5432
DB_NAME=social_network
DB_USER=postgres
DB_PASSWORD=postgres

JWT_SECRET="JWT_SECRET"
USER_MANAGER_SECRET="USER_MANAGER_SECRET"
```
6. Activate the virtual environment of the project
7. Use `alembic upgrade head ` for creating tables
8. Run the API with your host and port:
```
uvicorn main:app --reload --host <IP> --port <PORT>
``` 
9. The API will be able by `http://<IP>:<PORT>`
10. The Swagger will be able by `http://<IP>:<PORT>/docs`

## Testing
1. For testing auth module use: 
```python
pytest -v .\tests\test_auth.py
```
2. For testing feed module use: 
```python
pytest -v .\tests\test_feed.py
```