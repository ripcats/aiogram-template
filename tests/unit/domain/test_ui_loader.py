from app.ui import UI


class TestUILoader:
    def test_common_start_welcome_exists(self) -> None:
        assert hasattr(UI.common.start, "welcome")  # type: ignore[attr-defined]
        assert "{full_name}" in UI.common.start.welcome  # type: ignore[attr-defined]

    def test_buttons_exist(self) -> None:
        for btn in ("back", "close", "user_ban", "user_unban", "users_list", "refresh"):
            assert hasattr(UI.buttons, btn), f"Missing button: {btn}"

    def test_callback_answers_exist(self) -> None:
        for key in ("action_banned", "action_unbanned", "action_denied"):
            assert hasattr(UI.callback_answers, key), f"Missing callback_answer: {key}"

    def test_owner_panel_texts_exist(self) -> None:
        assert hasattr(UI.owner.panel, "title")  # type: ignore[attr-defined]
        assert hasattr(UI.owner.panel, "ban_success")  # type: ignore[attr-defined]
