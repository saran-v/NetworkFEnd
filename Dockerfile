FROM python:3.9-slim-buster

COPY requirements.txt /
RUN pip install --upgrade pip
RUN pip install -r /requirements.txt

ENV PYTHONUNBUFFERED True

WORKDIR /app
COPY . .

#EXPOSE 8080
#CMD python app.py
CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 --timeout 0 app:server
