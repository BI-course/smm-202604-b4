param([string]$BaseUrl = 'http://127.0.0.1:5001')
$ErrorActionPreference = 'Stop'
$samples = Get-Content -LiteralPath (Join-Path $PSScriptRoot 'examples.json') -Raw | ConvertFrom-Json
foreach ($sample in $samples.PSObject.Properties) {
    Write-Host "Testing $($sample.Name)"
    Invoke-RestMethod -Method Post -Uri "$($BaseUrl.TrimEnd('/'))/api/v1/models/$($sample.Name)/predictions" -ContentType 'application/json' -Body ($sample.Value | ConvertTo-Json -Depth 6) | ConvertTo-Json -Depth 8
}
