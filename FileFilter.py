import configparser
import os
import sys
import re
import time
import pprint
import logging
import traceback
import csv

# global parameter
g_param = {\
    # Location
    'SRC_DIR'                   ='',
    'OUT_DIR'                   ='',
    # File name
    'FIX_SORTING'               ='',
    'FIX_SORTING_INDEX'         ='',
    'FIX_DATETIME_FORMAT'       ='',
    'FIX_DATETIME_INDEX'        ='',
    'FIX_DATETIME_START'        ='',
    'FIX_DATETIME_END'          ='',
    'FIX_MATCH_PATTERN'         ='',
    # File property
    'FILE_FILTER_START_TIME'    ='',
    'FILE_FILTER_END_TIME'      ='',
    'FILE_FILTER_SIZE'          ='',
    'FILE_FILTER_FORMAT'        ='',
    # File operation
    'OP_SINGLE_FOLDER'          ='',
    'OP_MOVE'                   ='',
    'OP_FIX_DATETIME_LATEST'    ='',
    'OP_FILE_DATETIME_LATEST'   ='',
    # Ini
    'CONFIG_FILE'               ='',
    'INI_SECTION'               ='',
    # Log
    'LOG_FILE'                  ='',
    'LOGGING_COLLECT'           ='',
    'LOGGING_IGNORE'            ='',
    'LOGGING_DISCARD'           ='',
    }

# program parameter
g_program = {\
    'VERSION'                   ='V.1.0.0.0',
    'USAGE_NORMAL'              ="""
Develop by ThinkRain, using MIT License.
Version V.1.0.0.0
Usage:  FileFilter [[options]=properties]

Show manual:
    -h or --help       -- print options info
    
Set params in command line:
    # Location
    -src= or --src_dir=
        set directory path which you want to filter files.
    -out= or --out_dir=
        set directory path which you want to store files.
    # File name
    -fs= or --fix_sorting=
        set path of txt file containing sorting string like:
        ### txt file ###
        A10
        A12
        A20
        B30
        B30
        ### txt file ###
    -fsi= or --fix_sorting_index=
        set index of sorting string like 0:3, which mean 'A10' in filename like 'A10-001.log'
    -fdf= or --fix_datetime_format=
    -fdi= or --fix_datetime_index=
    -fds= or --fix_datetime_start=
    -fde= or --fix_datetime_end=
    -fmp= or --fix_match_pattern=
    # File property
    -ffst= or --file_filter_start_time=
    -ffet= or --file_filter_end_time=
    -ffs= or --file_filter_size=
    -fff= or --file_filter_format=
    # File operation
    -osf= or --op_single_folder=
    -om= or --op_move=
    -oFIXdl= or --op_fix_datetime_latest=
    -oFILEdl= or --op_file_datetime_latest=

Set params in .ini setting file and use it:
example .ini setting:
##########
[example]
src_dir = ~/data/one_part/
out_dir = ~/result/one_part/
fix_sorting = ./fix_sorting.txt
fix_sorting_index = 0:3
fix_datetime_format = yyyy-MM-dd_HH-mm-SS
fix_datetime_index = Auto
fix_datetime_start = 2018-07-17_08-00-00
fix_datetime_end = 2018-07-18_20-00-00
fix_match_pattern = ABC\d{10}\-\d{4}\-\d{2}\-\d{2}_\d{2}\-\d{2}\-\d{2}.log
file_filter_start_time = 2018-07-17 08:00:00
file_filter_end_time = 2018-07-17 20:00:00
file_filter_size = <=10*2^20
file_filter_format = log
op_single_folder = True
op_move = False
op_fix_datetime_latest = False
op_file_datetime_latest = False
##########
then call .ini using:
    -c= or --configure=
    -s= or --section=

Logging output setting:
    -lf= or --log_file=
    -nl or --no_log
    -nli or --no_log_ignore
    -nld or --no_log_discard
    -nlc or --no_log_collect
    -r or --report
"""
    }


##### program logic #####
# 1. get params from command line or loading ini file
# 2. check params is legal or not, exit with error if not
# 3. process using setting and logging it
#########################



def parse_sys_argv(argv):
    param_map = {\
        '-src'  = 'SRC_DIR',
        '-out'  = 'OUT_DIR',
        '-fs'   = 'FIX_SORTING',
        '-fsi'  = 'FIX_SORTING_INDEX',
        '-fdf'  = 'FIX_DATETIME_FORMAT',
        '-fds'  = 'FIX_DATETIME_START',
        '-fde'  = 'FIX_DATETIME_END',
        '-fmp'  = 'FIX_MATCH_PATTERN',
        '-ffst' = 'FIX_FILTER_START_TIME',
        '-ffet' = 'FIX_FILTER_END_TIME',
        '-fff'  = 'FIX_FILTER_FORMAT',
        '-osf'  = 'OP_SINGLE_FORMAT',
        '-om'   = 'OP_MOVE',
        '-oFIXdl'   = 'OP_FIX_DATETIME_LATEST',
        '-oFILEdl'  = 'OP_FILE_DATETIME_LATEST',
        
        '--src_dir'                 = 'SRC_DIR',
        '--out_dir'                 = 'OUT_DIR',
        '--fix_sorting'             = 'FIX_SORTING',
        '--fix_sorting_index'       = 'FIX_SORTING_INDEX',
        '--fix_datetime_format'     = 'FIX_DATETIME_FORMAT',
        '--fix_datetime_start'      = 'FIX_DATETIME_START',
        '--fix_datetime_end'        = 'FIX_DATETIME_END',
        '--fix_match_patch'         = 'FIX_MATCH_PATTERN',
        '--fix_filter_start_time'   = 'FIX_FILTER_START_TIME',
        '--fix_filter_end_time'     = 'FIX_FILTER_END_TIME',
        '--fix_filter_format'       = 'FIX_FILTER_FORMAT',
        '--op_single_format'        = 'OP_SINGLE_FORMAT',
        '--op_move'                 = 'OP_MOVE',
        '--op_fix_datetime_latest'  = 'OP_FIX_DATETIME_LATEST',
        '--op_file_datetime_latest' = 'OP_FILE_DATETIME_LATEST',
        }

    # set program params
    for s in argv:
        a = s.split('=',1)
        if len(a) == 2:
            g_param[a[0]] = a[1]
        else:
            pass
    pass


def load_ini():
    
