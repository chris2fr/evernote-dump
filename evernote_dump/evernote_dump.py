#!/usr/bin/env python
# -*- coding: utf-8 -*-

#############
## IMPORTS ##
#############

import sys
import xml.sax # Steaming XML data for use with larger files
import argparse # Added by chris2fr
import re
from note import Note, Attachment
from helpers import isYesNo, chooseLanguage, lang, isPythonThree, urlSafeString, set_lang
from language import translation

############################
## Note Handler Functions ##
############################
class NoteHandler( xml.sax.ContentHandler ):
    def __init__(self):
        self.CurrentData = ""
        self.in_note_attributes = False
        self.in_resource_attributes = False
        self.__prefix_filename = ""
        self.__prefix_date = False
    
    def set_prefix_filename(self, prefix_filename = ""):
        self.__prefix_filename = prefix_filename
    
    def set_prefix_date(self, prefix_date = False):
        self.__prefix_date = prefix_date
    
    ########################
    ## ELEMENT READ START ##
    ########################
    def startElement(self, tag, attributes):
        '''
        Called when a new element is found
        '''
        self.CurrentData = tag
        if tag == "en-export": # First tag found in .enex file
            print("\n####%s####" % (lang("_export_started")))
        elif tag == "note": # New note found
            self.note = Note()
            self.note.set_path(current_file)
            self.note.set_prefix_filename(self.__prefix_filename)
            self.note.set_prefix_date(self.__prefix_date)
        elif tag == "data": # Found an attachment
            self.attachment = Attachment()
            self.attachment.set_path(current_file)
            self.attachment.set_created_date(self.note.get_created_date())
            self.attachment.set_filename(self.note.get_title())
            self.attachment.set_uuid(self.note.get_uuid())
            self.attachment.set_media_path(self.note.get_media_path())
        elif tag == "note-attributes":
            self.in_note_attributes = True
        elif tag == "resource-attributes":
            self.in_resource_attributes = True
    
    #########################
    ## ELEMENT READ FINISH ##
    #########################
    def endElement(self, tag):
        if tag == "title":
            print("\n%s: %s" % ( lang('_note_processing'), self.note.get_title()))
        elif tag == "content":
            pass
        elif tag == "resource":
            print("---%s: %s" % (lang('_exporting_attachment'), self.attachment.get_filename()))
            self.attachment.finalize(keep_file_names)
            self.in_resource_attributes = False
        elif tag == "data":
            self.note.add_attachment(self.attachment)
        elif tag == "note": # Last tag called before starting a new note
            #TODO ask user if they want to use qownnotes style. i.e. make attachment links "file://media/aldskfj.png"
            print("---%s: %s" % (lang('_exporting_note'), self.note.get_filename()))
            self.note.finalize()
        elif tag == "note-attributes":
            self.in_note_attributes = False
        elif tag == "en-export": #Last tag closed in the whole .enex file
            print("\n####%s####\n" % (lang('_export_finished')))

    #########################
    ## CONTENT STREAM READ ##
    #########################
    def characters(self, content_stream):
        if self.CurrentData == "title":
            self.note.set_title(content_stream)
        elif self.CurrentData == "content":
            self.note.append_html(content_stream)
        elif self.CurrentData == "created":
            self.note.set_created_date(content_stream)
        elif self.CurrentData == "updated":
            self.note.set_updated_date(content_stream)
        elif self.CurrentData == "tag":
            self.note.append_tag(content_stream)
        elif self.CurrentData == "data":
            self.attachment.data_stream_in(content_stream)
        elif self.CurrentData == "mime":
            self.attachment.set_mime(content_stream)
        elif self.CurrentData == "file-name":
            self.attachment.set_filename(content_stream)
        
        if self.in_note_attributes:
            self.note.add_found_attribute(self.CurrentData, content_stream)
        if self.in_resource_attributes:
            self.attachment.add_found_attribute(self.CurrentData, content_stream)

def filename_format(format_str):
    """
    Verifies the format of the format string:
    n : original filename
    d : file date in yymmdd format
    c : category (the name of the ENEX file by default)
    """
    allowed = ['%c','%d','%n','%%']
    for c in re.findall(r'(%.)',format_str,re.S):
        if c not in allowed:
            return False
    return format_str

if ( __name__ == "__main__"):
    """
    Main execution function to be called from the command-line.
    #TODO set up flags for the different parameters :
    - keep_file_names
    - prefix_string
    - prefix_date
    - choose_language
    """
    
    if not isPythonThree():
        print("Please use Python version 3")
        sys.exit()
    
    parser = argparse.ArgumentParser(description='Convert Evernote .ENEX file to .MD Files.')
    parser.add_argument('enexfile', type=argparse.FileType('r'),
                        help="ENEX File to Export")
    parser.add_argument('--lang', dest='lang', type=str, choices=translation.keys(), default="en",
                        help="Two-Letter Language Code")
    parser.add_argument('--filenameformat',dest='filename_format', type=filename_format, default='%c-%d-%n.md',
                        help="""This format is composed of three elements :
                        %c : category
                        %d : date (YYMMDD)
                        %n : the original file title
                        """)
    parser.add_argument('--cat',type=str,dest='category',default=None,
                        help="Category. By default, the name of the ENEX File.")
    parser.add_argument('--no-cat',dest='ignore_category',action='store_true',
                        help="Ignore Categories")
    parser.add_argument('--no-appendtags',dest='ignore_append_tags',action='store_true',
                        help="Ignore Appending the Tags with # at the End of Each File")
    parser.add_argument('--no-frontmatter',dest='ignore_front_matter',action='store_true',
                        help="Include YAML Frontmatter")
    parser.add_argument('-i','--interactive', dest='interactive', action='store_false',
                        help='Silent Non-Interactive Mode')
    args = parser.parse_args()

    print(args)

    prefix_enex_filename = args.filename_format
    prefix_date_filename = args.filename_format
    keep_file_names = args.filename_format
    if args.lang is not None:
        set_lang(args.lang)
    else:
        set_lang()

    # create an XMLReader
    parser = xml.sax.make_parser()

    # turn off namespaces
    parser.setFeature(xml.sax.handler.feature_namespaces, 0)

    #override the default ContextHandler
    Handler = NoteHandler()
    parser.setContentHandler( Handler )
    
    for i in range(1,len(sys.argv)):
        # pass in first argument as input file.
        if ".enex" in sys.argv[i]:
            if prefix_enex_filename:
                Handler.set_prefix_filename(urlSafeString(sys.argv[i].split('/')[-1].replace(".enex",''))[:10] + "-")
            # print(prefix_enex_filename)
            Handler.set_prefix_date(prefix_date_filename)
            current_file = sys.argv[i].replace(".enex", "/")
            #try:
            parser.parse(sys.argv[i])
            #except:
                #print(sys.argv[i] + " was unable to be parsed correctly.")
