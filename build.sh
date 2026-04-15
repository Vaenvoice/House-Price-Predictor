#!/usr/bin/env bash
# exit on error
set -o errexit

echo "Installing backend dependencies..."
pip install --upgrade pip
pip install -r backend/requirements.txt

echo "Build successful!"
