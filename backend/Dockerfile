FROM python:3.12.9-bookworm
#
#ENV CELERY_BROKER_URL redis://redis:6379/0
#ENV CELERY_RESULT_BACKEND redis://redis:6379/0
ENV C_FORCE_ROOT true

WORKDIR /app
COPY . /app
RUN pip install --no-cache-dir -r requirements.txt
CMD ["python", "main.py"]
