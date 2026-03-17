from __future__ import annotations

import os
import re
import signal
import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

from rich.console import Console


ROOT_DIR = Path(__file__).resolve().parent
console = Console()


@dataclass(slots=True)
class ProjectConfig:
    name: str
    version: str
    mode: str
    include_aiogram_dialog: bool


@dataclass(slots=True)
class PyprojectMeta:
    name: str
    version: str


PROD_ENV_KEYS = (
    "bot_webhook_host",
    "bot_webhook_path",
    "bot_webhook_secret",
    "server_host",
    "server_port",
)

PROD_ENV_DEFAULTS = {
    "bot_webhook_host": "https://yourdomain.com",
    "bot_webhook_path": "/webhook",
    "bot_webhook_secret": "change_me_secret_32chars_minimum!!",
    "server_host": "0.0.0.0",
    "server_port": "8080",
}


def ask_project_config() -> ProjectConfig | None:
    inquirer, style, validation_error_cls, validator_cls = _load_prompt_dependencies()
    current_meta = _load_pyproject_meta(ROOT_DIR / "pyproject.toml")

    class ProjectNameValidator(validator_cls):
        def validate(self, document) -> None:
            text = document.text.strip()

            if not text:
                return

            if not re.fullmatch(r"[A-Za-z0-9._-]+", text):
                raise validation_error_cls(
                    message="Use only letters, numbers, '.', '-' and '_'.",
                    cursor_position=len(document.text),
                )

            if text[0] in "-._" or text[-1] in "-._":
                raise validation_error_cls(
                    message="Project name cannot start or end with '.', '-' or '_'.",
                    cursor_position=len(document.text),
                )

            if "--" in text or "__" in text or ".." in text:
                raise validation_error_cls(
                    message="Project name cannot contain consecutive '.', '-' or '_' characters.",
                    cursor_position=len(document.text),
                )

    class VersionValidator(validator_cls):
        def validate(self, document) -> None:
            text = document.text.strip()

            if not text:
                return

            if not re.fullmatch(r"\d+\.\d+\.\d+", text):
                raise validation_error_cls(
                    message="Version must match x.y.z.",
                    cursor_position=len(document.text),
                )

    name = inquirer.text(
        message=f"Project name ({current_meta.name})",
        validate=ProjectNameValidator(),
        default="",
        filter=lambda x: x.strip(),
        style=style,
        raise_keyboard_interrupt=False,
    ).execute()
    if name is None:
        return None

    version = inquirer.text(
        message=f"Project version ({current_meta.version})",
        default="",
        validate=VersionValidator(),
        filter=lambda x: x.strip(),
        style=style,
        raise_keyboard_interrupt=False,
    ).execute()
    if version is None:
        return None

    mode = inquirer.select(
        message="Project mode",
        choices=["dev", "prod"],
        default="dev",
        style=style,
        raise_keyboard_interrupt=False,
    ).execute()
    if mode is None:
        return None

    include_aiogram_dialog = inquirer.confirm(
        message="Keep aiogram-dialog?",
        default=True,
        style=style,
        raise_keyboard_interrupt=False,
    ).execute()
    if include_aiogram_dialog is None:
        return None

    return ProjectConfig(
        name=name or current_meta.name,
        version=version or current_meta.version,
        mode=mode,
        include_aiogram_dialog=include_aiogram_dialog,
    )


def _venv_python_path(root_dir: Path) -> Path:
    if sys.platform.startswith("win"):
        return root_dir / ".venv" / "Scripts" / "python.exe"
    return root_dir / ".venv" / "bin" / "python"


def _run_uv_sync(root_dir: Path) -> None:
    with console.status("[bold blue]Installing InquirerPy for init.py...[/]"):
        uv = shutil.which("uv")
        if uv is not None:
            pyproject_path = root_dir / "pyproject.toml"
            if pyproject_path.exists() and "inquirerpy" in pyproject_path.read_text(
                encoding="utf-8"
            ).lower():
                subprocess.run([uv, "sync"], cwd=root_dir, check=True)
            else:
                subprocess.run([uv, "add", "InquirerPy"], cwd=root_dir, check=True)
            return

        if sys.platform.startswith("win"):
            pip_path = root_dir / ".venv" / "Scripts" / "pip.exe"
        else:
            pip_path = root_dir / ".venv" / "bin" / "pip"

        if pip_path.exists():
            subprocess.run(
                [str(pip_path), "install", "InquirerPy"],
                cwd=root_dir,
                check=True,
            )
            return

    raise RuntimeError(
        "InquirerPy is not installed. Install it with `uv add InquirerPy` or `.venv/bin/pip install InquirerPy`."
    )


def _load_prompt_dependencies():  # type: ignore[no-untyped-def]
    try:
        from InquirerPy import inquirer
        from InquirerPy.utils import get_style
        from prompt_toolkit.validation import ValidationError, Validator
    except ModuleNotFoundError:
        _run_uv_sync(ROOT_DIR)

        try:
            from InquirerPy import inquirer
            from InquirerPy.utils import get_style
            from prompt_toolkit.validation import ValidationError, Validator
        except ModuleNotFoundError:
            venv_python = _venv_python_path(ROOT_DIR)
            current_python = Path(sys.executable).resolve()
            if venv_python.exists() and current_python != venv_python.resolve():
                os.execv(
                    str(venv_python),
                    [str(venv_python)] + sys.argv,
                )
            raise RuntimeError(
                "InquirerPy is still unavailable after installation. Run `uv run python init.py`."
            )

    style = get_style(
        {
            "pointer": "#5f87ff",
            "highlighted": "#5f87ff",
            "selected": "#5f87ff",
            "validation-toolbar": "#ff5f5f",
        },
        style_override=False,
    )
    return inquirer, style, ValidationError, Validator


def _load_pyproject_meta(file_path: Path) -> PyprojectMeta:
    text = file_path.read_text(encoding="utf-8")

    name_match = re.search(r'^name = "(.+)"$', text, re.MULTILINE)
    version_match = re.search(r'^version = "(.+)"$', text, re.MULTILINE)

    return PyprojectMeta(
        name=name_match.group(1) if name_match is not None else "aiogram-template",
        version=version_match.group(1) if version_match is not None else "0.1.0",
    )


def _replace_project_toml_value(file_path: Path, key: str, value: str) -> None:
    lines = file_path.read_text(encoding="utf-8").splitlines()
    in_project_section = False

    for index, line in enumerate(lines):
        stripped = line.strip()
        if stripped.startswith("[") and stripped.endswith("]"):
            in_project_section = stripped == "[project]"
            continue

        if in_project_section and re.fullmatch(rf"{re.escape(key)} = \".*\"", stripped):
            lines[index] = f'{key} = "{value}"'
            file_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
            return

    raise RuntimeError(f"Key `{key}` was not found in [project] section of pyproject.toml")


def _set_env_value(file_path: Path, key: str, value: str) -> None:
    if file_path.exists():
        lines = file_path.read_text(encoding="utf-8").splitlines()
    else:
        lines = []
    key_lower = key.lower()

    for index, line in enumerate(lines):
        if "=" not in line:
            continue
        current_key, _current_value = line.split("=", 1)
        if current_key.lower() == key_lower:
            lines[index] = f"{key}={value}"
            break
    else:
        if lines and lines[-1] != "":
            lines.append("")
        lines.append(f"{key}={value}")

    file_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _ensure_env_file(root_dir: Path) -> Path:
    env_path = root_dir / ".env"
    if env_path.exists():
        return env_path

    env_example_path = root_dir / ".env.example"
    if env_example_path.exists():
        shutil.copyfile(env_example_path, env_path)
    else:
        env_path.write_text("", encoding="utf-8")

    return env_path


def _dialog_removal_command(root_dir: Path) -> list[str]:
    if sys.platform.startswith("win"):
        shell = shutil.which("powershell") or shutil.which("pwsh")
        if shell is None:
            raise RuntimeError("PowerShell not found. Run dialog_rem.ps1 manually.")
        return [shell, "-ExecutionPolicy", "Bypass", "-File", str(root_dir / "dialog_rem.ps1")]

    return ["sh", str(root_dir / "dialog_rem.sh")]


def _remove_aiogram_dialog(root_dir: Path) -> None:
    subprocess.run(
        _dialog_removal_command(root_dir),
        cwd=root_dir,
        check=True,
    )


def apply_project_config(config: ProjectConfig, root_dir: Path = ROOT_DIR) -> None:
    _replace_project_toml_value(root_dir / "pyproject.toml", "name", config.name)
    _replace_project_toml_value(root_dir / "pyproject.toml", "version", config.version)
    env_path = _ensure_env_file(root_dir)
    _set_env_value(env_path, "bot_mode", config.mode)

    if config.mode == "prod":
        env_defaults = dict(PROD_ENV_DEFAULTS)
        env_example_path = root_dir / ".env.example"
        if env_example_path.exists():
            for line in env_example_path.read_text(encoding="utf-8").splitlines():
                if "=" not in line or line.lstrip().startswith("#"):
                    continue
                key, value = line.split("=", 1)
                env_defaults[key] = value
        for key in PROD_ENV_KEYS:
            _set_env_value(env_path, key, env_defaults[key])

    if not config.include_aiogram_dialog:
        _remove_aiogram_dialog(root_dir)


def _handle_exit_signal(signum: int, _frame: object) -> None:
    console.print("\n[dim]Cancelled.[/dim]")
    raise SystemExit(0)


def _register_exit_handlers() -> None:
    signal.signal(signal.SIGINT, _handle_exit_signal)


def main() -> None:
    _register_exit_handlers()

    try:
        config = ask_project_config()
    except (KeyboardInterrupt, EOFError):
        console.print("\n[dim]Cancelled.[/dim]")
        return

    if config is None:
        console.print("\n[dim]Cancelled.[/dim]")
        return

    apply_project_config(config)

    console.print("[green]Settings saved.[/green]")


if __name__ == "__main__":
    main()
