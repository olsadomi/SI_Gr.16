# Windows setup and troubleshooting

1. Install Git, Python 3.11+, and Docker Desktop.
2. Enable Linux containers in Docker Desktop.
3. Allocate at least 6 GB RAM to Docker when possible.
4. Open PowerShell in the repository root.
5. Copy `.env.example` to `.env` and run the bootstrap script.

Useful checks:

```powershell
git --version
python --version
docker version
docker compose version
```

If port 8888 is occupied, stop the conflicting process before running the experiment. The approved experiment assumes `http://localhost:8888`; changing the port requires updating both `.env` and generated ZAP input.

If `host.docker.internal` cannot be resolved from ZAP, confirm Docker Desktop is using Linux containers. This name is how the ZAP container reaches crAPI through the Windows host.

