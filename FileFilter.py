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
    }

g_setting = {\
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
    -fdf= or --fix_datetime_format=             -- set python3 time format string
        %Y  Year with century as a decimal number.-
        %m  Month as a decimal number [01,12].
        %d  Day of the month as a decimal number [01,31].
        %H  Hour (24-hour clock) as a decimal number [00,23].
        %M  Minute as a decimal number [00,59].
        %S  Second as a decimal number [00,61].
        %z  Time zone offset from UTC.
        %a  Locale's abbreviated weekday name.
        %A  Locale's full weekday name.
        %b  Locale's abbreviated month name.
        %B  Locale's full month name.
        %c  Locale's appropriate date and time representation.
        %I  Hour (12-hour clock) as a decimal number [01,12].
        %p  Locale's equivalent of either AM or PM.
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
        '--fix_datetime_index'      = 'FIX_DATETIME_INDEX',
        '--fix_datetime_start'      = 'FIX_DATETIME_START',
        '--fix_datetime_end'        = 'FIX_DATETIME_END',
        '--fix_match_pattern'       = 'FIX_MATCH_PATTERN',
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
    cfg_parser = configparser.ConfigParser()
    cfg_parser.read(g_setting['CONFIG_FILE'])
    for k in g_param:
        t = cfg_parser.get(g_setting['INI_SECTION'],k.lower(),fallback='')
        t.strip()
        if len(t) >= 2:
            if t[0] == '"' and t[-1] == '"':
                t = t[1:-1]
        g_param[k] = t
    
    # check params are legal or not
    ## 1. src dir
    if not os.path.exists(g_param['SRC_DIR']):
        raise Exception(f'src_dir : {g_param["SRC_DIR"]} is not exists.')
    elif not os.path.isdir(g_param['SRC_DIR']):
        raise Exception(f'src_dir : {g_param["SRC_DIR"]} is not a directory.')
    ## 2. out dir
    if not os.path.exists(g_param['OUT_DIR']):
        raise Exception(f'out_dir : {g_param["OUT_DIR"]} is not exists.')
    elif not os.path.isdir(g_param['OUT_DIR']):
        raise Exception(f'out_dir : {g_param["OUT_DIR"]} is not a directory.')
    ## 3. fix sorting
    if not os.path.exists(g_param['FIX_SORTING']):
        raise Exception(f'fix_sorting : {g_param["FIX_SORTING"]} is not exists.')
    elif not os.path.isfile(g_param['FIX_SORTING']):
        raise Exception(f'fix_sorting : {g_param["FIX_SORTING"]} is not a file.')
    ## 4. fix sorting index
    fsi = g_param['FIX_SORTING_INDEX'].strip().split(':')
    try:
        if len(fsi) != 2:
            raise Exception()
        a = int(fsi[0].split())
        b = int(fsi[1].split())
        g_param['FIX_SORTING_INDEX'] = (a,b)
    except:
        raise Exception(f'fix_sorting_index : {g_param["FIX_SORTING_INDEX"]} being illegal format, it should be like "0:13"')
    ## 5. fix_datetime_format
    fdf = g_param['FIX_DATETIME_FORMAT'].strip()
    g_param['FIX_DATETIME_FORMAT'] = fdf
    ## 6. fix_datetime_start && 7. fix_datetime_end
    fds = g_param['FIX_DATETIME_START'].strip()
    fde = g_param['FIX_DATETIME_END'].strip()
    try:
        time.strptime(fds,fdf)
        time.strptime(fde,fdf)
    except:
        raise Exception('fix_datetime_start / fix_datetime_end\n' +
                        f'{fds} / {fde}\n' +
                        'are not match {fdf} datetime format.')
    ## 8. fix_match_pattern
    try:
        fmp = re.compile(g_param['FIX_MATCH_PATTERN'])
        g_param['FIX_MATCH_PATTERN'] = fmp
    except:
        raise Exception(f'fix_match_pattern : {g_param["FIX_MATCH_PATTERN"]} is illegal.')
    ## 9 && 10. fix_filter_start_time && fix_filter_end_time
    try:
        fmt = '%Y-%m-%d %H:%M:%S'
        if g_param['FIX_FILTER_START_TIME'].strip() != '':
            ffst = time.strptime(fmt,g_param['FIX_FILTER_START_TIME'].strip())
            g_param['FIX_FILTER_START_TIME'] = ffst
        if g_param['FIX_FILTER_END_TIME'].strip() != '':
            ffet = time.strptime(fmt,g_param['FIX_FILTER_END_TIME'].strip())
            g_param['FIX_FILTER_END_TIME'] = ffet
    except:
        raise Exception('fix_filter_start_time / fix_filter_end_time\n' +
                        f'{g_param["FIX_FILTER_START_TIME"]} / {g_param["FIX_FILTER_END_TIME"]}\n' +
                        r'are not match %Y-%m-%d %H:%M:%S datetime format.')
    ## 11. fix_filter_format
    fff = g_param['FIX_FILTER_FORMAT'].split('|')
    fs = []
    for f in fff:
        f = f.strip()
        if f != "":
            fs.append(f)
    g_param['FIX_FILTER_FORMAT'] = tuple(fs)
    ## 12. op_single_folder
    if g_param['OP_SINGLE_FOLDER'] in ['True','true','TRUE']:
        g_param['OP_SINGLE_FOLDER'] = True
    elif g_param['OP_SINGLE_FOLDER'] in ['False','false','FALSE', '']:
        g_param['OP_SINGLE_FOLDER'] = False
    else:
        raise Exception(f'op_single_folder : can\'t parse {g_param["OP_SINGLE_FOLDER"]}, please use True or False')
    ## 13. op_move
    if g_param['OP_MOVE'] in ['True', 'true', 'TRUE']:
        g_param['OP_MOVE'] = True
    elif g_param['OP_MOVE'] in ['False', 'false', 'FALSE', '']:
        g_param['OP_MOVE'] = True
    else:
        raise Exception(f'op_move : can\'t parse {g_param["OP_MOVE"]}, please use True or False')
    ## 14. op_fix_datetime_latest
    if g_param['OP_FIX_DATETIME_LATEST'] in ['True', 'true', 'TRUE']:
        g_param['OP_FIX_DATETIME_LATEST'] = True
    elif g_param['OP_FIX_DATETIME_LATEST'] in ['False', 'false', 'FALSE', '']:
        g_param['OP_FIX_DATETIME_LATEST'] = True
    else:
        raise Exception(f'op_fix_datetime_latest : can\'t parse {g_param["OP_FIX_DATETIME_LATEST"]}, please use True or False')
    ## 15. op_file_datetime_latest
    if g_param['OP_FILE_DATETIME_LATEST'] in ['True', 'true', 'TRUE']:
        g_param['OP_FILE_DATETIME_LATEST'] = True
    elif g_param['OP_FILE_DATETIME_LATEST'] in ['False', 'false', 'FALSE', '']:
        g_param['OP_FILE_DATETIME_LATEST'] = True
    else:
        raise Exception(f'OP_FILE_DATETIME_LATEST : can\'t parse {g_param["OP_FILE_DATETIME_LATEST"]}, please use True or False')
