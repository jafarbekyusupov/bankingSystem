#!/bin/bash
set -e

echo "===== starting postgres ====="
while ! nc -z postgres 5432; do
  sleep 0.1
done
echo "| OK | postgres started ====="

echo "===== INITING DB ====="
python init_db.py
echo "| OK | DB INITTED"

echo " ========== STARTING =========="
exec gunicorn run:app --bind 0.0.0.0:5000 --workers 2
