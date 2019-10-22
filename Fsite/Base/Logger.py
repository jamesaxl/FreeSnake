# -*- coding: utf-8 -*-

'''
FCP API in Python created by James Axl 2018

For FCP documentation, see http://wiki.freenetproject.org/FCPv2 still under construction
'''
import logging

LOGGER = logging.getLogger('FWebSite')
LOGGER.setLevel(logging.DEBUG)
FORMATTER = logging.Formatter('%(levelname)s %(asctime)s %(message)s')
CSL_STRM = logging.StreamHandler()
CSL_STRM.setFormatter(FORMATTER)
LOGGER.addHandler(CSL_STRM)
