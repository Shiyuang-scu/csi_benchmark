#!/usr/bin/env bash
# Build script for Render deployment

set -o errexit  # Exit on error

pip install -r requirements.txt

# Run database migrations
flask db upgrade

echo "Build completed successfully!"
