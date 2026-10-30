# LAN File Server

A small [FastAPI](https://fastapi.tiangolo.com/) app that shares a local folder over HTTP. It serves the files of the [CorVo project](https://www.corvo-project.eu/).

It exposes:

| Route            | Description                                        |
| ---------------- | -------------------------------------------------- |
| `/`              | Landing page with a link to the browser            |
| `/browse/<path>` | Simple HTML directory listing                      |
| `/files/<path>`  | Direct file download (no directory listing)        |

Requests that try to escape the shared folder (e.g. `../`) return `404`.

## Configuration

Set the folder to share in a `.env` file next to `server.py`:

```env
BASE_DIR=/path/to/shared/folder
```

A `BASE_DIR` environment variable, if set, takes precedence over `.env`.

## Running with Docker (recommended)

Docker Compose mounts `./share` read-only into the container and restarts the service automatically after a reboot:

```bash
docker compose up -d --build
```

The server is then available at `http://<host>:8088/`.

To share a different folder, change the `./share` volume in `docker-compose.yml`.

Useful commands:

```bash
docker compose logs -f           # follow logs
docker compose down              # stop
docker compose up -d --build     # rebuild after changing server.py
```

## Running locally

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python -m uvicorn server:app --root-path /files --port 8088 --host 0.0.0.0
```

`--root-path` is for when the app sits behind a reverse proxy that serves it under that prefix. Adjust it, or drop it, to match your setup.
