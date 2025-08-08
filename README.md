# Fitness Booking API

## Setup Instructions

### 1. Activate Virtual Environment

If you haven't created one yet, create it first:

```bash
python3 -m venv myvenv
```

Activate the virtual environment:

**On macOS/Linux:**
```bash
source myvenv/bin/activate
```

**On Windows:**
```bash
myvenv\Scripts\activate
```

### 2. Install Dependencies

Make sure you have pip updated:
```bash
pip install --upgrade pip
```

Install required packages from requirements.txt:
```bash
pip install -r requirements.txt
```

### 3. Database Setup: Make Migrations and Migrate

Create migrations for all apps:
```bash
python manage.py makemigrations
```

Apply migrations to your database:
```bash
python manage.py migrate
```

### 4. Run Test Cases (Booking app)

To run test cases for the booking app:
```bash
python manage.py test booking
```

### 5. Run the Development Server

Start the Django development server:
```bash
python manage.py runserver
```

The API will be available at:
```
http://127.0.0.1:8000/
```

### 6. Access API Documentation (Swagger UI)

If you have integrated drf-yasg for Swagger, you can access the interactive API docs at:
```
http://127.0.0.1:8000/swagger/
```