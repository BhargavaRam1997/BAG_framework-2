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

"""This module provides functions needed to get Virtuoso to work with BAG.
"""
from __future__ import (absolute_import, division,
                        print_function, unicode_literals)
# noinspection PyUnresolvedReferences,PyCompatibility
from builtins import *

import os
import sys
import atexit
import signal
import argparse

import bag.interface
import bag.io


def run_skill_server(args):
    """Run the BAG/Virtuoso server."""
    error_msg = ''
    server = None
    port_file = None
    port_number = None

    try:
        # process command line arguments
        min_port = args.min_port
        max_port = args.max_port
        # remove directory from port file name
        port_file = os.path.basename(args.port_file)
        log_file = args.log_file

        # create log file directory, and remove old log.
        if log_file is not None:
            log_file = os.path.abspath(log_file)
            log_dir = os.path.dirname(log_file)
            if not os.path.exists(log_dir):
                os.makedirs(log_dir)
            elif os.path.exists(log_file):
                os.remove(log_file)

        # determine port file name
        if 'BAG_WORK_DIR' not in os.environ:
            raise Exception('Environment variable BAG_WORK_DIR not defined')
        work_dir = os.environ['BAG_WORK_DIR']
        if not os.path.isdir(work_dir):
            raise Exception('$BAG_WORK_DIR = %s is not a directory' % work_dir)

        port_file = os.path.join(work_dir,  port_file)

        # determine temp directory
        tmp_dir = None
        if 'BAG_TEMP_DIR' in os.environ:
            tmp_dir = os.environ['BAG_TEMP_DIR']
            if not os.path.isdir(tmp_dir):
                if os.path.exists(tmp_dir):
                    raise Exception('$BAG_TEMP_DIR = %s is not a directory' % tmp_dir)
                else:
                    os.makedirs(tmp_dir)

        # attempt to open port and start server
        router = bag.interface.ZMQRouter(min_port=min_port, max_port=max_port, log_file=log_file)
        server = bag.interface.SkillServer(router, sys.stdout, sys.stdin, tmpdir=tmp_dir)
        port_number = router.get_port()
    except Exception as ex:
        error_msg = 'bag server process error:\n%s\n' % str(ex)

    if not error_msg:
        bag.io.write_file(port_file, '%r\n' % port_number)

        # TODO: somehow this is a bug??!! figure it out.
        # make sure port_file is removed at exit
        # def exit_handler():
        #     if os.path.exists(port_file):
        #         os.remove(port_file)

        # atexit.register(exit_handler)
        # signal.signal(signal.SIGTERM, exit_handler)

        try:
            server.run()
        except Exception as ex:
            error_msg = 'bag server process error:\n%s\n' % str(ex)

    if error_msg:
        sys.stderr.write(error_msg)
        sys.stderr.flush()


def parse_command_line_arguments():
    """Parse command line arguments, then run the corresponding function."""

    desc = 'A Python program that performs tasks for virtuoso.'
    parser = argparse.ArgumentParser(description=desc)
    desc = 'Valid commands.  Supply -h/--help flag after the command name to learn more about the command.'
    sub_parsers = parser.add_subparsers(title='Commands', description=desc, help='command name.')

    desc = 'Run BAG skill server.'
    par2 = sub_parsers.add_parser('run_skill_server', description=desc, help=desc)

    par2.add_argument('min_port', type=int, help='minimum socket port number.')
    par2.add_argument('max_port', type=int, help='maximum socket port number.')
    par2.add_argument('port_file', type=str, help='file to write the port number to.')
    par2.add_argument('log_file', type=str, nargs='?', default=None,
                      help='log file name.')
    par2.set_defaults(func=run_skill_server)

    args = parser.parse_args()
    args.func(args)


if __name__ == '__main__':
    parse_command_line_arguments()
