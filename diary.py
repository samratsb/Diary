import datetime
from rich.console import Console
from rich.table import Table
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy import Column, create_engine, Date, String, Integer
import typer

app = typer.Typer()
Base = declarative_base()
engine = create_engine('sqlite:///diary.db', echo=True)

class Diary(Base):
    __tablename__ = 'diary'

    id = Column(Integer, primary_key=True, autoincrement=True)
    log = Column(String)
    date = Column(Date)
    tags = Column(String)
    
    def __init__(self, log, date, tags=""):
        self.log = log
        self.date = date
        self.tags = tags


def init_db():
    Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)
session = Session()


@app.command()
def add_entry():
    text = typer.prompt('Enter your log')
    tags = typer.prompt('Enter tags (comma separated)', default="")
    session.add(Diary(log=text, date=datetime.date.today(), tags=tags))
    session.commit()
    typer.echo("Entry added successfully!")


import textwrap

def truncate_log(log: str, word_limit: int = 5) -> str:
    """Truncate the log to show only the first and last few words."""
    words = log.split()
    if len(words) <= 2 * word_limit:
        return ' '.join(words)
    
    first_part = ' '.join(words[:word_limit])
    last_part = ' '.join(words[-word_limit:])
    return f"{first_part} ... {last_part}"

@app.command()
def list_entries():
    """List all diary entries with truncated logs."""
    entries = session.query(Diary).all()
    table = Table(title="Diary Entries")
    table.add_column("ID", justify="right", style="cyan", no_wrap=True)
    table.add_column("Log", style="magenta")
    table.add_column("Date", style="green")
    table.add_column("Tags", style="blue")
    
    for entry in entries:
        truncated_log = truncate_log(entry.log)
        table.add_row(str(entry.id), truncated_log, str(entry.date), entry.tags)
    
    console = Console()
    console.print(table)


@app.command()
def delete_entry(entry_id: int):
    """Delete a diary entry by its ID."""
    entry = session.query(Diary).filter(Diary.id == entry_id).first()
    
    if entry:
        session.delete(entry)
        session.commit()
        typer.echo(f"Entry with ID {entry_id} deleted successfully!")
    else:
        typer.echo(f"Entry with ID {entry_id} not found.")


@app.command()
def show_commands():
    typer.echo("Available commands: add-entry")

if __name__ == "__main__":
    init_db()
    app()
