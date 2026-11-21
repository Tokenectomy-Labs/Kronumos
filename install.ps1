# Kronumos Core CLI - Windows Automated Native Installer (v1.3.0)
# Powered by Tokenectomy Labs (https://kronumos.com)

$ErrorActionPreference = "Stop"

# Ensure UTF-8 I/O on Windows PowerShell 5.1+ / CMD so Unicode UI renders cleanly
try {
    $utf8NoBom = New-Object System.Text.UTF8Encoding($false)
    $OutputEncoding = $utf8NoBom
    [Console]::OutputEncoding = $utf8NoBom
    [Console]::InputEncoding = $utf8NoBom
} catch {}

$Tag = "v1.3.0"

Write-Host ""
Write-Host "  ┌─ KRONUMOS CORE · WINDOWS INSTALLER $Tag" -ForegroundColor White
Write-Host "  │  Autonomous Software Engineering CLI (Native x64 · No WSL)" -ForegroundColor DarkGray
Write-Host "  └───────────────────────────────────────────────────────────" -ForegroundColor DarkGray
Write-Host ""

$arch = $env:PROCESSOR_ARCHITECTURE
if ($env:PROCESSOR_ARCHITEW6432) {
    $arch = $env:PROCESSOR_ARCHITEW6432
}
if ($arch -ne "AMD64") {
    Write-Host "  ▲ Pre-compiled native binaries are currently published for windows-amd64 and linux-amd64 (detected: $arch)." -ForegroundColor Red
    Write-Host "    ↳ ARM64 & macOS builds are in active release staging — track status at https://kronumos.com/changelog" -ForegroundColor DarkGray
    exit 1
}

Write-Host "  ◆ Preparing install path..." -ForegroundColor White
$installDir = "$env:LOCALAPPDATA\Programs\kronumos\bin"
if (-not (Test-Path $installDir)) {
    New-Item -ItemType Directory -Force -Path $installDir | Out-Null
}
Write-Host "    ↳ Target: $installDir" -ForegroundColor DarkGray

$exePath = Join-Path $installDir "kronumos.exe"
$tmpExe = Join-Path $installDir "kronumos.exe.download"
$tmpSha = Join-Path $installDir "kronumos.exe.sha256"
$oldExe = Join-Path $installDir "kronumos.exe.old"
$directPagesUrl = "https://kronumos.com/kronumos-windows-amd64.exe"
$primaryUrl = "https://dl.kronumos.com/kronumos-windows-amd64.exe"
$pagesUrl = "https://kronumos.com/releases/kronumos-windows-amd64.exe"

Write-Host "  ◆ Downloading Kronumos Core CLI ($Tag) native Windows binary..." -ForegroundColor White

try {
    [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12 -bor [Net.SecurityProtocolType]::Tls13
} catch {
    [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
}

$downloaded = $false
$downloadedUrl = ""
$urls = @($directPagesUrl, $primaryUrl, $pagesUrl)
$hasCurlExe = Get-Command "curl.exe" -ErrorAction SilentlyContinue

foreach ($url in $urls) {
    try {
        if (Test-Path $tmpExe) { Remove-Item -Path $tmpExe -Force -ErrorAction SilentlyContinue }
        if ($hasCurlExe) {
            & curl.exe -fsSL "$url" -o "$tmpExe" 2>$null
        } else {
            Invoke-WebRequest -Uri $url -OutFile $tmpExe -UseBasicParsing -TimeoutSec 300
        }
        if ((Test-Path $tmpExe) -and (Get-Item $tmpExe).Length -gt 1000000) {
            $downloaded = $true
            $downloadedUrl = $url
            break
        }
    } catch {
        # try next fallback url
    }
}

if (-not $downloaded -or -not (Test-Path $tmpExe)) {
    if (Test-Path $tmpExe) { Remove-Item -Path $tmpExe -Force -ErrorAction SilentlyContinue }
    Write-Error "Could not download native kronumos.exe. Please check your internet connection or visit https://kronumos.com/download"
    exit 1
}

# Fail-closed cryptographic SHA-256 checksum verification
$shaCandidates = @("$downloadedUrl.sha256", "$directPagesUrl.sha256", "$primaryUrl.sha256")
$expectedSha = $null
$shaMismatchError = $null

foreach ($shaUrl in $shaCandidates) {
    try {
        if (Test-Path $tmpSha) { Remove-Item -Path $tmpSha -Force -ErrorAction SilentlyContinue }
        if ($hasCurlExe) {
            & curl.exe -fsSL "$shaUrl" -o "$tmpSha" 2>$null
        } else {
            Invoke-WebRequest -Uri $shaUrl -OutFile $tmpSha -UseBasicParsing -TimeoutSec 30
        }
        if (Test-Path $tmpSha) {
            $candidateSha = ((Get-Content $tmpSha -Raw).Trim() -split '\s+')[0].ToLowerInvariant()
            Remove-Item -Path $tmpSha -Force -ErrorAction SilentlyContinue
            if ($candidateSha -and ($candidateSha -match '^[0-9a-f]{64}$')) {
                $expectedSha = $candidateSha
                break
            }
        }
    } catch {
        if (Test-Path $tmpSha) { Remove-Item -Path $tmpSha -Force -ErrorAction SilentlyContinue }
    }
}

if (-not $expectedSha) {
    Remove-Item -Path $tmpExe -Force -ErrorAction SilentlyContinue
    $shaMismatchError = "SHA-256 verification failed: could not download valid .sha256 checksum manifest (fail-closed verification)."
} else {
    $actualSha = (Get-FileHash -Path $tmpExe -Algorithm SHA256).Hash.ToLowerInvariant()
    if ($expectedSha -ne $actualSha) {
        Remove-Item -Path $tmpExe -Force -ErrorAction SilentlyContinue
        $shaMismatchError = "SHA-256 checksum verification failed! Expected $expectedSha, got $actualSha"
    }
}

if ($shaMismatchError) {
    Write-Error $shaMismatchError
    exit 1
}

$shortSha = $actualSha.Substring(0, 12)
Write-Host "    ✔ SHA-256 verified ($shortSha...)" -ForegroundColor Gray

# Safe atomic swap even if a previous kronumos.exe process is running
if (Test-Path $oldExe) { Remove-Item -Path $oldExe -Force -ErrorAction SilentlyContinue }
if (Test-Path $exePath) {
    try {
        Remove-Item -Path $exePath -Force -ErrorAction Stop
    } catch {
        Rename-Item -Path $exePath -NewName "kronumos.exe.old" -Force -ErrorAction SilentlyContinue
    }
}
Move-Item -Path $tmpExe -Destination $exePath -Force

Write-Host "  ◆ Updating User PATH & verifying installation..." -ForegroundColor White
$userPath = [Environment]::GetEnvironmentVariable("Path", [EnvironmentVariableTarget]::User)
if ([string]::IsNullOrWhiteSpace($userPath)) {
    [Environment]::SetEnvironmentVariable("Path", $installDir, [EnvironmentVariableTarget]::User)
} elseif ($userPath -split ';' -notcontains $installDir) {
    [Environment]::SetEnvironmentVariable("Path", "$userPath;$installDir", [EnvironmentVariableTarget]::User)
}
$env:Path = "$installDir;$env:Path"

Write-Host ""
Write-Host "  ✔ Kronumos Core CLI $Tag installed natively to:" -ForegroundColor White
Write-Host "    ↳ $exePath" -ForegroundColor DarkGray
Write-Host ""
Write-Host "  Next steps:" -ForegroundColor DarkGray
Write-Host "    kronumos         Launch interactive workbench & slash palette" -ForegroundColor White
Write-Host "    kronumos setup   Configure BYOK API key, local Ollama, or Kronumos Cloud" -ForegroundColor White
Write-Host "    kronumos update  Self-update anytime (or /update inside REPL)" -ForegroundColor White
Write-Host "    /hunt  /fix      0-LLM AST bug audit & autonomous test repair" -ForegroundColor White
Write-Host ""

# Test run
try {
    & "$exePath" --version
} catch {}
