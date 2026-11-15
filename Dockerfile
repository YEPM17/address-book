FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV ADDRESSBOOK_DB=/data/addressbook.sqlite3
RUN mkdir -p /data
VOLUME ["/data"]

EXPOSE 8000
# On platform free tiers the filesystem is ephemeral: seed the demo book on
# every cold start so the public URL is never empty.  With a mounted disk the
# seed command is a no-op after the first run.
CMD ["sh", "-c", "python -m flask --app app seed-demo && exec gunicorn --workers 2 --bind 0.0.0.0:${PORT:-8000} app:app"]