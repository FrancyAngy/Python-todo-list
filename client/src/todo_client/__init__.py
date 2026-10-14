import sqlalchemy as sql
from sqlalchemy.orm import Session
from textual.app import App, ComposeResult, log
from textual.containers import HorizontalGroup, VerticalGroup, VerticalScroll
from textual.widgets import (Button, Checkbox, Collapsible, Footer, Header,
                             Input, Label)

from .models import *
from .sqlalchemy_url import db_url


class ToDoItem(HorizontalGroup):

    def __init__(self, Obj: ToDo, db: Session):
        super().__init__()
        self.todo = Obj
        self.db = db

    def compose(self) -> ComposeResult:
        yield Checkbox("Done", id="done", value=self.todo.done)
        with Collapsible(title=self.todo.name):
            yield Label(self.todo.description)
        yield Button("Delete", "error", id="delete")

    def on_checkbox_changed(self, event: Checkbox.Changed):
        if event.checkbox.id == "done":
            stmt = (
                sql.update(ToDo)
                .where(ToDo.id == self.todo.id)
                .values(done=event.checkbox.value)
            )
            self.db.execute(stmt)
            self.db.commit()

    def on_button_pressed(self, event: Button.Pressed):
        if event.button.id == "delete":
            stmt = sql.delete(ToDo).where(ToDo.id == self.todo.id)
            self.db.execute(stmt)
            self.db.commit()
            self.remove()


class ToDoApp(App):

    BINDINGS = [
        ("d", "toggle_dark", "Toggle dark mode"),
        ("r", "refresh", "Refresh list"),
    ]
    db = sql.create_engine(db_url)
    con = Session(db)

    def compose(self) -> ComposeResult:
        yield Header()
        yield Footer()
        with VerticalScroll():
            for item in self.con.scalars(sql.select(ToDo).where(ToDo.done == False)):
                yield ToDoItem(item, self.con)

        with Collapsible(title="Already done"), VerticalScroll():
            for item in self.con.scalars(sql.select(ToDo).where(ToDo.done)):
                yield ToDoItem(item, self.con)

    def action_toggle_dark(self) -> None:
        self.theme = (
            "textual-dark" if self.theme == "textual-light" else "textual-light"
        )

    def action_refresh(self):
        self.refresh(recompose=True)

    def __del__(self):
        self.con.commit()
        self.con.close()


def main() -> None:
    app = ToDoApp()
    app.run()
