$ErrorActionPreference = 'Stop'
Set-Location -LiteralPath $PSScriptRoot
python -c "import fastapi,uvicorn" 2>$null
if ($LASTEXITCODE -ne 0) { throw 'Python 依赖缺失，请先运行 python -m pip install -r requirements.txt' }
if (-not (Test-Path -LiteralPath 'frontend/dist/index.html')) {
  Push-Location frontend
  try {
    if (-not (Test-Path -LiteralPath 'node_modules')) { npm install; if ($LASTEXITCODE -ne 0) { throw 'npm install 失败' } }
    npm run build
    if ($LASTEXITCODE -ne 0) { throw '前端构建失败' }
  } finally { Pop-Location }
}
Write-Host '浏览器地址: http://127.0.0.1:8000 （首次启动需要建立索引）'
python -m uvicorn backend.app:app --host 127.0.0.1 --port 8000
