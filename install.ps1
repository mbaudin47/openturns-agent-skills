$GeminiDir = "$env:USERPROFILE\.gemini"
$LinkPath = "$GeminiDir\skills"
$TargetPath = "$(Get-Location)\skills"

if (!(Test-Path $GeminiDir)) {
    New-Item -ItemType Directory -Path $GeminiDir | Out-Null
}

if (Test-Path $LinkPath) {
    Remove-Item $LinkPath -Recurse -Force
}

New-Item -ItemType SymbolicLink -Path $LinkPath -Target $TargetPath
Write-Host "Lien symbolique créé : $LinkPath -> $TargetPath"