FROM python:3.10-slim
RUN mkdir /app
COPY requirements.txt /app
WORKDIR /app
RUN pip3 install -r /app/requirements.txt --no-cache-dir
COPY . /app
RUN python manage.py collectstatic --noinput
#CMD gunicorn config.wsgi:application --bind 0.0.0.0:8000