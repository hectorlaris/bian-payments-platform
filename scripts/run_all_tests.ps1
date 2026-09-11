# Repo-level test runner: installs Python packages, runs all Python and .NET test
# suites, validates contracts and diagrams, and runs the end-to-end smoke test.
# Mirrors what CI does, for local one-command verification.

$ErrorActionPreference = "Stop"
$env:DOTNET_CLI_TELEMETRY_OPTOUT = "1"
$root = Split-Path -Parent $PSScriptRoot

Write-Host "== Installing Python packages (editable) ==" -ForegroundColor Cyan
$pyPackages = @(
    "services/shared/iso20022_python",
    "services/payment-initiation",
    "services/payment-execution/rail-adapter",
    "services/integration"
)
foreach ($pkg in $pyPackages) {
    python -m pip install -e (Join-Path $root $pkg) --quiet
}

Write-Host "== Structure + contracts + diagrams ==" -ForegroundColor Cyan
python (Join-Path $root "scripts/validate_structure.py")
python (Join-Path $root "scripts/validate_examples.py")
python (Join-Path $root "scripts/check_mermaid.py")

Write-Host "== Python unit tests ==" -ForegroundColor Cyan
foreach ($pkg in $pyPackages) {
    Write-Host "-- pytest $pkg" -ForegroundColor DarkCyan
    python -m pytest (Join-Path $root $pkg) -q
}

Write-Host "== .NET tests ==" -ForegroundColor Cyan
$dotnetTests = @(
    "services/shared/iso20022-dotnet.Tests",
    "services/payment-order/PaymentOrder.Tests",
    "services/payment-execution/PaymentExecution.Tests"
)
foreach ($proj in $dotnetTests) {
    Write-Host "-- dotnet test $proj" -ForegroundColor DarkCyan
    dotnet test (Join-Path $root $proj) --nologo
}

Write-Host "== End-to-end smoke ==" -ForegroundColor Cyan
python (Join-Path $root "scripts/e2e_smoke.py")

Write-Host "All checks passed." -ForegroundColor Green
