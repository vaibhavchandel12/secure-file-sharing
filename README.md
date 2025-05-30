# secure-file-sharing

Secure file sharing backend API with user authentication and encrypted download links.

## Overview

This project implements a secure file-sharing system with two types of users:  
- **Operation User**: Can log in and upload files (only pptx, docx, and xlsx formats allowed).  
- **Client User**: Can sign up, verify email, log in, list uploaded files, and download files via secure encrypted URLs.

## Features

- User authentication for both Operation and Client users.
- Role-based access control.
- File upload restrictions to specific file types.
- Email verification for Client users with secure encrypted download links.
- Secure URL generation for file downloads, accessible only to authorized Client users.
- RESTful API endpoints.

## Technologies Used

- Python (Flask/FastAPI/Django - specify your choice)
- Database: SQL (e.g., PostgreSQL, MySQL) or NoSQL (e.g., MongoDB)
- JWT for authentication
- Email service for verification
- File storage on local disk or cloud storage (e.g., AWS S3)

## API Endpoints

### Operation User
- `POST /login` - Login for operation users.
- `POST /upload` - Upload pptx, docx, and xlsx files.

### Client User
- `POST /signup` - Register a new client user (returns encrypted verification URL).
- `GET /verify-email` - Verify client user email.
- `POST /login` - Login for client users.
- `GET /files` - List all uploaded files.
- `GET /download-file/{file_id}` - Get secure download link for a file.

## How to Run Locally

1. Clone the repository  
2. Install dependencies using pip
3. Configure database connection settings in `config.py`


