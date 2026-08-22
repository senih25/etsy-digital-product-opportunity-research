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
& python -c @'
from pathlib import Path
import re

patterns = [
    re.compile(r"sk-[A-Za-z0-9]+"),
    re.compile(r"xoxb-[A-Za-z0-9-]+"),
    re.compile(r"-----BEGIN PRIVATE KEY-----"),
]

root = Path(".")
for path in root.rglob("*"):
    if path.is_dir():
        continue
    if ".git" in path.parts:
        continue
    if "__pycache__" in path.parts:
        continue
    if path.suffix in (".pyc", ".pyo"):
        continue
    if path.as_posix().endswith("scripts/verify.ps1"):
        continue
    text = path.read_text(encoding="utf-8", errors="ignore")
    for pattern in patterns:
        if pattern.search(text):
            raise SystemExit(f"secret pattern found in {path}")
print("SECRET_SCAN=PASS")
'@
if ($LASTEXITCODE -ne 0) {
  exit $LASTEXITCODE
}

Invoke-Checked { git diff --check }
