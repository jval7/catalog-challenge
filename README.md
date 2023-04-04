# Catalog API
This is a RESTful API for managing products. It is built using FastAPI, SQLAlchemy, Black, and Pytest.
The architecture of the project is based on Event Driven Architecture (EDA).

## Some architectural decisions:
1. Unit of Work pattern is used to manage the database session.
2. Repository pattern is used to abstract the database layer.
3. Command and event pattern is used to decouple the business logic from the database layer.
4. CQRS pattern is used to separate the read and write models.

## Some design patterns used:
1. strategy pattern is used to implement the different types of message to be send when a product is created\ changed\ deleted.
2. factory pattern is used to create the different types of message to be send when a product is created\ changed\ deleted.


## Admin Explanation
There are 3 types of users in the system:
1. Admin
2. Super Admin
3. Anonymous

- The admin and super admin can create, update, and delete products.
- The Super Admin can create, update, and delete users.
- The Anonymous user can only view products.
- The viewed products are stored in the database in the table `product_seen`.


## Getting Started
To get started with this project, follow these steps:

1. run `pip install -r requirements.txt` to install the required packages.
2. run ``python db_script.py`` to create a test database with example data.
3. run `uvicorn main:app --reload` to start the server.
4. navigate to `http://localhost:8000/docs` to view the API documentation.
5. log in using the following credentials:
    - username: `super@test.com`
    - password: `password1`
6. The tests can be run using `pytest` command, example: `pytest tests`

The project is configured to use a SQLite database by default. If you'd like to use a different database, you can update the database URI in the config.py file using environment variables.

## Next Steps
2. Add a Dockerfile to the project to containerize the application.
3. Add a CI/CD pipeline to the project.
4. Implement a message broker to allow for asynchronous communication between the services.
