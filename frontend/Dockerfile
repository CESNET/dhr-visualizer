FROM python:3.12.9-bookworm
WORKDIR /app
COPY . /app
RUN ln -s /data/output /app/output
EXPOSE 8080
CMD ["python", "-m", "http.server", "8080"]
