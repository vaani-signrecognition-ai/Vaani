# Script to create A-Z folder structure for ISL videos
# Run this in PowerShell from the backend/static/isl_words directory

Write-Host "Creating A-Z folder structure for ISL videos..." -ForegroundColor Green

$letters = "A","B","C","D","E","F","G","H","I","J","K","L","M","N","O","P","Q","R","S","T","U","V","W","X","Y","Z"

$basePath = "c:\Users\Admn\Documents\GitHub\Vaani\backend\static\isl_words"

foreach ($letter in $letters) {
    $folderPath = Join-Path $basePath $letter
    if (-not (Test-Path $folderPath)) {
        New-Item -ItemType Directory -Path $folderPath | Out-Null
        Write-Host "✓ Created folder: $letter" -ForegroundColor Cyan
    } else {
        Write-Host "- Folder exists: $letter" -ForegroundColor Yellow
    }
}

Write-Host "`n✅ Folder structure complete!" -ForegroundColor Green
Write-Host "📁 Location: $basePath" -ForegroundColor White
Write-Host "`nNext steps:" -ForegroundColor Yellow
Write-Host "1. Place your .mp4 videos in corresponding letter folders"
Write-Host "2. Run the Colab notebook to load videos to database"
Write-Host "3. Videos will be accessible via the Sign Dictionary UI"
