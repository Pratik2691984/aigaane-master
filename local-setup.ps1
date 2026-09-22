$ErrorActionPreference = "Continue"
Write-Host "=== Validating Toolchain ===" -ForegroundColor Cyan
foreach ($tool in @("node", "gcloud", "git", "rustc", "wasm-pack", "docker", "jq")) {
    if (Get-Command $tool -ErrorAction SilentlyContinue) {
        Write-Host "[PASS] $tool found" -ForegroundColor Green
    } else {
        Write-Host "[FAIL] $tool missing" -ForegroundColor Red
    }
}
