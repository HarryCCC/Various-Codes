# Migrate_All.ps1
param(
    [string]$sourceRoot = "I:\股票数据\L2-到202406",
    [string]$destRoot = "F:\股票"
)

# 处理核心逻辑
function Process-Folder {
    param(
        [string]$sourceDir,
        [string]$year,
        [string]$dateFolderName
    )
    
    $destDir = Join-Path -Path $destRoot -ChildPath "$year\$dateFolderName"
    $allSourceFiles = Get-ChildItem -Path $sourceDir -Filter "*.gz" -File
    $missingFiles = @()

    # 检查缺失文件
    foreach ($file in $allSourceFiles) {
        $destFile = Join-Path -Path $destDir -ChildPath $file.Name
        if (-not (Test-Path -Path $destFile)) {
            $missingFiles += $file
        }
    }

    # 若无缺失则跳过
    if ($missingFiles.Count -eq 0) {
        Write-Host "  [完整] $year\$dateFolderName (共 $($allSourceFiles.Count) 文件)" -ForegroundColor DarkGray
        return
    }

    # 迁移缺失文件
    Write-Host "  [处理] $year\$dateFolderName (缺失 $($missingFiles.Count)/$($allSourceFiles.Count) 文件)" -ForegroundColor Cyan
    foreach ($file in $missingFiles) {
        $destFile = Join-Path -Path $destDir -ChildPath $file.Name
        try {
            New-Item -Path $destDir -ItemType Directory -Force | Out-Null
            Copy-Item -Path $file.FullName -Destination $destFile -ErrorAction Stop
            Write-Host "    → 已复制: $($file.Name)" -ForegroundColor Green
        } catch {
            Write-Host "    → 失败: $($file.Name) → $_" -ForegroundColor Red
        }
    }
}

# 主流程
$yearFolders = Get-ChildItem -Path $sourceRoot -Directory |
               Where-Object { $_.Name -match '^\d{4}$' } |
               Sort-Object @{ Expression={[int]$_.Name}; Descending=$true }

foreach ($yearFolder in $yearFolders) {
    $year = $yearFolder.Name
    Write-Host "`n处理年份: $year" -ForegroundColor Cyan -BackgroundColor DarkGray

    # 优先处理 YYYY-MM-DD 格式目录
    Get-ChildItem -Path $yearFolder.FullName -Directory |
    Where-Object { $_.Name -match '^\d{4}-\d{2}-\d{2}$' } |
    Sort-Object @{ Expression={ [datetime]::ParseExact($_.Name, "yyyy-MM-dd", $null) }; Descending=$true } |
    ForEach-Object {
        Process-Folder -sourceDir $_.FullName -year $year -dateFolderName $_.Name
    }

    # 处理 YYYYMMDD 格式目录
    Get-ChildItem -Path $yearFolder.FullName -Directory |
    Where-Object { $_.Name -match '^\d{8}$' } |
    Sort-Object @{ Expression={[int]$_.Name}; Descending=$true } |
    ForEach-Object {
        Process-Folder -sourceDir $_.FullName -year $year -dateFolderName $_.Name
    }
}

Write-Host "`n全部迁移完成！" -ForegroundColor Magenta