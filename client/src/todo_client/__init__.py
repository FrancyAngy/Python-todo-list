import sqlalchemy as sql
from sqlalchemy.orm import Session
from textual.app import App, ComposeResult, log
from textual.containers import HorizontalGroup, VerticalScroll
from textual.widgets import (Button, Checkbox, Collapsible, Footer, Header,
                             Label, Static)

from .models import *
from .sqlalchemy_url import db_url


class ToDoItem(HorizontalGroup):

    def __init__(self, name: str, description: str, done: bool, id: int, db: Session):
        super().__init__()
        self.todo_name = name
        self.todo_desc = description
        self.todo_done = done
        self.todo_id = id
        self.db = db

    def compose(self) -> ComposeResult:
        yield Checkbox("Done", id="done", value=self.todo_done)
        with Collapsible(title=self.todo_name):
            yield Label(self.todo_desc)
        yield Button("Delete", "error")

    def on_checkbox_changed(self, event: Checkbox.Changed):
        if event.checkbox.id == "done":
            stmt = (
                sql.update(ToDo)
                .where(ToDo.id == self.todo_id)
                .values(done=event.checkbox.value)
            )
            log(stmt)
            self.db.execute(stmt)


class ToDoApp(App):

    BINDINGS = [("d", "toggle_dark", "Toggle dark mode")]
    db = sql.create_engine(db_url)
    con = Session(db)

    def compose(self) -> ComposeResult:
        yield Header()
        yield Footer()
        with VerticalScroll():
            for item in self.con.scalars(sql.select(ToDo)):
                log(f"Name: {item.name}, ID: {item.id}")
                yield ToDoItem(
                    item.name.__str__(),
                    item.description.__str__(),
                    item.done.__bool__(),
                    item.id.__int__(),
                    self.con,
                )

    def action_toggle_dark(self) -> None:
        self.theme = (
            "textual-dark" if self.theme == "textual-light" else "textual-light"
        )

    def __del__(self):
        self.con.commit()
        self.con.close()


def main() -> None:
    app = ToDoApp()
    app.run()
