$ErrorActionPreference = "Stop"
\(PROJECT_ID = gcloud config get-value project 2>\)null
if (-not $PROJECT_ID) { throw "No active GCP project found." }
Write-Host "Deploying Track A to $PROJECT_ID..." -ForegroundColor Cyan
gcloud run deploy aigaane-track-a-proxy --source="./track-a/backend" --region="asia-south1" --platform="managed" --ingress="internal-and-cloud-load-balancing" --no-allow-unauthenticated --min-instances=0 --max-instances=10 --memory="512Mi" --cpu=1 --timeout="60s" --concurrency=80 --set-env-vars="^:^CANONICAL_WRITE=FALSE:ALLOWED_ORIGINS=https://aigaane.in:LANGUAGE_MODES=en,sa,both:GEMINI_MODEL_ID=gemini-3.8-flash" --set-secrets="^:^GEMINI_API_KEY=aigaane-gemini-key:latest:API_KEY=aigaane-api-key:latest"
Write-Host "Done!" -ForegroundColor Green
