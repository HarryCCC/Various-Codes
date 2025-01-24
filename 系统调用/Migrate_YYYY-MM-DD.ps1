# Migrate_Standard.ps1
param(
    [string]$sourceRoot = "I:\股票数据\L2-到202406",
    [string]$destRoot = "F:\股票"
)

# 主逻辑
$yearFolders = Get-ChildItem -Path $sourceRoot -Directory |
               Where-Object { $_.Name -match '^\d{4}$' } |
               Sort-Object @{ Expression={[int]$_.Name}; Descending=$true }

foreach ($yearFolder in $yearFolders) {
    $year = $yearFolder.Name
    Write-Host "`n处理年份: $year" -ForegroundColor Cyan
    
    # 获取并排序 YYYY-MM-DD 格式目录（最新日期优先）
    $dateFolders = Get-ChildItem -Path $yearFolder.FullName -Directory |
                   Where-Object { $_.Name -match '^\d{4}-\d{2}-\d{2}$' } |
                   Sort-Object @{ 
                       Expression = { [datetime]::ParseExact($_.Name, "yyyy-MM-dd", $null) }
                       Descending = $true
                   }

    foreach ($dateFolder in $dateFolders) {
        $sourceDir = $dateFolder.FullName
        $destDir = Join-Path -Path $destRoot -ChildPath "$year\$($dateFolder.Name)"
        $allSourceFiles = Get-ChildItem -Path $sourceDir -Filter "*.gz" -File
        $missingFiles = @()

        # 检查缺失文件
        foreach ($file in $allSourceFiles) {
            $destFile = Join-Path -Path $destDir -ChildPath $file.Name
            if (-not (Test-Path -Path $destFile)) {
                $missingFiles += $file
            }
        }

        # 若完整则跳过
        if ($missingFiles.Count -eq 0) {
            Write-Host "  [完整] $year\$($dateFolder.Name) (共 $($allSourceFiles.Count) 文件)" -ForegroundColor DarkGray
            continue
        }

        # 迁移缺失文件
        Write-Host "  [处理] $year\$($dateFolder.Name) (缺失 $($missingFiles.Count) 文件)" -ForegroundColor Cyan
        foreach ($file in $missingFiles) {
            try {
                New-Item -Path $destDir -ItemType Directory -Force | Out-Null
                Copy-Item -Path $file.FullName -Destination (Join-Path $destDir $file.Name) -ErrorAction Stop
                Write-Host "    → 已复制: $($file.Name)" -ForegroundColor Green
            } catch {
                Write-Host "    → 失败: $($file.Name) → $_" -ForegroundColor Red
            }
        }
    }
}

Write-Host "`nYYYY-MM-DD 格式迁移完成！" -ForegroundColor Magenta