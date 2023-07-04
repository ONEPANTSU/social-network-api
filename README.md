![SocialNetworkFastAPI](/res/img/logo.svg)
___

💻 SocialNetworkFastAPI is a simple and efficient RESTful API built using FastAPI for a social networking application. It provides various features to enhance the user experience, including JWT authentication and registration. Users can easily sign up and log in to access the platform's functionalities.

One of the main features of this API is the ability to create, edit, delete, and view posts. Users can share their thoughts, experiences they want with others. Additionally, users can interact with posts by liking or disliking them. However, they can only perform these actions on other users' posts and not on their own.

To ensure a seamless experience for developers, SocialNetworkFastAPI also includes a UI documentation feature powered by Swagger. This documentation makes it easy to understand and explore the available endpoints, request formats, and response structures.

Overall, SocialNetworkFastAPI aims to provide a robust and user-friendly API solution for building social networking applications, enabling developers to focus on implementing the core features of their application without worrying about the complexities of authentication, post management, and user interactions.

## Features
- [X] There are JWT authentication and registration
- [X] There are ability to signup and login
- [X] There are ability to create, edit, delete and view posts
- [X] There are ability to like and dislike other users’ posts but not your own 
- [X] There are a UI Documentation (Swagger) for API

## Endpoints
The API has following endpoints:
1. Auth module:
    + POST /auth/jwt/login
    + POST /auth/jwt/logout
    + POST /auth/registration

2. Feed module:
     + GET /feed/get_post/{post_id}
     + GET /feed/get_reactions/{post_id}
     + GET /feed/get_posts/{user_id}
     + POST /feed/create_post
     + DELETE /feed/delete_post/{post_id}
     + PUT /feed/edit_post/{post_id}
     + PUT /feed/view_post/{post_id}
     + PUT /feed/like_post/{post_id}
     + PUT /feed/dislike_post/{post_id}
     + DELETE /feed/remove_the_reaction/{post_id}

## Installation
1. Clone the repository: 
```
git clone https://github.com/ONEPANTSU/SocialNetworkFastAPI.git
```
2. Install the requirements:
```
pip install -r requirements/requirements.txt
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
7. Use alembic for creating tables:
```python
alembic upgrade head
```  
8. Run the API with your host and port:
```python
uvicorn src.main:app --reload --host <IP> --port <PORT>
``` 
9. The API will be able by link: `http://<IP>:<PORT>`
10. The Swagger will be able by link: `http://<IP>:<PORT>/docs`

## Testing
1. For testing Auth module use: 
```python
pytest -v .\tests\test_auth.py
```
2. For testing Feed module use: 
```python
pytest -v .\tests\test_feed.py
```
