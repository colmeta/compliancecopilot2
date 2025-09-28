# run.py
from app import create_app

# The application factory returns the configured app instance
app = create_app()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
