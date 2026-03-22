FROM python:3.11-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8000

# Command gets overridden by docker-compose, this is just a default
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
