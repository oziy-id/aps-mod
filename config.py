import os

class Config:
    # --- BASIC SETTINGS ---
    SECRET_KEY = 'ozi-secret-key-ganti-nanti'
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    
    # --- DATABASE ---
    # Menggunakan SQLite untuk kemudahan, bisa diganti PostgreSQL nanti
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(BASE_DIR, 'apsmod.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # --- UPLOAD SETTINGS ---
    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'static/uploads')
    ALLOWED_EXTENSIONS = {'apk', 'xapk', 'zip'}
    MAX_CONTENT_LENGTH = 100 * 1024 * 1024  # Max upload 100MB

    # --- META INFO ---
    APP_NAME = "APSMod"
    ADMIN_USERNAME = "admin"
    ADMIN_PASSWORD = "password123" # Di production gunakan hash!
    
    # --- THEME COLORS (Untuk referensi backend) ---
    COLOR_PRIMARY = "#1B5E20"
    COLOR_SECONDARY = "#4CAF50"

    # --- AUTO EXTRACT SETTINGS ---
    AUTO_EXTRACT_METADATA = True
