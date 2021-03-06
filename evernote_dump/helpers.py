#/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import re # Added by Chris2fr
from unidecode import unidecode
from language import translation

def checkForDouble(path, filename):
    '''
    # Make sure the path has a trailing /
    # Check file path and modifies it if a duplicate is found.
    # Used for creating new files.
    # Works with file extensions too.
            
    path: to desired save point
    
    returns: an updated path if path double found
    '''
    doubleCounter = 2
    tempFileName = filename 
    while os.path.exists(path + tempFileName):
        if len(filename.rsplit('.',1)) > 1:
            tempFileName = filename.rsplit('.', 1)[0] + \
                          '-' + str(doubleCounter) + '.' + \
                          filename.rsplit('.', 1)[1]
        else:
            tempFileName += '-' + str(doubleCounter)
        doubleCounter += 1
    return tempFileName

def isPythonThree():
    if sys.version_info[:2] <= (2, 7):
        return False 
    else:
        return True

def isYesNo(phrase,default = None):
    '''
    # Ask as yes/no question and have the input check and turned into
    # a boolean. Compatible with all versions of Python.

    phrase: Yes/No phrase you would like to get input from user for

    returns: True for yes, False for no
    '''
    prompt = "%s [y/n]" % (lang(phrase))
    if default:
        prompt += " (%s)" % (default)
    while True:
        if isPythonThree():
            result = str(input(prompt))
        else:
            result = str(raw_input(prompt))

        if not result and default:
            result = default

        if result.lower() == 'yes' or result.lower() == 'y':
            return True
        elif result.lower() == 'no' or result.lower() == 'n':
            return False


def lang(phrase):
        if phrase in translation[selang]:
            return translation[selang][phrase]
        else:
            return phrase + " (NEEDS TRANSLATION)"

def set_lang(lang = 'en'):
    global selang
    selang = lang

def chooseLanguage(default = 'en'):
    global selang
    phrase = ''
    counter = 1
    languages = []
    for language in sorted(translation.keys()):
        phrase += '[' + language + '] ' + translation[language]['_language_name']
        if language == default:
            phrase += "*"
        phrase += ' '
        languages.append(language)
        counter += 1

    if sys.version_info[:2] <= (2, 7):
        result = raw_input(phrase)
    else:
        result = input(phrase)

    if result in translation:
        selang = result
    else:
        selang = default
        
def makeDirCheck(path):
    '''
    # Check if path exists. If not found path is created
    # and the path is returned.  

    path: location of new directory
    
    returns: path
    '''
    if not os.path.exists(path):
        os.makedirs(path)

    return path

def multiChoice(inTuple):
    '''
    # Input a Tuple of choices.
    # Returns the user's choice as tuple entry
    '''
    phrase = ''
    for i in range(len(inTuple)):
        phrase += inTuple[i] + '[' + str(i+1) + '] '

    while True:
        if sys.version_info[:2] <= (2, 7):
            result = int(raw_input(phrase))
        else:
            result = int(input(phrase))

        if result >= 0 and result < len(inTuple):
            return result

def urlSafeString(text):
    retval = re.sub(r"[^A-z0-9-]","_",unidecode(text))[:26].lower()
    while len(retval) > 10 and retval[1] == "-":
        retval = retval[1:]
    while len(retval) > 10 and retval[-1] == '_' or retval[-1] == '-':
        retval = retval[:-1]
    return retval

def list_to_yaml(name, list):
    return list_to_text(name, list, name + ": [", "", ", ", "]  \n")
    retval = ""
    if len(list) is 0:
        return ""
    retval += name + ": ["
    for item in list:
        retval += re.sub(r'^[^-]*-','',urlSafeString(item))
        #retval += urlSafeString(list[i])
        retval += ", "
    return retval[:-2] + "]  \n"

def list_to_text_tags(name, list):
    return list_to_text(name, list, "", "#", " ", "  \n")

def list_to_text(name, list, begin, prefix, suffix, end):
    retval = ""
    if len(list) is 0:
        return ""
    retval += begin
    for item in list:
        retval += prefix
        retval += re.sub(r'^[^-]*-','',urlSafeString(item))
        #retval += urlSafeString(list[i])
        retval += suffix
    return retval[:-len(suffix)] + end

