#!/usr/bin/env python

'''
    Metadata anonymisation toolkit library
'''

import os
import subprocess
import logging
import mimetypes

import hachoir_core.cmd_line
import hachoir_parser

import images
import audio
import office
import archive

__version__ = '0.1'
__author__ = 'jvoisin'

LOGGING_LEVEL = logging.DEBUG

logging.basicConfig(level=LOGGING_LEVEL)

STRIPPERS = {
    'application/x-tar': archive.TarStripper,
    'application/x-gzip': archive.GzipStripper,
    'application/x-bzip2': archive.Bzip2Stripper,
    'application/zip': archive.ZipStripper,
    'audio/mpeg': audio.MpegAudioStripper,
    'image/jpeg': images.JpegStripper,
    'image/png': images.PngStripper,
    'application/x-pdf ': office.PdfStripper,
    'application/vnd.oasis.opendocument': office.OpenDocumentStripper,
}

try:
    import mutagen
    STRIPPERS['audio/x-flac'] = audio.FlacStripper
except ImportError:
    print('unable to import python-mutagen : limited audio format support')

def secure_remove(filename):
    '''
        securely remove the file
    '''
    try:
        subprocess.call('shred --remove %s' % filename, shell=True)
    except:
        logging.error('Unable to remove %s' % filename)


def is_secure(filename):
    '''
        Prevent shell injection
    '''
    if not(os.path.isfile(filename)):  # check if the file exist
        logging.error('%s is not a valid file' % filename)
        return False
    else:
        return True


def create_class_file(name, backup, add2archive):
    '''
        return a $FILETYPEStripper() class,
        corresponding to the filetype of the given file
    '''
    if not is_secure(name):
        return

    filename = ''
    realname = name

    try:
        filename = hachoir_core.cmd_line.unicodeFilename(name)
    except TypeError:  # get rid of "decoding Unicode is not supported"
        filename = name

    parser = hachoir_parser.createParser(filename)
    if not parser:
        logging.info('Unable to parse %s' % filename)
        return

    mime = parser.mime_type

    if mime.startswith('application/vnd.oasis.opendocument'):
        mime = 'application/vnd.oasis.opendocument'  # opendocument fileformat

    try:
        stripper_class = STRIPPERS[mime]
    except KeyError:
        logging.info('Don\'t have stripper for %s\' format' % filename)
        return

    return stripper_class(filename, parser, mime, backup, add2archive)
