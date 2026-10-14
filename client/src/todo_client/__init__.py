import sqlalchemy as sql
from sqlalchemy.orm import Session
from textual.app import App, ComposeResult, Notify
from textual.containers import Grid, HorizontalGroup, VerticalScroll
from textual.screen import Screen
from textual.widgets import (Button, Checkbox, Collapsible, Footer, Header,
                             Input, Label)

from .models import *
from .sqlalchemy_url import db_url

new_dialog = True


class ToDoItem(HorizontalGroup):

    def __init__(self, Obj: ToDo, db: Session):
        super().__init__()
        self.todo = Obj
        self.db = db

    def compose(self) -> ComposeResult:
        yield Checkbox("Done", id="done", value=self.todo.done.__bool__())
        with Collapsible(title=self.todo.name.__str__()):
            yield Label(self.todo.description.__str__())
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


class ToDoAdd(Screen):

    CSS = """
        ToDoAdd {
                align: center middle;
        }

        #dialog {
            grid-size: 2;
            grid-gutter: 1 2;
            grid-rows: 1fr 3;
            padding: 0 1;
            width: 60;
            height: 16;
            border: thick $background 80%;
            background: $surface;
        }

        #title {
            column-span: 2;
            height: 1fr;
            width: 1fr;
            content-align: center middle;
        }

        Button {
            width: 100%;
        }

    """

    def __init__(self, con: Session, app: ToDoApp):
        super().__init__()
        self.con = con
        self.main = app

    def compose(self) -> ComposeResult:
        with Grid(id="dialog"):
            yield Label("Create new To-Do item", id="title")
            yield Input(placeholder="Name", id="name")
            yield Input(placeholder="Description", id="desc")
            yield Button("Create", "success", id="create")
            yield Button("Cancel", "error", id="cancel")

    def on_button_pressed(self, event: Button.Pressed):
        global new_dialog
        if event.button.id == "create":
            name = self.query_one("#name", Input).value
            description = self.query_one("#desc", Input).value
            if name == "":
                self.notify("The name must not be empty", severity="error")
                return

            todo = ToDo(name=name, description=description)
            self.con.add(todo)
            self.con.commit()
            self.main.refresh(recompose=True)

        new_dialog = True
        self.app.pop_screen()


class ToDoApp(App):

    BINDINGS = [
        ("d", "toggle_dark", "Toggle dark mode"),
        ("r", "refresh", "Refresh list"),
        ("n", "new", "Create new To-Do item"),
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

    def action_new(self):
        global new_dialog
        if new_dialog:
            new_dialog = False
            self.push_screen(ToDoAdd(self.con, self))

    def __del__(self):
        self.con.commit()
        self.con.close()


def main() -> None:
    app = ToDoApp()
    app.run()
