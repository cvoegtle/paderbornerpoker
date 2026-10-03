#!/usr/bin/env bash
set -e

cd "$(dirname "$0")"

gcloud config set project effortpoker
gcloud app deploy app.yaml "$@"

