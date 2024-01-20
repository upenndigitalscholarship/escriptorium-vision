import json
from lxml import etree
from xml.etree.ElementTree import Element, SubElement, tostring
import base64
from googleapiclient.discovery import build
from pathlib import Path
import os 
from io import StringIO, BytesIO

def vision(image_content:str, APIKEY:str, type_:str = 'DOCUMENT_TEXT_DETECTION', language:str = 'es'):
    vservice = build('vision', 'v1', developerKey=APIKEY)
    language = language
    request = vservice.images().annotate(body={
             'requests': [{
                           'image': {
                                     'content': image_content.decode('UTF-8')
                                    },
                           'imageContext': {
                                     'languageHints': [language]},
                                      'features': [{
                           'type': type_
                                        }]
                                      }]
                    })
    return request.execute(num_retries=3)
    

def lines_from_paragraphs(response:dict):
    lines = []
    blocks  = response['responses'][0]['fullTextAnnotation']['pages'][0]['blocks']
    for block in blocks:
        paragraphs = block['paragraphs']
        for paragraph in paragraphs:
            paragraph_text = ""
            for word in paragraph['words']:
                w = ""
                for symbol in word['symbols']:
                    w += symbol['text']
                paragraph_text += w + ' '
                
            lines.append({'text':paragraph_text, 'bbox':paragraph['boundingBox']})
    return lines

def find_next_word(lines:list, text:str):
    try:
        start = [t for t in lines if text.lower() in t['text'].lower()][0]
        # find the word after the start word using the x and y coordinates of the bounding box
        next = [t for t in lines if t['bbox']['vertices'][0]['x'] > start['bbox']['vertices'][0]['x'] and t['bbox']['vertices'][0]['y'] > start['bbox']['vertices'][0]['y']][0]
        return next
    except:
        return None
    
def vision_to_alto(filename:str, response:json):
    # Create the ALTO XML document
    alto = Element('alto', {'xmlns:xsi': 'http://www.w3.org/2001/XMLSchema-instance',
                            'xmlns': 'http://www.loc.gov/standards/alto/ns-v4#',
                            'xsi:schemaLocation': 'http://www.loc.gov/standards/alto/ns-v4# http://www.loc.gov/standards/alto/v4/alto-4-0.xsd'})

    # Add the Description element
    description = SubElement(alto, 'Description')
    measurement_unit = SubElement(description, 'MeasurementUnit')
    measurement_unit.text = 'pixel'
    source_image_information = SubElement(description, 'sourceImageInformation')
    file_name = SubElement(source_image_information, 'fileName')
    file_name.text = filename

    # Add the Tags element
    tags = SubElement(alto, 'Tags')
    title = SubElement(tags, 'OtherTag', {'ID': 'BT1', 'LABEL': 'Title', 'DESCRIPTION': 'block type Title'})
    main = SubElement(tags, 'OtherTag', {'ID': 'BT2', 'LABEL': 'Main', 'DESCRIPTION': 'block type Main'})
    commentary = SubElement(tags, 'OtherTag', {'ID': 'BT3', 'LABEL': 'Commentary', 'DESCRIPTION': 'block type Commentary'})
    illustration = SubElement(tags, 'OtherTag', {'ID': 'BT4', 'LABEL': 'Illustration', 'DESCRIPTION': 'block type Illustration'})
    text = SubElement(tags, 'OtherTag', {'ID': 'BT7', 'LABEL': 'text', 'DESCRIPTION': 'block type text'})
    default = SubElement(tags, 'OtherTag', {'ID': 'LT7', 'LABEL': 'default', 'DESCRIPTION': 'line type'})

    # Add the layout information
    layout = SubElement(alto, 'Layout')
    width = str(response['responses'][0]['fullTextAnnotation']['pages'][0]['width'])
    height = str(response['responses'][0]['fullTextAnnotation']['pages'][0]['height'])
    page = SubElement(layout, 'Page', {'WIDTH': width, 'HEIGHT': height, 'PHYSICAL_IMG_NR': '0', 'ID': 'eSc_dummypage_'})
    print_space = SubElement(page, 'PrintSpace', {'HPOS': '0', 'VPOS': '0', 'WIDTH': width, 'HEIGHT': height})

    # Add the text annotations as text blocks, text lines, and strings
    # For each paragraph, add words 
    lines = lines_from_paragraphs(response)
    for line in lines:
        paragraph_text = line['text']
        paragraph_bbox = line['bbox']
        text_block = SubElement(print_space, 'TextBlock', {'HPOS': str(paragraph_bbox['vertices'][0]['x']), 'VPOS': str(paragraph_bbox['vertices'][0]['y']), 'WIDTH': str(paragraph_bbox['vertices'][2]['x'] - paragraph_bbox['vertices'][0]['x']), 'HEIGHT': str(paragraph_bbox['vertices'][2]['y'] - paragraph_bbox['vertices'][0]['y']), 'ID': 'text_block_1'})
        shape = SubElement(text_block, 'Shape')
        polygon = SubElement(shape, 'Polygon', {'POINTS': ' '.join([f"{vertex['x']} {vertex['y']}" for vertex in paragraph_bbox['vertices']])})
        # generate line id
        line_id = 'line_' + str(paragraph_bbox['vertices'][0]['x']) + '_' + str(paragraph_bbox['vertices'][0]['y'])
        height_ = paragraph_bbox['vertices'][2]['y'] - paragraph_bbox['vertices'][0]['y']

        text_line = SubElement(text_block, 'TextLine', {'ID': line_id, 'BASELINE': f"{paragraph_bbox['vertices'][0]['x']} {paragraph_bbox['vertices'][0]['y']+ height_} {paragraph_bbox['vertices'][2]['x']} {paragraph_bbox['vertices'][2]['y']}", 'HPOS': str(paragraph_bbox['vertices'][0]['x']), 'VPOS': str(paragraph_bbox['vertices'][0]['y']), 'WIDTH': str(paragraph_bbox['vertices'][2]['x'] - paragraph_bbox['vertices'][0]['x']), 'HEIGHT': str(paragraph_bbox['vertices'][2]['y'] - paragraph_bbox['vertices'][0]['y'])})
        string = SubElement(text_line, 'String', {'CONTENT': paragraph_text, 'HPOS': str(paragraph_bbox['vertices'][0]['x']), 'VPOS': str(paragraph_bbox['vertices'][0]['y']), 'WIDTH': str(paragraph_bbox['vertices'][2]['x'] - paragraph_bbox['vertices'][0]['x']), 'HEIGHT': str(paragraph_bbox['vertices'][2]['y'] - paragraph_bbox['vertices'][0]['y'])})
        
    # Output the ALTO XML document
    return tostring(alto, encoding='unicode')

def get_strings_for_alto_line(vision_response:json,hpos:int,vpos:int,width:int,height:int):
    """
    Given a vision response and the coordinates of an ALTO text line, return a list of ALTO String elements that fit within the line.
    Each ALTO String element is a single word.
    HPOS = Horizontal (x) position upper/left corner
    VPOS = Vertical (y) position upper/left corner
    """
    # create a list of all the words within the line coordinates
    line_x_min = hpos
    line_x_max = hpos + width
    line_y_min = vpos
    line_y_max = vpos + height

    line_words = []
    for response in vision_response['responses']:
        for i, annotation in enumerate(response['textAnnotations']):
            if i == 0:
                full_text = annotation.get('description', None)
                language = annotation.get('locale', None)
            else:
                text = annotation.get('description', None)
                # The bounding box for the word. The vertices are in the order of top-left, top-right, bottom-right, bottom-left.
                # https://cloud.google.com/distributed-cloud/hosted/docs/latest/gdch/apis/vertex-ai/ocr/rpc/google.cloud.vision.v1
                boundingbox = annotation.get('boundingPoly', None) #'boundingPoly': {'vertices': [{'x': 22, 'y': 453}, {'x': 22, 'y': 342}, {'x': 39, 'y': 342}, {'x': 39, 'y': 453}]}
                word_x_min = boundingbox['vertices'][0]['x']
                word_x_max = boundingbox['vertices'][1]['x']
                word_y_min = boundingbox['vertices'][0]['y']
                word_y_max = boundingbox['vertices'][2]['y']\
                # if the word is within the line coordinates, add it to the list of words
                if word_x_min >= line_x_min and word_x_max <= line_x_max and word_y_min >= line_y_min and word_y_max <= line_y_max:
                    line_words.append({'text':text, 'bbox':boundingbox})
                


def merge_vision_alto(vision_response:json, alto_xml:str):
    #TODO assert that dimentions of alto xml and vision response are the same, necessary to compare coordinates

    # read the alto xml into an ElementTree
    alto = etree.XML(alto_xml)
    # find all TextLine elements 
    text_lines = alto.findall('.//{http://www.loc.gov/standards/alto/ns-v4#}TextLine')
    for line in text_lines:
        line_attrib = line.attrib #{'ID': 'eSc_line_3f31ece7', 'TAGREFS': 'LT15', 'BASELINE': '1029 797 2255 780', 'HPOS': '1026', 'VPOS': '724', 'WIDTH': '1229', 'HEIGHT': '118'}
        id = line_attrib.get('ID',None)
        baseline = line_attrib.get('BASELINE',None)
        hpos = line_attrib.get('HPOS',None) # Horizontal position upper/left corner (1/10 mm) 
        vpos = line_attrib.get('VPOS',None) # Vertical position upper/left corner (1/10 mm) 
        width = line_attrib.get('WIDTH',None)
        height = line_attrib.get('HEIGHT',None)
        text = line.text

        # remove any existing String elements from the TextLine 
        # <String CONTENT="Par " HPOS="220" VPOS="369" WIDTH="3" HEIGHT="22" />
        strings = line.findall('.//{http://www.loc.gov/standards/alto/ns-v4#}String')
        for string in strings:
            line.remove(string)

        # add new String elements from the vision response
        line_strings_with_vision_text = get_strings_for_alto_line(vision_response,hpos,vpos,width,height) 


def push_new_transcription():
    """
    Create a new transcription in eScriptorium for the document and upload the updated ALTO XML file.
    """
   pass


# <TextBlock>
# <TextLine>
# <String/>
# <SP/>
# <HYP/>
# </TextLine>
# </TextBlock>
      
    print('text lines', text_lines)
    return None


if __name__ == '__main__':
    filepath = '/home/apjanco/Pictures/SM_NPQ_C01_006_1.jpg'
    response = vision(filepath)
    #TODO, here filename needs to match the file in eScriptorium for import to work
    filename = filepath.split('/')[-1]
    xml = vision_to_alto(filename,response)
    # save to disk
    with open(f'{filepath.split(".")[-2]}.xml', 'w') as f:
        f.write(xml)