"""
Entry point untuk Flask application
Jalankan file ini untuk start server: python run.py
"""

from app import create_app
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Create Flask app instance
app = create_app()

if __name__ == '__main__':
    host = os.getenv('HOST', '0.0.0.0')
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('FLASK_ENV') == 'development'
    
    print(f"🍌 Banana Detection Backend")
    print(f"🚀 Server running on http://{host}:{port}")
    print(f"📝 Environment: {os.getenv('FLASK_ENV', 'production')}")
    print(f"⚙️  Debug mode: {debug}")
    
    app.run(
        host=host,
        port=port,
        debug=debug
    )