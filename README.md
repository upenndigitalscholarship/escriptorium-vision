# <img height="30px" src="moon-mustache.png" /> eScriptorium-Vision 

eScriptorium-Vision is a command line tool that uses Google Vision to perform HTR on images in eScriptorium. You will need to upload your images to eScriptorium. This tool can fetch the images from eScriptorium, run HTR on the images, and upload the transcriptions back to eScriptorium. Doing this process can significantly reduce the time needed to transcribe a document. Rather than manually adding text, you can upload an automatic transcription and correct it in eScriptorium.  

Please note that you will need to create an account for Google Vision, and this is a paid and proprietary product. You will also need an existing account on an eScriptorium instance. See the instructions below for more information.

## Installation:

Create a virtual environment and install the requirements:

1. Download the whl file from the [releases page](https://github.com/upenndigitalscholarship/escriptorium-vision/releases) or [here](https://github.com/upenndigitalscholarship/escriptorium-vision/releases/download/escriptorium/escriptorium_vision-0.1.0-py3-none-any.whl)
2. Install with pip:
    ```bash 
    pip install escriptorium_vision-0.1.0-py3-none-any.whl
    ```
3. You can now run the tool with the command `transcribe` in the terminal.
```bash
(venv) $ transcribe
```

> This tool requires that your images be segmented in order to add the transcription. If you images have not been segmented, you can run segmentation on your eScriptorium server or use the `--local-segment` tag to run segmentation locally.

## Set Secrets:

You will be asked for some information the first time you use this tool. This information will be stored in a file called `secrets.json` in the root directory of the project. You can edit this file at any time to change the information. To delete the file, use the tag `--clear-secrets`.    

### Google Vision API key
This tool uses Google Vision to perform OCR on the images. You must create a Google Cloud account and enable the Vision API. You can find instructions for doing this [here](https://cloud.google.com/vision/docs/setup). You can then make an API key using these [instructions](https://support.google.com/googleapi/answer/6158862?hl=en). Once you have the key, enter it in the terminal when prompted or edit the `secrets.json` file directly.

### eScriptorium url
This tool connects to eScriptorium to fetch images and upload the transcriptions. You need to have an existing account on an eScriptorium instance. You must enter the URL (`https://escriptorium.pennds.org`) of the instance when prompted or edit the `secrets.json` file directly. 

### eScriptorium username
This is the username that you use to log into eScriptorium. You must enter it when prompted or edit the `secrets.json` file directly.

### eScriptorium password
This is the password that you use to log into eScriptorium. You must enter it when prompted or edit the `secrets.json` file directly.