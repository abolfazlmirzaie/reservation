FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir --upgrade pip \
    --timeout 100 --retries 10 \
    -i https://mirror-pypi.runflare.com/simple \
    --trusted-host mirror-pypi.runflare.com \
    && pip install --no-cache-dir --timeout 100 --retries 10 \
    -i https://mirror-pypi.runflare.com/simple \
    --trusted-host mirror-pypi.runflare.com \
    -r requirements.txt

COPY . .

RUN chmod +x /app/entrypoint.sh

EXPOSE 8000

ENTRYPOINT ["/app/entrypoint.sh"]

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]