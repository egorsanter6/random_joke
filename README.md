Random Joke Project

Description:
  This is a Django-based project that allows you to enjoy random jokes via a web
  application. The application runs using Docker.

Requirements:
  Python 3.11.9
  pip (Python package installer)
  Docker & Docker Compose installed on your machine
  PostgreSQL database for storing application data

Installation Guide:
  Step 1. Clone the repository.
    git clone https:github.com/egorsanter6/random_joke.git
    cd random_joke

  Step 2. Set up a virtual environment.
    python -m venv your_venv_name
    source your_venv_name/bin/activate # For Linux/MacOS
    your_venv_name/scripts/activate # For Windows

  Step 3. Install Python dependencies.
    pip install -r requirements.txt

  Step 4. Set up a PostgreSQL database.
    Create a new PostgreSQL database.
    Grant privileges to a user (database and schema)

  Step 5. Configure the .env file.
    Just write parameters of your PostgreSQL database,
    get your SECRET KEY (https://djecrety.ir/), set up allowed hosts
    and choose is DEBUG option (True/False)

  Step 6. Build & run the app.
    write in your terminal in the root directory of the app:
      docker-compose build
      docker-compose up

  Step 7. Final step
    Open your browser and navigate to http://127.0.0.1:8000, http://0.0.0.0:8000, etc
    Congratulations!
    
