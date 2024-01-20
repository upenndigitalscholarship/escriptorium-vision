import typer
from pathlib import Path
from rich import print
from rich.progress import Progress, SpinnerColumn, TextColumn, track
import srsly 
from util import vision, lines_from_paragraphs, find_next_word, vision_to_alto
from escriptorium_connector import EscriptoriumConnector
from util import vision, merge_vision_alto
from zipfile import ZipFile
import io
from io import BytesIO
import zipfile
from PIL import Image
import base64

app = typer.Typer()

def main(): 
    """
    🤩 escriptorium-vision 🤩
    A CLI for using Google Vision API to extract text from images and create ALTO XML files.
    """
    if Path("secrets.json").exists():
        secrets = srsly.read_json("secrets.json")
    else:
        secrets = {}
        secrets['VISION_KEY'] = input("Please enter your Google Vision API Key: ")
        secrets['ESCRIPTORIUM_URL'] = input("Please enter your Escriptorium Url: ") or 'https://escriptorium.pennds.org/'
        secrets['ESCRIPTORIUM_USERNAME'] = input("Please enter your Escriptorium Username: ") or 'invitado'
        secrets['ESCRIPTORIUM_PASSWORD'] = input("Please enter your Escriptorium Password: ")
        srsly.write_json("secrets.json", secrets)

    # using the eScriporium info, fetch as list of documents
    try: 
        E = EscriptoriumConnector(secrets['ESCRIPTORIUM_URL'], secrets['ESCRIPTORIUM_USERNAME'], secrets['ESCRIPTORIUM_PASSWORD'])
        documents = E.get_documents()
        
        # create a menu for the user to select a document from the results
        document_names = [d.name for d in documents.results]
        for i, name in enumerate(document_names):
            print(f"[bold green_yellow]{i}[/bold green_yellow] [bold white]{name}[/bold white]")
        document_name = typer.prompt("Please select a document to transcribe")
        # if the user enters a number, use that to select the document
        if document_name.isdigit():
            document = documents.results[int(document_name)]
            print(f"[bold green_yellow] 🤩 Transcribing {document.name}...[/bold green_yellow]")
            
            # Select relevant transcription/segmentation to process
            transcriptions = E.get_document_transcriptions(document.pk)
            # prompt user to select a transcription
            for i, t in enumerate(transcriptions):
                print(f"[bold green_yellow]{i}[/bold green_yellow] [bold white]{t.name}[/bold white]")
            transcription_name = typer.prompt("Please select a transcription to transcribe")
            if transcription_name.isdigit():
                transcription_pk = transcriptions[int(transcription_name)].pk
                transcription_name = transcriptions[int(transcription_name)].name
        
            # Process each page of the selected document
            parts = E.get_document_parts(document.pk)
            for page in parts.results:
                filename = page.filename
                img_binary = E.get_document_part_image(document.pk, page.pk)
                #convert img_binary to jpg and base64
                # It is important to use the part image because the alto line coordinates are based on this file, not the jpg thumbnail
                img = Image.open(io.BytesIO(img_binary))
                rgb_im = img.convert("RGB")
                img_byte_arr = io.BytesIO()
                rgb_im.save(img_byte_arr, format='JPEG')
                image_content = base64.b64encode(img_byte_arr.getvalue())
                vision_response = vision(image_content,secrets['VISION_KEY'])

                # get the alto xml for the page
                alto_xml = E.download_part_alto_transcription(document.pk,page.pk,transcription_pk)
                #You will need to unzip these bytes in order to access the XML data (zipfile can do this).
                with ZipFile(BytesIO(alto_xml)) as z:
                    with z.open(z.namelist()[0]) as f:
                        alto_xml = f.read()
                merged = merge_vision_alto(vision_response,alto_xml)
                #print(filename, img_src, type(img_binary),alto_xml)  

                #upload_part_transcription(document_pk: int, transcription_name: str, filename: str, file_data: BytesIO, override: str = "off",)        
        else:
            print("💀 Please enter a number")
        
            
        
    except Exception as e:
        print(f"[bold purple] 💀 Error connecting to Escriptorium: {e}[/bold purple] Please check that your login information is correct.")
        raise typer.Exit(code=1)
    
def old_main(path: str = typer.Argument(..., help="Path to the image file"), apikey: str = typer.Option(..., envvar="VISION_KEY", help="Google Vision API Key")):
    """
    🤩 escriptorium-vision 🤩
    A CLI for using Google Vision API to extract text from images and create ALTO XML files.
    """
    path = Path(path)
    if path.exists() and path.is_file() and path.suffix in ['.jpg','.png','.jpeg']:
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
        images = [f for f in path.rglob("*") if f.is_file() and f.suffix.lower() in ['.jpg','.png','.jpeg']]
        for img in track(images, description="Transcribiendo actualmente..."):
            response = vision(str(img),apikey)
            filename = str(img).split('/')[-1]
            xml = vision_to_alto(filename,response)
            # save to disk
            with open(f'{str(img).split(".")[-2]}.xml', 'w') as f:
                f.write(xml)
    else:
        print(f"[bold purple] 💀 Path {path} does not exist[/bold purple]")
        raise typer.Exit(code=1)
#TODO push all transcripts to escriptorium using connector
    

if __name__ == "__main__":
    typer.run(main)