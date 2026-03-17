from pathlib import Path

from init import ProjectConfig, apply_project_config


def test_apply_project_config_updates_project_files(tmp_path: Path) -> None:
    project_dir = tmp_path / "project"
    project_dir.mkdir()

    (project_dir / "pyproject.toml").write_text(
        '[project]\nname = "aiogram-template"\nversion = "0.1.0"\n',
        encoding="utf-8",
    )
    (project_dir / ".env.example").write_text(
        "\n".join(
            [
                "bot_mode=dev",
                "bot_webhook_host=https://yourdomain.com",
                "bot_webhook_path=/webhook",
                "bot_webhook_secret=change_me_secret_32chars_minimum!!",
                "server_host=0.0.0.0",
                "server_port=8080",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    (project_dir / ".env").write_text(
        "\n".join(
            [
                "bot_mode=prod",
                "bot_webhook_host=https://custom.example.com",
                "bot_webhook_path=/hook",
                "bot_webhook_secret=secret",
                "server_host=127.0.0.1",
                "server_port=9000",
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    apply_project_config(
        ProjectConfig(
            name="my-bot",
            version="1.2.3",
            mode="dev",
            include_aiogram_dialog=True,
        ),
        root_dir=project_dir,
    )

    assert 'name = "my-bot"' in (project_dir / "pyproject.toml").read_text(
        encoding="utf-8"
    )
    assert 'version = "1.2.3"' in (project_dir / "pyproject.toml").read_text(
        encoding="utf-8"
    )
    assert "bot_mode=dev" in (project_dir / ".env").read_text(encoding="utf-8")
    assert "bot_webhook_host=https://custom.example.com" in (
        project_dir / ".env"
    ).read_text(encoding="utf-8")
    assert "server_host=127.0.0.1" in (project_dir / ".env").read_text(
        encoding="utf-8"
    )
    assert "bot_webhook_host=https://yourdomain.com" in (
        project_dir / ".env.example"
    ).read_text(encoding="utf-8")


def test_apply_project_config_runs_dialog_removal(tmp_path: Path, monkeypatch) -> None:
    project_dir = tmp_path / "project"
    project_dir.mkdir()

    (project_dir / "pyproject.toml").write_text(
        '[project]\nname = "aiogram-template"\nversion = "0.1.0"\n',
        encoding="utf-8",
    )
    (project_dir / ".env.example").write_text("bot_mode=dev\n", encoding="utf-8")

    called: list[Path] = []

    def fake_remove(root_dir: Path) -> None:
        called.append(root_dir)

    monkeypatch.setattr("init._remove_aiogram_dialog", fake_remove)

    apply_project_config(
        ProjectConfig(
            name="my-bot",
            version="1.2.3",
            mode="dev",
            include_aiogram_dialog=False,
        ),
        root_dir=project_dir,
    )

    assert called == [project_dir]


def test_apply_project_config_creates_env_example_if_missing(tmp_path: Path) -> None:
    project_dir = tmp_path / "project"
    project_dir.mkdir()

    (project_dir / "pyproject.toml").write_text(
        '[project]\nname = "aiogram-template"\nversion = "0.1.0"\n',
        encoding="utf-8",
    )

    apply_project_config(
        ProjectConfig(
            name="my-bot",
            version="1.2.3",
            mode="prod",
            include_aiogram_dialog=True,
        ),
        root_dir=project_dir,
    )

    env_text = (project_dir / ".env").read_text(encoding="utf-8")
    assert "bot_mode=prod" in env_text
    assert "bot_webhook_host=https://yourdomain.com" in env_text
    assert "bot_webhook_path=/webhook" in env_text
    assert "bot_webhook_secret=change_me_secret_32chars_minimum!!" in env_text
    assert "server_host=0.0.0.0" in env_text
    assert "server_port=8080" in env_text


def test_apply_project_config_copies_env_example_and_restores_prod_values(
    tmp_path: Path,
) -> None:
    project_dir = tmp_path / "project"
    project_dir.mkdir()

    (project_dir / "pyproject.toml").write_text(
        '[project]\nname = "aiogram-template"\nversion = "0.1.0"\n',
        encoding="utf-8",
    )
    (project_dir / ".env.example").write_text(
        "\n".join(
            [
                "bot_mode=dev",
                "bot_webhook_host=https://yourdomain.com",
                "bot_webhook_path=/webhook",
                "bot_webhook_secret=change_me_secret_32chars_minimum!!",
                "server_host=0.0.0.0",
                "server_port=8080",
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    apply_project_config(
        ProjectConfig(
            name="my-bot",
            version="1.2.3",
            mode="prod",
            include_aiogram_dialog=True,
        ),
        root_dir=project_dir,
    )

    env_text = (project_dir / ".env").read_text(encoding="utf-8")
    assert "bot_mode=prod" in env_text
    assert "bot_webhook_host=https://yourdomain.com" in env_text
    assert "bot_webhook_path=/webhook" in env_text
    assert "bot_webhook_secret=change_me_secret_32chars_minimum!!" in env_text
    assert "server_host=0.0.0.0" in env_text
    assert "server_port=8080" in env_text


def test_apply_project_config_keeps_prod_fields_for_new_dev_env(tmp_path: Path) -> None:
    project_dir = tmp_path / "project"
    project_dir.mkdir()

    (project_dir / "pyproject.toml").write_text(
        '[project]\nname = "aiogram-template"\nversion = "0.1.0"\n',
        encoding="utf-8",
    )
    (project_dir / ".env.example").write_text(
        "\n".join(
            [
                "bot_mode=prod",
                "bot_webhook_host=https://yourdomain.com",
                "bot_webhook_path=/webhook",
                "bot_webhook_secret=change_me_secret_32chars_minimum!!",
                "server_host=0.0.0.0",
                "server_port=8080",
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    apply_project_config(
        ProjectConfig(
            name="my-bot",
            version="1.2.3",
            mode="dev",
            include_aiogram_dialog=True,
        ),
        root_dir=project_dir,
    )

    env_text = (project_dir / ".env").read_text(encoding="utf-8")
    assert "bot_mode=dev" in env_text
    assert "bot_webhook_host=https://yourdomain.com" in env_text
    assert "bot_webhook_path=/webhook" in env_text
    assert "bot_webhook_secret=change_me_secret_32chars_minimum!!" in env_text
    assert "server_host=0.0.0.0" in env_text
    assert "server_port=8080" in env_text


def test_apply_project_config_updates_env_key_case_insensitively(tmp_path: Path) -> None:
    project_dir = tmp_path / "project"
    project_dir.mkdir()

    (project_dir / "pyproject.toml").write_text(
        '[project]\nname = "aiogram-template"\nversion = "0.1.0"\n',
        encoding="utf-8",
    )
    (project_dir / ".env").write_text("BOT_MODE=dev\n", encoding="utf-8")

    apply_project_config(
        ProjectConfig(
            name="my-bot",
            version="1.2.3",
            mode="prod",
            include_aiogram_dialog=True,
        ),
        root_dir=project_dir,
    )

    env_text = (project_dir / ".env").read_text(encoding="utf-8")
    assert "BOT_MODE=dev" not in env_text
    assert "bot_mode=prod" in env_text


def test_apply_project_config_updates_only_project_section(tmp_path: Path) -> None:
    project_dir = tmp_path / "project"
    project_dir.mkdir()

    (project_dir / "pyproject.toml").write_text(
        "\n".join(
            [
                '[project]',
                'name = "aiogram-template"',
                'version = "0.1.0"',
                '',
                '[tool.demo]',
                'name = "keep-me"',
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    (project_dir / ".env").write_text("bot_mode=dev\n", encoding="utf-8")

    apply_project_config(
        ProjectConfig(
            name="my-bot",
            version="1.2.3",
            mode="dev",
            include_aiogram_dialog=True,
        ),
        root_dir=project_dir,
    )

    pyproject_text = (project_dir / "pyproject.toml").read_text(encoding="utf-8")
    assert '[project]\nname = "my-bot"\nversion = "1.2.3"' in pyproject_text
    assert '[tool.demo]\nname = "keep-me"' in pyproject_text
