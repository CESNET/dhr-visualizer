FROM python:3.12.9-bookworm
WORKDIR /app
COPY . /app
RUN pip install --no-cache-dir -r requirements.txt
CMD ["gunicorn", "main:app", "-b", "0.0.0.0:8081", "-k", "uvicorn.workers.UvicornWorker", "--workers", "4"]
