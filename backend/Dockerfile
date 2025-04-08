FROM python:3.12.9-bookworm
WORKDIR /app
COPY . /app
RUN pip install --no-cache-dir -r requirements.txt
EXPOSE 8081
CMD ["python", "main.py"]
