# PowerShell script to run the E-Commerce Dashboard
Write-Host "Starting E-Commerce Analytics Dashboard..." -ForegroundColor Green
Write-Host ""

# Change to the script directory
Set-Location $PSScriptRoot

# Run Streamlit
streamlit run app.py

# Keep window open if there's an error
if ($LASTEXITCODE -ne 0) {
    Write-Host "`nPress any key to exit..." -ForegroundColor Yellow
    $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
}
