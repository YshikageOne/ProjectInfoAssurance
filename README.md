# Laundry Management System

A secure web-based laundry management application built with Flask, SQLite, and Bootstrap.

## System Overview

This system provides a comprehensive solution for laundry businesses to track and manage customer orders. The application offers user authentication, order management, and status tracking in a responsive web interface.

## Security Features

- **Password Hashing**: All user passwords are securely hashed using werkzeug.security before storage
- **JWT Authentication**: JSON Web Tokens used for secure session management
- **Token Expiration**: Tokens automatically expire after a configured time period
- **Authorization Headers**: API endpoints protected with Bearer token validation
- **Form Validation**: Input validation on both client and server side
- **CORS Protection**: Cross-Origin Resource Sharing configured for API security
- **SQL Injection Prevention**: Parameterized queries for all database operations
- **XSS Protection**: Data sanitization before rendering in templates
- **Session Management**: Secure session handling for user state
- **Error Handling**: Secure error responses that don't expose system details
- **HTTPS Support**: Compatible with HTTPS when deployed with proper certificates
- **Route Protection**: Authenticated routes protected via decorators
- **Token Verification**: Complete validation of token integrity and signature

## Development Tools

- Backend: Flask web framework
- Database: SQLite with prepared statements
- Frontend: HTML5, CSS3, JavaScript with Bootstrap 5
- Authentication: JWT (JSON Web Tokens)
- HTTP Tunneling: LocalXpose for development access

## Running the Application

1. Install dependencies: `pip install flask werkzeug pyjwt flask-cors`
2. Ensure SQLite is available
3. Run the application: `python app.py`
4. Access at http://localhost:8000

## Deployment

The application can be deployed using:

- LocalXpose HTTP tunnel for temporary public access
- Apache with mod_wsgi for production environments
- Gunicorn or Waitress for production-grade serving

## Database Structure

- **Users**: Authentication and user management
- **LaundryItems**: Order tracking with status and customer information
