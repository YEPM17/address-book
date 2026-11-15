# Deployment Guide

The application is a standard WSGI app with a single writable SQLite file, so it
runs on any small Linux VM or container platform. **No public instance was
deployed for the submitted version** — the optional cloud bonus was not claimed.
This guide is what the author would follow (and what the reviewer can reproduce).

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

### Render free plan

The repository includes `render.yaml` for a one-click Blueprint:

1. Push the repository to GitHub.
2. Render dashboard → **New → Blueprint** → select the repository → **Apply**.
3. Render builds the Dockerfile and gives a URL like
   `https://folio-address-book.onrender.com`.

The free plan has **no persistent disk**: the SQLite file is recreated on every
restart. The Docker `CMD` therefore runs `flask --app app seed-demo` before
gunicorn, which repopulates the 14 demo contacts when the database is empty.
For a real deployment add a paid disk at `/data` and set
`ADDRESSBOOK_DB=/data/addressbook.sqlite3`; the seed step then becomes a no-op.
Free services also sleep after ~15 minutes of inactivity, so the first request
after a pause may take ~30 seconds.

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

## 6. Current deployment (PythonAnywhere, free)

| Item | Value |
| --- | --- |
| Public URL | <https://nannan17.pythonanywhere.com/> |
| Platform | PythonAnywhere Beginner (free) |
| Python | 3.13 |
| Database | SQLite at `/home/nannan17/folio_app/instance/addressbook.sqlite3` |

Because PythonAnywhere free accounts have no SSH access, the app is shipped as a
single `folio_bundle.zip` (project + vendored pure-Python dependencies) and a
small WSGI bootstrap:

```python
# /var/www/nannan17_pythonanywhere_com_wsgi.py (simplified)
HOME = "/home/nannan17"
APP_DIR = os.path.join(HOME, "folio_app")
BUNDLE = os.path.join(HOME, "folio_bundle.zip")
if not os.path.exists(os.path.join(APP_DIR, "app.py")):
    with zipfile.ZipFile(BUNDLE) as archive:
        archive.extractall(APP_DIR)
sys.path.insert(0, APP_DIR)
sys.path.insert(0, os.path.join(APP_DIR, "vendor"))
from app import app as application
```

The WSGI file extracts the bundle on first request, seeds the 14 demo contacts if
the database is empty, and then serves the normal Flask app. To deploy an update:
upload a new bundle, delete `/home/nannan17/folio_app`, and reload the web app.

Free-tier limits: 100 CPU seconds/day, 512 MB disk, one web app, no cron/SSH.
SQLite data persists between restarts; the demo data is recreated only when the
database is empty.