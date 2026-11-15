# Deployment Guide

The application is a standard WSGI app with a single writable SQLite file, so it
runs on any small Linux VM or container platform. **No public instance was
deployed for the submitted version** — the optional cloud bonus was not claimed.
This guide is what the team would follow (and what the reviewer can reproduce).

## 1. Docker (recommended)

```bash
docker build -t folio-address-book .
docker run -d --name folio \
  -p 8000:8000 \
  -v folio-data:/data \
  -e SECRET_KEY="$(openssl rand -hex 32)" \
  folio-address-book
```

Open `http://<server-ip>:8000`. The `folio-data` volume keeps
`/data/addressbook.sqlite3` across container restarts.

`docker-compose.yml` example:

```yaml
services:
  folio:
    build: .
    ports:
      - "8000:8000"
    environment:
      SECRET_KEY: "change-me"
      ADDRESSBOOK_DB: /data/addressbook.sqlite3
    volumes:
      - folio-data:/data
    restart: unless-stopped

volumes:
  folio-data:
```

## 2. Cloud VM (Huawei Cloud / Alibaba Cloud)

1. Create an Ubuntu 22.04 ECS instance with a public IP and open port 80/443 in
   the security group.
2. Install Docker:
   `curl -fsSL https://get.docker.com | sudo sh`
3. Clone the repository and build:
   `git clone <repo-url> && cd address-book && sudo docker build -t folio .`
4. Run with a persistent volume:
   `sudo docker run -d --restart=always -p 80:8000 -v /srv/folio:/data -e SECRET_KEY=<random> folio`
5. (Optional) Put Nginx in front for TLS:

   ```nginx
   server {
       listen 80;
       server_name your.domain;
       location / {
           proxy_pass http://127.0.0.1:8000;
           proxy_set_header Host $host;
           proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
       }
   }
   ```

6. Verify `curl http://<server-ip>/api/health` returns `{"status":"ok"}`.

## 3. Render / Railway (PaaS)

- New **Web Service** → connect the GitHub repository.
- Build command: `pip install -r requirements.txt`
- Start command: `gunicorn --workers 2 --bind 0.0.0.0:$PORT app:app`
- Add a **persistent disk** mounted at `/var/data` and set
  `ADDRESSBOOK_DB=/var/data/addressbook.sqlite3`. Without a disk the SQLite
  file is lost on every deploy.
- Health check path: `/api/health`.

## 4. Environment variables

| Variable | Default | Purpose |
| --- | --- | --- |
| `PORT` | `5000` (dev server) | HTTP port |
| `ADDRESSBOOK_DB` | `instance/addressbook.sqlite3` | SQLite file path |
| `SECRET_KEY` | dev placeholder | Flask signing key — set a random value in production |
| `FLASK_DEBUG` | `0` | never enable in production |

## 5. Production notes

- Run behind gunicorn/uWSGI; never use `python app.py` in production.
- Back up the SQLite file (`sqlite3 .backup` or a volume snapshot).
- SQLite allows one writer at a time; this is fine for a personal address book,
  not for hundreds of concurrent writers. Move to PostgreSQL if that changes.
- The app has no authentication: deploy it on an intranet, behind a VPN, or add
  a login layer before exposing it to the internet.
- Uploads are capped at 8 MB; put a reverse-proxy limit in front as well.