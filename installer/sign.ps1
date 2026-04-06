Write-Host "Starting code signing process..."

$thumbprint = "F54ED66C29666B0315EBB1940CD04234544B1238"

$timestampUrl = $env:WINDOWS_SIGN_TIMESTAMP_URL
if (-not $timestampUrl) { $timestampUrl = "http://timestamp.digicert.com" }

$signtool = "C:\Program Files (x86)\Windows Kits\10\bin\10.0.26100.0\x64\signtool.exe"

function Sign-File($file) {
    if (Test-Path $file) {
        & $signtool sign /sha1 $thumbprint /fd sha256 /tr $timestampUrl /td sha256 $file
        if ($LASTEXITCODE -eq 0) {
            Write-Host "Successfully signed: $file"
        } else {
            Write-Host "Failed to sign: $file"
            exit 1
        }
    } else {
        Write-Host "File not found: $file"
        exit 1
    }
}

# Find the installer exe in the Output directory
$installerDir = Join-Path $PSScriptRoot "Output"
$exeFiles = Get-ChildItem -Path $installerDir -Filter "winactor-for-wmc-setup-v*.exe" -ErrorAction SilentlyContinue

if (-not $exeFiles) {
    Write-Host "No installer found in $installerDir"
    Write-Host "Run the InnoSetup build first, or download the artifact from GitHub Actions."
    exit 1
}

foreach ($exe in $exeFiles) {
    Sign-File $exe.FullName
}

Write-Host "Code signing process completed."
