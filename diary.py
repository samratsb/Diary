import datetime
import logging
from rich.console import Console
from rich.table import Table
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy import Column, create_engine, Date, String, Integer
import typer

# Set up Typer and Console
app = typer.Typer()
console = Console()

# SQLAlchemy setup
Base = declarative_base()
engine = create_engine('sqlite:///diary.db', echo=False)  # Set echo=False initially

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

def configure_logging(debug: bool):
    """Configure logging based on the debug flag."""
    logging.basicConfig(level=logging.DEBUG if debug else logging.WARNING)

@app.command()
def add_entry(debug: bool = False):
    """Add a new diary entry."""
    configure_logging(debug)
    text = typer.prompt('Enter your log')
    tags = typer.prompt('Enter tags (comma separated)', default="")
    entry = Diary(log=text, date=datetime.date.today(), tags=tags)
    session.add(entry)
    session.commit()
    console.print("[bold green]Entry added successfully![/bold green]")


def truncate_log(log: str, word_limit: int = 5) -> str:
    """Truncate the log to show only the first and last few words."""
    words = log.split()
    if len(words) <= 2 * word_limit:
        return ' '.join(words)
    
    first_part = ' '.join(words[:word_limit])
    last_part = ' '.join(words[-word_limit:])
    return f"{first_part} ... {last_part}"


@app.command()
def list_entries(debug: bool = False):
    """List all diary entries with truncated logs."""
    configure_logging(debug)
    entries = session.query(Diary).all()
    table = Table(title="Diary Entries")
    table.add_column("ID", justify="right", style="cyan", no_wrap=True)
    table.add_column("Log", style="magenta")
    table.add_column("Date", style="green")
    table.add_column("Tags", style="blue")
    
    for entry in entries:
        truncated_log = truncate_log(entry.log)
        table.add_row(str(entry.id), truncated_log, str(entry.date), entry.tags)
    
    console.print(table)

@app.command()
def search_entries(keyword: str, debug: bool = False):
    """Search for diary entries containing the keyword."""
    configure_logging(debug)
    results = session.query(Diary).filter(Diary.log.ilike(f"%{keyword}%")).all()
    if results:
        table = Table(title="Search Results")
        table.add_column("ID", justify="right")
        table.add_column("Log")
        table.add_column("Date", justify="right")
        table.add_column("Tags")

        for entry in results:
            table.add_row(str(entry.id), entry.log[:30] + ("..." if len(entry.log) > 30 else ""), entry.date.strftime("%Y-%m-%d"), entry.tags)
        
        console.print(table)
    else:
        console.print(f"[bold red]No entries found containing '{keyword}'[/bold red]")


@app.command()
def delete_entry(entry_id: int, debug: bool = False):
    """Delete a diary entry by ID."""
    configure_logging(debug)
    entry = session.query(Diary).filter(Diary.id == entry_id).first()
    if entry:
        session.delete(entry)
        session.commit()
        console.print(f"[bold red]Entry with ID {entry_id} deleted successfully![/bold red]")
    else:
        console.print(f"[bold red]No entry found with ID {entry_id}[/bold red]")
        

@app.command()
def show_commands():
    """Show available commands."""
    console.print("[bold blue]Available commands:[/bold blue]")
    console.print("[bold]add-entry[/bold] - Add a new diary entry")
    console.print("[bold]delete-entry[/bold] - Delete a diary entry by ID")
    console.print("[bold]search-entries[/bold] - Search for diary entries containing a keyword")
    console.print("[bold]list-entries[/bold] - List all diary entries")
    console.print("[bold]show-commands[/bold] - Show this help message")



if __name__ == "__main__":
    init_db()
    app()
