import sqlalchemy as sql
from sqlalchemy.orm import sessionmaker
from textual.app import App, ComposeResult
from textual.containers import HorizontalGroup, VerticalScroll
from textual.widgets import (Button, Checkbox, Collapsible, Footer, Header,
                             Label)

from .models import *
from .sqlalchemy_url import db_url

db = sql.create_engine(db_url)
session = sessionmaker(db)


class ToDoItem(HorizontalGroup):

    def __init__(self, name: str, description: str, done: bool, id: int):
        super().__init__()
        self.todo_name = name
        self.todo_desc = description
        self.todo_done = done
        self.todo_id = id

    def compose(self) -> ComposeResult:
        yield Checkbox("Done", id="done", value=self.todo_done)
        with Collapsible(title=self.todo_name):
            yield Label(self.todo_desc)
        yield Button("Delete", "error")


class ToDoApp(App):

    BINDINGS = [("d", "toggle_dark", "Toggle dark mode")]
    con = session()

    def compose(self) -> ComposeResult:
        yield Header()
        yield Footer()
        with VerticalScroll():
            for item in self.con.scalars(sql.select(ToDo)):
                yield ToDoItem(
                    str(item.name), str(item.description), bool(item.done), item.id
                )

    def action_toggle_dark(self) -> None:
        self.theme = (
            "textual-dark" if self.theme == "textual-light" else "textual-light"
        )


def main() -> None:
    app = ToDoApp()
    app.run()
