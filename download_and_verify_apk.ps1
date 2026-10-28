# PowerShell Script: Download & Verify Android APK from GitHub Actions
param(
    [string]$ArtifactName = "Zombi-Apploclips-Release-APK",
    [string]$OutputDir = "c:\coding\game\bin"
)

$ErrorActionPreference = "Stop"

# 1. Fetch GitHub Token from Git Credential Manager
Write-Host "[*] Obtaining GitHub credentials..."
$credOutput = "protocol=https`nhost=github.com`n" | git credential fill
$token = ($credOutput | Where-Object { $_ -match "^password=" }) -replace "^password=", ""
$headers = @{
    "Authorization" = "Bearer $token"
    "Accept" = "application/vnd.github.v3+json"
}

# 2. Get latest artifacts list
Write-Host "[*] Querying GitHub artifacts API..."
$artifactsResp = Invoke-RestMethod -Uri "https://api.github.com/repos/yashahire213-debug/zoombi-game-/actions/artifacts" -Headers $headers
$targetArtifact = $artifactsResp.artifacts | Where-Object { $_.name -eq $ArtifactName } | Select-Object -First 1

if (-not $targetArtifact) {
    Write-Warning "Artifact '$ArtifactName' not found yet. Current artifacts:"
    $artifactsResp.artifacts | Select-Object id, name, size_in_bytes, created_at | Format-Table
    exit 1
}

Write-Host "[+] Found Artifact: $($targetArtifact.name) (ID: $($targetArtifact.id), Size: $([math]::Round($targetArtifact.size_in_bytes/1MB, 2)) MB)"

# 3. Download Artifact ZIP
$zipPath = Join-Path $OutputDir "artifact_$($targetArtifact.id).zip"
if (-not (Test-Path $OutputDir)) { New-Item -ItemType Directory -Path $OutputDir -Force | Out-Null }

Write-Host "[*] Downloading APK artifact archive..."
curl.exe -s -L -H "Authorization: Bearer $token" $targetArtifact.archive_download_url -o $zipPath

if ((Get-Item $zipPath).Length -lt 1000) {
    Write-Error "Downloaded archive is too small or invalid."
}

Write-Host "[+] Unpacking APK into $OutputDir..."
Expand-Archive -Path $zipPath -DestinationPath $OutputDir -Force
Remove-Item -Path $zipPath -Force

# 4. Locate and Verify Compiled APK
$apkFiles = Get-ChildItem -Path $OutputDir -Filter "*.apk"
if ($apkFiles.Count -eq 0) {
    Write-Error "No .apk found in $OutputDir after extraction!"
}

foreach ($apk in $apkFiles) {
    $sizeMB = [math]::Round($apk.Length / 1MB, 2)
    Write-Host ""
    Write-Host "=================================================================" -ForegroundColor Green
    Write-Host "  SUCCESS! ANDROID APK READY FOR INSTALLATION" -ForegroundColor Green
    Write-Host "=================================================================" -ForegroundColor Green
    Write-Host "  File Path:    $($apk.FullName)"
    Write-Host "  Package Size: $sizeMB MB"
    Write-Host "  Last Modified: $($apk.LastWriteTime)"
    Write-Host "=================================================================" -ForegroundColor Green
}
