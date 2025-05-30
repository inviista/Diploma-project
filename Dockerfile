# Use official Python base image
FROM python:3.10-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set working directory inside the container
WORKDIR /app

# Install Python dependencies
COPY requirements.txt /app/
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

RUN apt-get update \
    && apt-get install -y locales \
    && sed -i '/ru_RU.UTF-8/s/^# //g' /etc/locale.gen \
    && locale-gen

# Copy Django project code
COPY . /app/

# Collect static files (optional, only if needed)
RUN python manage.py collectstatic --noinput

# Expose the port Django will run on (if running directly, usually 8000)
EXPOSE 8000

# Default command (can be overridden by docker-compose or CMD)
CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000"]