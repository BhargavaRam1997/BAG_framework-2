# -*- coding: utf-8 -*-
########################################################################################################################
#
# Copyright (c) 2014, Regents of the University of California
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without modification, are permitted provided that the
# following conditions are met:
#
# 1. Redistributions of source code must retain the above copyright notice, this list of conditions and the following
#   disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the
#    following disclaimer in the documentation and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES,
# INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
# WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#
########################################################################################################################

"""This module handles file related IO.
"""

from __future__ import (absolute_import, division,
                        print_function, unicode_literals)
# noinspection PyUnresolvedReferences,PyCompatibility
from builtins import *

import os
import tempfile
import time
import pkg_resources
import codecs

import yaml

from .common import bag_encoding, bag_codec_error


def open_file(fname, mode):
    """Opens a file with the correct encoding interface.

    Use this method if you need to have a file handle.

    Parameters
    ----------
    fname : string
        the file name.
    mode : string
        the mode, either 'r', 'w', or 'a'.

    Returns
    -------
    file_obj : file
        a file objects that reads/writes string with the BAG system encoding.
    """
    if mode != 'r' and mode != 'w' and mode != 'a':
        raise ValueError("Only supports 'r' or 'w' mode.")
    return open(fname, mode, encoding=bag_encoding, errors=bag_codec_error)


def read_file(fname):
    """Read the given file and return content as string.

    Parameters
    ----------
    fname : string
        the file name.

    Returns
    -------
    content : unicode
        the content as a unicode string.
    """
    with open_file(fname, 'r') as f:
        content = f.read()
    return content


def readlines_iter(fname):
    """Iterate over lines in a file.

    Parameters
    ----------
    fname : string
        the file name.

    Yields
    ------
    line : unicode
        a line in the file.
    """
    with open_file(fname, 'r') as f:
        for line in f:
            yield line


def read_yaml(fname):
    """Read the given file using YAML.

    Parameters
    ----------
    fname : string
        the file name.

    Returns
    -------
    content : Any
        the object returned by YAML.
    """
    with open_file(fname, 'r') as f:
        content = yaml.load(f)

    return content


def read_resource(package, fname):
    """Read the given resource file and return content as string.

    Parameters
    ----------
    package : string
        the package name.
    fname : string
        the resource file name.

    Returns
    -------
    content : unicode
        the content as a unicode string.
    """
    raw_content = pkg_resources.resource_string(package, fname)
    return raw_content.decode(encoding=bag_encoding, errors=bag_codec_error)


def write_file(fname, content, append=False, mkdir=True):
    """Writes the given content to file.

    Parameters
    ----------
    fname : string
        the file name.
    content : unicode
        the unicode string to write to file.
    append : bool
        True to append instead of overwrite.
    mkdir : bool
        If True, will create parent directories if they don't exist.
    """
    if mkdir:
        fname = os.path.abspath(fname)
        dname = os.path.dirname(fname)
        if not os.path.exists(dname):
            os.makedirs(dname)

    mode = 'a' if append else 'w'
    with open_file(fname, mode) as f:
        f.write(content)


def make_temp_dir(prefix, parent_dir=None):
    """Create a new temporary directory.

    Parameters
    ----------
    prefix : string
        the directory prefix.
    parent_dir : string
        the parent directory.
    """
    prefix += time.strftime("_%Y%m%d_%H%M%S")
    parent_dir = parent_dir or tempfile.gettempdir()
    return tempfile.mkdtemp(prefix=prefix, dir=parent_dir)


def open_temp(**kwargs):
    """Opens a new temporary file for writing with unicode interface.

    Parameters
    ----------
    kwargs : dict[string, any]
        the tempfile keyword arguments.  See documentation for
        :func:`tempfile.NamedTemporaryFile`.

    Returns
    -------
    file : file
        the opened file that accepts unicode input.
    """
    timestr = time.strftime("_%Y%m%d_%H%M%S")
    if 'prefix' in kwargs:
        kwargs['prefix'] += timestr
    else:
        kwargs['prefix'] = timestr
    temp = tempfile.NamedTemporaryFile(**kwargs)
    return codecs.getwriter(bag_encoding)(temp, errors=bag_codec_error)
