# CloudNotes — Cloud Lab Dynamic Website

A small self-hosted Flask website with authentication and a SQLite database. Users can create an account, sign in, save private notes, and delete their own notes.

## Requirements
- Python 3
- pip

## Install and run
```bash
python3 -m pip install -r requirements.txt
python3 app.py
```
Open `http://localhost:8000`.

The application creates `website.db` automatically on first launch.

## Lightsail deployment
Clone this public repository into `/opt/website`, install `requirements.txt`, and run `python3 app.py`. The application listens on `0.0.0.0:8000`, so the Lightsail firewall should allow TCP port 8000 in addition to SSH.
