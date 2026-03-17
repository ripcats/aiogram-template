import shutil
import subprocess
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]


def _prepare_project_copy(tmp_path: Path) -> Path:
    project_copy = tmp_path / "project"
    project_copy.mkdir()

    files_to_copy = (
        "dialog_rem.sh",
        "pyproject.toml",
        "README.md",
        "app/main.py",
        "app/logging_setup.py",
        "app/presentation/dialogs/__init__.py",
        "app/presentation/dialogs/basic.py",
    )

    for relative_path in files_to_copy:
        source_path = PROJECT_ROOT / relative_path
        target_path = project_copy / relative_path
        target_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source_path, target_path)

    return project_copy


def test_dialog_rem_script_removes_aiogram_dialog_artifacts(tmp_path: Path) -> None:
    project_copy = _prepare_project_copy(tmp_path)

    result = subprocess.run(
        ["sh", "dialog_rem.sh"],
        cwd=project_copy,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    assert (
        result.stdout.strip()
        == "aiogram-dialog dependency, startup integration and dialog files removed."
    )

    pyproject_text = (project_copy / "pyproject.toml").read_text(encoding="utf-8")
    main_text = (project_copy / "app/main.py").read_text(encoding="utf-8")
    logging_text = (project_copy / "app/logging_setup.py").read_text(encoding="utf-8")
    readme_text = (project_copy / "README.md").read_text(encoding="utf-8")

    assert "aiogram-dialog>=" not in pyproject_text
    assert "from aiogram_dialog import setup_dialogs" not in main_text
    assert "setup_dialogs(dp)" not in main_text
    assert "aiogram_dialog" not in logging_text
    assert not (project_copy / "app/presentation/dialogs").exists()
    assert "aiogram-dialog" not in readme_text
    assert "dialog_rem.sh" not in readme_text
    assert "dialog_rem.ps1" not in readme_text
    assert "from aiogram import Bot, Dispatcher" in main_text


def test_dialog_rem_script_is_safe_to_run_twice(tmp_path: Path) -> None:
    project_copy = _prepare_project_copy(tmp_path)

    first_run = subprocess.run(
        ["sh", "dialog_rem.sh"],
        cwd=project_copy,
        capture_output=True,
        text=True,
        check=False,
    )
    second_run = subprocess.run(
        ["sh", "dialog_rem.sh"],
        cwd=project_copy,
        capture_output=True,
        text=True,
        check=False,
    )

    assert first_run.returncode == 0, first_run.stderr
    assert second_run.returncode == 0, second_run.stderr
    assert not (project_copy / "app/presentation/dialogs").exists()


def test_dialog_rem_powershell_script_targets_same_artifacts() -> None:
    script_path = PROJECT_ROOT / "dialog_rem.ps1"
    script_text = script_path.read_text(encoding="utf-8")

    assert script_path.exists()
    assert '"aiogram-dialog>=2.5.0",' in script_text
    assert 'from aiogram_dialog import setup_dialogs' in script_text
    assert 'setup_dialogs(dp)' in script_text
    assert 'app/presentation/dialogs' in script_text
    assert 'aiogram_dialog' in script_text
    assert (
        "aiogram-dialog dependency, startup integration and dialog files removed."
        in script_text
    )
