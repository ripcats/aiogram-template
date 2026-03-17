$ErrorActionPreference = "Stop"

$RootDir = Split-Path -Parent $MyInvocation.MyCommand.Path

function Replace-FileContent {
    param(
        [string]$FilePath,
        [string]$Content
    )

    [System.IO.File]::WriteAllText($FilePath, $Content, [System.Text.UTF8Encoding]::new($false))
}

function Remove-LineContaining {
    param(
        [string]$FilePath,
        [string[]]$Needles
    )

    $lines = Get-Content -Path $FilePath
    $filtered = foreach ($line in $lines) {
        $skip = $false
        foreach ($needle in $Needles) {
            if ($line.Contains($needle)) {
                $skip = $true
                break
            }
        }
        if (-not $skip) {
            $line
        }
    }

    Replace-FileContent -FilePath $FilePath -Content (($filtered -join "`n") + "`n")
}

function Remove-Dependency {
    $filePath = Join-Path $RootDir "pyproject.toml"
    Remove-LineContaining -FilePath $filePath -Needles @('"aiogram-dialog>=2.5.0",')
}

function Remove-Logger {
    $filePath = Join-Path $RootDir "app/logging_setup.py"
    $content = Get-Content -Path $filePath -Raw
    $content = $content.Replace(', "aiogram_dialog"', "")
    Replace-FileContent -FilePath $filePath -Content $content
}

function Remove-StartupSetup {
    $filePath = Join-Path $RootDir "app/main.py"
    Remove-LineContaining -FilePath $filePath -Needles @(
        "from aiogram_dialog import setup_dialogs",
        "setup_dialogs(dp)"
    )
}

function Remove-DialogFiles {
    $dialogsPath = Join-Path $RootDir "app/presentation/dialogs"
    if (Test-Path -Path $dialogsPath) {
        Remove-Item -Path $dialogsPath -Recurse -Force
    }
}

function Update-Readme {
    $filePath = Join-Path $RootDir "README.md"
    $lines = Get-Content -Path $filePath
    $filtered = @()
    $skip = $false

    foreach ($line in $lines) {
        if ($line -eq "## Удаление aiogram-dialog") {
            $skip = $true
            continue
        }

        if ($skip -and $line -eq "---") {
            $skip = $false
            continue
        }

        if ($skip) {
            continue
        }

        if (
            $line.Contains("aiogram-dialog") -or
            $line.Contains("dialog_rem.sh") -or
            $line.Contains("dialog_rem.ps1")
        ) {
            continue
        }

        $filtered += $line
    }

    Replace-FileContent -FilePath $filePath -Content (($filtered -join "`n") + "`n")
}

Remove-Dependency
Remove-Logger
Remove-StartupSetup
Remove-DialogFiles
Update-Readme

Write-Output "aiogram-dialog dependency, startup integration and dialog files removed."
