# eScriptorium-Vision

Una herramienta para transcribir imágenes automáticamente con Google Vision y guardarlas en ALTOXml para importarlas a eScriptorium

Segment image using kraken?

Or download corrected segmentation from eScriptorium?


Then match Vision text to line segments? 
Would that then be valid XML for model training? Or is there some other problem? 


push/pull to eScriptorium

input:
escriptorium login info [ or local folder of images ]
document id or name 

interaction:
connect to eScriptorium, list documents
select document
fetch images from eScriptorium
fetch segmentation from eScriptorium (allows manual corrections)

pass images to Vision
match Vision text to line segments
push transcription back to eScriptorium

output:
document in eScriptorium with transcription from Vision


