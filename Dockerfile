FROM python:3.11-slim

WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

EXPOSE 8000

# Use the correct path to manage.py
CMD cd ChaguaSmart && python manage.py collectstatic --noinput && python manage.py migrate && gunicorn config.wsgi:application