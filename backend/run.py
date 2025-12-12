"""Run the Flask development server."""
import os
from app import create_app
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Create app
app = create_app(os.environ.get('FLASK_ENV', 'development'))

if __name__ == '__main__':
    app.run(
        host=os.environ.get('FLASK_HOST', '0.0.0.0'),
        port=int(os.environ.get('FLASK_PORT', 5000)),
        debug=app.config['DEBUG']
    )
