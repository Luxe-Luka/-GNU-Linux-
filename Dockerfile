FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY bot_exemple.py .

CMD ["python", "-u", "bot_exemple.py"]
