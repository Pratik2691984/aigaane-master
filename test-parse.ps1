[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$OutputEncoding = [System.Text.Encoding]::UTF8
function Test-AigaaneParse {
    param([string]$Text = "rAjaputraH")
    $body = @{ text = $Text } | ConvertTo-Json -Compress
    Write-Host "`n=== Testing: $Text ===" -ForegroundColor Cyan
    Invoke-RestMethod -Uri "http://localhost:8000/api/v1/aigaane/parse" `
        -Method Post `
        -ContentType "application/json; charset=utf-8" `
        -Body ([System.Text.Encoding]::UTF8.GetBytes($body)) |
        ConvertTo-Json -Depth 10
}
Write-Host "Loaded. Run Test-AigaaneParse 'word'" -ForegroundColor Green
