from __future__ import annotations

import os
from pathlib import Path
from urllib.parse import quote

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv

load_dotenv(Path(__file__).with_name(".env"))

# Folder to expose
BASE_DIR = Path(os.environ["BASE_DIR"]).resolve()

app = FastAPI(title="LAN File Server")

# Serves files under /files/... (no directory listing by default)
app.mount("/files", StaticFiles(directory=str(BASE_DIR), html=False), name="files")


def safe_join(base: Path, rel: str) -> Path:
    """
    Prevent path traversal. Ensures requested path stays within base.
    """
    # rel comes from URL, could contain .. etc.
    target = (base / rel).resolve()
    if base != target and base not in target.parents:
        raise HTTPException(status_code=404, detail="Not found")
    return target


@app.get("/", response_class=HTMLResponse)
def index():
    return HTMLResponse(
        """<h3>File server for <a href='https://www.corvo-project.eu/'>CorVo project</a></h3>
        <p>Browse: <a href='/browse/'>/browse/</a></p>"""
    )


@app.get("/browse/{path:path}", response_class=HTMLResponse)
@app.get("/browse/", response_class=HTMLResponse)
def browse(path: str = ""):
    """
    Very small directory listing, with links to /files/...
    """
    p = safe_join(BASE_DIR, path)
    if not p.exists():
        raise HTTPException(status_code=404, detail="Not found")

    if p.is_file():
        # redirect-style link (simple)
        rel = p.relative_to(BASE_DIR).as_posix()
        return HTMLResponse(f"<a href='/files/{quote(rel)}'>Download {p.name}</a>")

    # directory listing
    entries = []
    if path:
        parent = "/".join(path.rstrip("/").split("/")[:-1])
        entries.append(f"<li><a href='/browse/{quote(parent)}'>..</a></li>")

    for child in sorted(p.iterdir(), key=lambda x: (x.is_file(), x.name.lower())):
        rel = child.relative_to(BASE_DIR).as_posix()
        if child.is_dir():
            entries.append(
                f"<li>📁 <a href='/browse/{quote(rel)}'>{child.name}/</a></li>"
            )
        else:
            entries.append(
                f"<li>📄 <a href='/files/{quote(rel)}'>{child.name}</a></li>"
            )

    title = f"/{path}" if path else "/"
    html = f"<h3>Index of {title}</h3><ul>{''.join(entries)}</ul>"
    return HTMLResponse(html)
