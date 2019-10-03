# coding=utf-8

import sys,os


def get_main_path():
    return os.path.dirname(os.path.dirname(__file__))

def get_script_path():
    return os.path.dirname(os.path.dirname(__file__))+'/CXA_Script'

def get_icon_path():
    return os.path.dirname(os.path.dirname(__file__))+'/CXA_Icon'

def get_config_path():
    return os.path.dirname(os.path.dirname(__file__))+'/CXA_Confight'

def get_library_path():
    return os.path.dirname(os.path.dirname(__file__))+'/CXA_Library'

def get_rely_path():
    return os.path.dirname(os.path.dirname(__file__))+'/CXA_Rely'

def get_style_path():
    return os.path.dirname(os.path.dirname(__file__))+'/CXA_Style'

def get_uipy_path():
    return os.path.dirname(os.path.dirname(__file__))+'/CXA_UIPY'


