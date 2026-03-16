from aiogram.filters.state import State, StatesGroup
from aiogram_dialog import Dialog, Window
from aiogram_dialog.widgets.text import Const


class BasicDialogSG(StatesGroup):
    main = State()


def build_basic_dialog() -> Dialog:
    return Dialog(
        Window(
            Const("Basic dialog"),
            state=BasicDialogSG.main,
        )
    )
