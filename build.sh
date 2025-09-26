#!/usr/bin/env bash
# exit on error
set -o errexit

# Step 1: Upgrade the builder's own tools to the latest versions
pip install --upgrade pip setuptools wheel

# Step 2: Now, with the modern tools, install the project's requirements
pip install -r requirements.txt
