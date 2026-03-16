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
    $content = Get-Content -Path $filePath -Raw
    $pattern = "Если ``aiogram-dialog`` не нужен, просто запусти:[\s\S]*?## Как расширять"
    $replacement = @"
Если `aiogram-dialog` не нужен, просто запусти:

```sh
./dialog_rem.sh
```

Для Windows:

```powershell
./dialog_rem.ps1
```

## Как расширять
"@
    $content = [System.Text.RegularExpressions.Regex]::Replace($content, $pattern, $replacement)
    Replace-FileContent -FilePath $filePath -Content $content
}

Remove-Dependency
Remove-Logger
Remove-StartupSetup
Remove-DialogFiles
Update-Readme

Write-Output "aiogram-dialog dependency, startup integration and dialog files removed."
