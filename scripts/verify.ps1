$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

function Invoke-Checked {
  param(
    [scriptblock]$Command
  )

  & $Command
  if ($LASTEXITCODE -ne 0) {
    exit $LASTEXITCODE
  }
}

Write-Host (& python --version)
Invoke-Checked { python -m etsy_research.cli validate-config }
Invoke-Checked { python -m pytest -q }
Invoke-Checked { python -m compileall src tests }
Invoke-Checked { python scripts/secret_scan.py }

Invoke-Checked { git diff --check }
