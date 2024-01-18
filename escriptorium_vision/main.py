import typer
from pathlib import Path
from rich import print
from rich.progress import Progress, SpinnerColumn, TextColumn

from util import vision, lines_from_paragraphs, find_next_word, vision_to_alto

app = typer.Typer()

def main(path: str = typer.Argument(..., help="Path to the image file"), apikey: str = typer.Option(..., envvar="VISION_KEY", help="Google Vision API Key")):
    """
    🤩 escriptorium-vision 🤩
    A CLI for using Google Vision API to extract text from images and create ALTO XML files.
    """
    path = Path(path)
    if path.exists() and path.is_file():
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            transient=True,
            ) as progress:
                progress.add_task(description="Transcribiendo actualmente...", total=None)
                response = vision(str(path),apikey)
                filename = str(path).split('/')[-1]
                xml = vision_to_alto(filename,response)
                # save to disk
                with open(f'{str(path).split(".")[-2]}.xml', 'w') as f:
                    f.write(xml)
                    print(f"[bold green_yellow] 🤩 Transcrito el archivo {path}[/bold green_yellow]")
    elif path.exists() and path.is_dir():
        print(f"[bold green] 🤩 Opening portal to {path}, {apikey} [/bold green]")
    else:
        print(f"[bold purple] 💀 Path {path} does not exist[/bold purple]")
        raise typer.Exit(code=1)
    
if __name__ == "__main__":
    typer.run(main)