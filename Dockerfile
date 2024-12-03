
FROM python:3.8.3-slim

RUN apt-get update \
    && apt-get -y install libpq-dev gcc \
    && pip install --upgrade pip \
    && pip install psycopg2

WORKDIR /app

COPY requirements.txt requirements.txt

RUN pip install --no-cache-dir --default-timeout=100 -r requirements.txt -i https://pypi.python.org/simple

COPY . .

CMD ["python", "app.py", "--host=0.0.0.0", "--port=5000"]




