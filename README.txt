## Project Requirements
- Python 3.10+
- PostgreSQL 14+
- Redis

## PostgreSQL Information
- **User:** postgres  
- **Password:** "YOUR_PASSWORD"  
- **Host:** localhost  
- **Port:** 5432  
- **Schema:** Pets_store  

## Database Setup
Start PostgreSQL using **pgAdmin 4** and create the connection using the following line:

    engine = create_engine(
        'postgresql://postgres:YOUR_PASSWORD@localhost:5432/postgres'
    )

## Run the Server
To start the API server, run:

    python pets_api.py

## API Testing
Use **Postman** to test all API endpoints.

## Main Endpoints, Supported Methods, and Core Functionality

### Authentication
- **POST /register** – Create a new user and obtain an authentication token  
- **POST /login** – Log in and obtain an authentication token  
- **GET /me** – View authenticated user information  

### Products
- **GET /products/list**  
- **POST /products/new_product** *(admin only)*  
- **POST /products/modification** *(admin only)*  
- **DELETE /products/delete** *(admin only)*  

### Cart
- **POST /cart/add**  
- **DELETE /cart/remove/product**  
- **POST /cart/modify/amount**  
- **GET /cart**  

### Invoices
- **POST /complete/purchase**  
- **GET /me/invoices**  
- **GET /me/invoices/detail**  
- **POST /invoices/modification** *(admin only)*  
- **DELETE /invoices/delete** *(admin only)*  
