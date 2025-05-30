# Secure File Sharing Backend API

Secure file sharing backend API with user authentication and encrypted download links.

---

## Overview

This project implements a secure file-sharing system with two types of users:

- **Operation User**: Can log in and upload files (only `.pptx`, `.docx`, and `.xlsx` formats allowed).
- **Client User**: Can sign up, verify email, log in, list uploaded files, and download files via secure encrypted URLs.

---

## Features

- User authentication for both Operation and Client users using JWT.
- Role-based access control (Operation vs Client).
- File upload restricted to specific file types (`pptx`, `docx`, `xlsx`).
- Email verification flow for Client users with encrypted verification URLs.
- Secure encrypted URL generation for file downloads accessible only to authorized Client users.
- RESTful API design for all functionalities.
- Secure storage of files locally or via cloud storage (configurable).
- Token-based API authentication.

---

## Technologies Used

- Python (choose your framework: Flask, FastAPI, or Django)
- Database: PostgreSQL / MySQL / MongoDB (configurable)
- JWT (JSON Web Tokens) for authentication and authorization
- SMTP email service for sending verification emails
- File storage on local disk or cloud (e.g., AWS S3, Google Cloud Storage)
- Environment variables management (e.g., with `python-dotenv`)

---

## API Endpoints

### Operation User Endpoints

| Method | Endpoint    | Description                         | Access           |
|--------|-------------|-----------------------------------|------------------|
| POST   | `/login`    | Login for operation users          | Operation Users  |
| POST   | `/upload`   | Upload files (pptx, docx, xlsx)   | Operation Users  |

---

### Client User Endpoints

| Method | Endpoint             | Description                            | Access       |
|--------|----------------------|------------------------------------|--------------|
| POST   | `/signup`            | Register new client user (returns verification email) | Public       |
| GET    | `/verify-email`      | Verify client user email via token   | Public       |
| POST   | `/login`             | Login for client users                | Client Users |
| GET    | `/files`             | List all uploaded files               | Client Users |
| GET    | `/download-file/{id}`| Get secure download link for a file  | Client Users |

---

## Getting Started: How to Run Locally

### Prerequisites

- Python 3.8+
- Git
- Database (PostgreSQL / MySQL / MongoDB) installed and running
- SMTP server credentials (for sending verification emails)

---

### Steps

1. **Clone the repository**

   ```bash
   git clone https://github.com/yourusername/secure-file-sharing.git
   cd secure-file-sharing
