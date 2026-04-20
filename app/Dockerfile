FROM python:3.10-slim

WORKDIR /app

COPY app.py .
COPY train2.py .
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt
RUN python train2.py

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]