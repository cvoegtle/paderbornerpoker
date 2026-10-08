#!/usr/bin/env bash
set -e

cd "$(dirname "$0")"

PROJECT_ID="effortpoker"
SERVICE_NAME="effortpoker"
REGION="europe-west1"

echo "Setting Google Cloud Project to $PROJECT_ID..."
gcloud config set project "$PROJECT_ID"

echo "Deploying $SERVICE_NAME to Cloud Run (Region: $REGION)..."
gcloud run deploy "$SERVICE_NAME" \
  --source . \
  --region "$REGION" \
  --allow-unauthenticated \
  --max-instances 1 \
  --concurrency 128 \
  --memory 512Mi \
  --cpu 1 \
  --timeout 60 \
  "$@"
