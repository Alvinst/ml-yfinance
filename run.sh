#!/bin/bash

. .venv/bin/activate

uvicorn main:app --host 0.0.0.0 --port 8000 --no-server-header >> /var/log/uvicorn/access.log 2>&1

