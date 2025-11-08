FROM python:3.11-slim

WORKDIR /app

COPY vol/requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY vol/ .

EXPOSE 5000

CMD ["python", "app.py"]
