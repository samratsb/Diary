import typer
from rich.console import Console
from rich.Table import Table

console = Console()
table = Table()
app = typer.Typer()

@app.command()
def main():
    typer.echo("")

if __name__ == "__main__":
    app()