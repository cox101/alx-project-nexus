import os

# Define the contents of the .env file
env_contents = """
# Django Settings
SECRET_KEY=your-very-secret-key
DEBUG=True
ALLOWED_HOSTS=127.0.0.1,localhost

# PostgreSQL Render DB
DB_NAME=dpg-d25666hr0fns73dortt0-a
DB_USER=chaguasmart_db
DB_PASSWORD=hpVI6FKvleBgubB21jG0k7HKfjYbHrci
DB_HOST=render.com
DB_PORT=5432
""".strip()

# Write to .env file in project root
with open(".env", "w") as env_file:
    env_file.write(env_contents + "\n")

print("✅ .env file created successfully.")
