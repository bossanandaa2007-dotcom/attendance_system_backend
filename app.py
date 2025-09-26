import os
from flask import Flask
from models.database import db
from routes.routes import routes_bp
from dotenv import load_dotenv
import pymysql
from sqlalchemy import text

# Load .env
load_dotenv()

DB_USERNAME = os.getenv("DB_USERNAME")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST", "127.0.0.1")
DB_PORT = int(os.getenv("DB_PORT", 3306))
DB_NAME = os.getenv("DB_NAME")

def create_app():
    app = Flask(__name__)
    from flask_cors import CORS
    CORS(app)
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Step 1: Ensure database exists using pymysql directly
    conn = pymysql.connect(host=DB_HOST, user=DB_USERNAME, password=DB_PASSWORD, port=DB_PORT)
    with conn.cursor() as cursor:
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DB_NAME}")
        print(f"✅ Database `{DB_NAME}` ensured!")
    conn.commit()
    conn.close()

    # Step 2: Configure SQLAlchemy with the actual database
    app.config['SQLALCHEMY_DATABASE_URI'] = f"mysql+pymysql://{DB_USERNAME}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

    # Step 3: Initialize db **only once**
    db.init_app(app)

    # Register routes
    app.register_blueprint(routes_bp)

    # Step 4: Create tables if not exist
    with app.app_context():
        db.create_all()
        print("✅ Database tables ready!")

    return app

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)
