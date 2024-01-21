# <img height="30px" src="moon-mustache.png" /> eScriptorium-Vision 

This is a command line tool that uses Google Vision to perform HTR on images in eScriptorium. You will need to upload your images to eScriptorium first and run segmentation. We recommend that you manually correct segmentation in eScriptorium. Then this tool can fetch the images and segmentation from eScriptorium, run HTR on the images, and upload the transcriptions back to eScriptorium. Doing this process can significantly reduce the amount of time needed to transcribe a document. Rather than adding text manually, you can upload an automatic transcription and then correct it in eScriptorium.  

Please note that you will need to create an account for Google Vision and this is a paid and proprietary product. You will also need an existing account on an eScriptorium instance. See the instructions below for more information.

## Installation:

Create a virtual environment and install the requirements:

1. Download the whl file from the [releases page](https://github.com/upenndigitalscholarship/escriptorium-vision/releases) or [here](https://github.com/upenndigitalscholarship/escriptorium-vision/releases/download/escriptorium/escriptorium_vision-0.1.0-py3-none-any.whl)
2. Install with pip:
    ```bash 
    pip install escriptorium_vision-0.1.0-py3-none-any.whl
    ```
## Set Secrets:

The first time that you use this tool, you will be asked for some information. This information will be stored in a file called `secrets.json` in the root directory of the project. You can edit this file at any time to change the information. To delete the file, use the tag `--clear-secrets`.    

### Google Vision API key
This tool uses Google Vision to perform OCR on the images. You will need to create a Google Cloud account and enable the Vision API. Then, you will need to create a service account and download the key. You can find instructions for doing this [here](https://cloud.google.com/vision/docs/setup). You can then create an API key using these [instructions](https://support.google.com/googleapi/answer/6158862?hl=en). Once you have the key, you can enter it in the terminal when prompted or edit the `secrets.json` file directly.

### eScriptorium url
This tool connects to eScriptorium to fetch images and upload the transcriptions. You need to have an existing account on an eScriptorium instance. You will need to enter the url (`https://escriptorium.pennds.org`) of the instance when prompted or edit the `secrets.json` file directly. 

### eScriptorium username
This is the username that you use to log into eScriptorium. You will need to enter it when prompted or edit the `secrets.json` file directly.

### eScriptorium password
This is the password that you use to log into eScriptorium. You will need to enter it when prompted or edit the `secrets.json` file directly.

