FROM python:3.11-slim

# Set working directory to the Django project directory
WORKDIR /app

# Copy requirements file
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project code
COPY . .

EXPOSE 8000

# Run Django commands directly (no CD needed)
CMD python manage.py collectstatic --noinput && python manage.py migrate && gunicorn config.wsgi:application