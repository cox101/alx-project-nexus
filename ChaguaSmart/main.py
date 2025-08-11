import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# Define the contents of the .env file
env_contents = """
# Django Settings
SECRET_KEY=your-very-secret-key-change-this-in-production
DEBUG=True
ALLOWED_HOSTS=127.0.0.1,localhost

# PostgreSQL Database Configuration
DB_NAME=chaguasmart_db
DB_USER=chaguasmart_db_user
DB_PASSWORD=hpVI6FKvleBgubB21jG0k7HKfjYbHrci
DB_HOST=dpg-d25666hr0fns73dortt0-a.render.com
DB_PORT=5432

# Full Database URL (alternative format)
DATABASE_URL=postgresql://chaguasmart_db_user:hpVI6FKvleBgubB21jG0k7HKfjYbHrci@dpg-d25666hr0fns73dortt0-a.render.com:5432/chaguasmart_db

# CORS Configuration
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
CORS_ALLOW_CREDENTIALS=True

# JWT Configuration
ACCESS_TOKEN_LIFETIME=60
REFRESH_TOKEN_LIFETIME=1440
""".strip()


with open(".env", "w") as env_file:
    env_file.write(env_contents + "\n")

print(".env file created successfully.")
print("Make sure to:")
print("1. Change the SECRET_KEY before deploying to production")
print("2. Set DEBUG=False in production")
print("3. Update ALLOWED_HOSTS for your production domain")

# Database configuration
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('DB_NAME'),
        'USER': os.getenv('DB_USER'),
        'PASSWORD': os.getenv('DB_PASSWORD'),
        'HOST': os.getenv('DB_HOST'),
        'PORT': os.getenv('DB_PORT'),
    }
}
