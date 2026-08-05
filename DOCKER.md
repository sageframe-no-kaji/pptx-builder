# PPTX Builder - Docker Setup

## Quick Start

```bash
# Build and start the web UI
docker compose up -d

# Visit http://localhost:7860
```

That's it! The web interface will be available at `http://localhost:7860`.

---

## Commands

```bash
# Start services
docker compose up -d

# Stop services
docker compose down

# View logs
docker compose logs -f pptx-builder

# Rebuild after code changes
docker compose up -d --build

# Stop and remove everything
docker compose down -v
```

---

## Features

✅ **Web UI** - Simple drag-and-drop interface
✅ **Auto-cleanup** - Temp files purged after 30 days
✅ **No storage needed** - Everything in temp, auto-deleted
✅ **Health checks** - Container auto-restarts if unhealthy
✅ **2GB temp space** - Plenty for processing

---

## Access

- **Local**: http://localhost:7860
- **Network**: http://YOUR-IP:7860

---

## Cleanup Service

The `cleanup` service runs daily to remove files older than 30 days:
- Searches for `pptx_builder_*` temp directories
- Searches for `pptx_pdf_*` temp directories
- Removes anything older than 30 days

---

## Customization

### Configure Limits

The web UI enforces limits via environment variables. Self-hosted deployments have no defaults applied — set these in `docker-compose.yml` to restrict usage:

| Variable | Default | Description |
|---|---|---|
| `PPTX_MAX_FILE_MB` | `50` | Max file size per upload (MB) |
| `PPTX_MAX_FILES` | `100` | Max number of files per batch |
| `PPTX_MAX_DPI` | `600` | Max DPI for PDF conversion |
| `PPTX_MAX_PDF_PAGES` | `0` | Max pages per PDF (`0` = unlimited) |
| `PPTX_MAX_QUALITY` | `100` | Max JPEG quality a visitor may select (`100` = uncapped) |

Example — restricting a public demo:

```yaml
environment:
  - PPTX_MAX_FILE_MB=20
  - PPTX_MAX_FILES=20
  - PPTX_MAX_DPI=300
  - PPTX_MAX_PDF_PAGES=20
  - PPTX_MAX_QUALITY=85
```

See `.env.example` for a copy-paste starting point.

### Configure Output Encoding

These are a different kind of setting: not ceilings on what a visitor may
request, but the defaults the conversion uses when nothing says otherwise. They
are honored by the CLI as well as the web UI.

| Variable | Default | Description |
|---|---|---|
| `PPTX_FORMAT` | `jpeg` | Encoder for PDF pages — `jpeg` or `png` |
| `PPTX_QUALITY` | `85` | JPEG quality, 1–100 |
| `PPTX_DPI` | `200` | Rendering DPI when none is given |

Output size is the product of DPI and encoder. A 43-page deck is roughly 14 MB
at the defaults and roughly 83 MB at `PPTX_FORMAT=png` with 300 DPI.

**On an uncapped deployment**, leaving `PPTX_MAX_DPI=600` and
`PPTX_MAX_QUALITY=100` together lets a visitor generate downloads in the
hundreds of megabytes. Cap at least one of DPI, page count, or quality on any
tier reachable by people you do not know.

---

### Change Port

Edit `docker-compose.yml`:
```yaml
ports:
  - "8080:7860"  # Now accessible at port 8080
```

### Increase Temp Storage

Edit `docker-compose.yml`:
```yaml
tmpfs:
  - /tmp:size=5G,mode=1777  # Increase to 5GB
```

### Change Cleanup Interval

Edit the cleanup service's `sleep` value:
```yaml
sleep 43200;  # Run twice daily (43200 = 12 hours)
```

---

## Troubleshooting

### Container won't start
```bash
docker compose logs pptx-builder
```

### Out of disk space
```bash
# Manual cleanup
docker compose exec pptx-builder sh -c "find /tmp -name 'pptx_*' -mtime +1 -delete"
```

### Port already in use
Change the port in `docker-compose.yml` or stop the conflicting service.

---

## Development

To run locally without Docker:
```bash
pip install -r requirements-web.txt
python app.py
```

Then visit http://localhost:7860
