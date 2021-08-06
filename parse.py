#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jun  1 15:25:28 2020

@author: antonio
"""
import time
import os
import pandas as pd

def parse_ann(datapath, labels_to_ignore = [], with_notes=False):
    '''
    DESCRIPTION: parse information in .ann files.
    
    Parameters
    ----------
    datapath: str 
        Route to the folder where the files are. 
    labels_to_ignore: list 
        Brat labels I will NOT parse.
    with_notes: bool 
        Whether to store Brat AnnotatorNotes (#) or not.
            
    Returns
    -------
    df: pandas DataFrame 
        It has information from ANN files. Columns: 'annotator', 'bunch',
        'filename', 'mark', 'label', 'offset1', 'offset2', 'span', 'code'
    '''
    start = time.time()
    info = []
    ## Iterate over the files and parse them
    filenames = []
    print(datapath)
    for root, dirs, files in os.walk(datapath):
        for filename in files:
            if filename[-3:] != 'ann':
                continue
            info,_ = parse_one_ann(info, filenames, root, filename, labels_to_ignore,
                                  ignore_related=False, with_notes=with_notes)
             
    if with_notes == True:
        cols = ['annotator','bunch','filename','mark','label','offset1',
                'offset2','span','code']
    else:
        cols = ['annotator','bunch','filename','mark','label','offset1',
                'offset2','span']
    df = pd.DataFrame(info, columns=cols)
    end = time.time()
    print("Elapsed time: " + str(round(end-start, 2)) + 's')
    
    return df

def parse_one_ann(ann_info, filenames, root, filename, labels_to_ignore,
                  ignore_related=True, with_notes=False):
    '''
    Parse one ANN file
    '''
    f = open(os.path.join(root,filename)).readlines()
    filenames.append(filename)
    
    # Get annotator and bunch
    bunch = root.split('/')[-1]
    annotator = root.split('/')[-2][-1]

    # Parse .ann file
    # Parse Relations (R)
    related_marks = []     
    if ignore_related == True:   
        for line in f:
            if line[0] != 'R':
                continue
            related_marks.append(line.split('\t')[1].split(' ')[1].split(':')[1])
            related_marks.append(line.split('\t')[1].split(' ')[2].split(':')[1])
            
    # Parse Notes (#) 
    if with_notes==True:
        mark2code = {}
        for line in f:
            if line[0] != '#':
                continue
            line_split = line.split('\t')
            mark2code[line_split[1].split(' ')[1]] = line_split[2].strip()
            
    # Parse Entities (T)
    for line in f:
        if line[0] != 'T':
            continue
        splitted = line.split('\t')
        if len(splitted)<3:
            print('Line with less than 3 tabular splits:')
            print(root + filename)
            print(line)
            print(splitted)
        if len(splitted)>3:
            print('Line with more than 3 tabular splits:')
            print(root + filename)
            print(line)
            print(splitted)
        mark = splitted[0]
        if mark in related_marks: # Ignore related Entities
            continue
        label_offset = splitted[1].split(' ')
        label = label_offset[0]
        if label in labels_to_ignore: # Ignore labels 
            continue
        offset = label_offset[1:]
        span = splitted[2].strip('\n')
        if with_notes==False:
            ann_info.append([annotator, bunch, filename,mark, label,
                         offset[0], offset[-1], span.strip('\n')])
            continue
        
        if mark in mark2code.keys(): # Add Notes (code) information
            code = mark2code[mark]
        else:
            code = ''
        ann_info.append([annotator, bunch, filename,mark, label,
                     offset[0], offset[-1], span.strip('\n'), code])
            
    return ann_info, filenames

def parse_tsv(in_path):
    '''
    Get information from ann that was already stored in a TSV file.
    
    Parameters
    ----------
    in_path: string
        path to TSV file with 9 columns: ['annotator', 'bunch', 'filename', 
        'mark','label', 'offset1', 'offset2', 'span', 'code']
        Additionally, we can also have the path to a 3 column TSV: ['code', 'label', 'span']
    
    Returns
    -------
    df_annot: pandas DataFrame
        It has 4 columns: 'filename', 'label', 'code', 'span'.
    '''
    df_annot = pd.read_csv(in_path, sep='\t', header=None)
    if len(df_annot.columns) == 9:
        df_annot.columns=['annotator', 'bunch', 'filename', 'mark',
                      'label', 'offset1', 'offset2', 'span', 'code']
    elif len(df_annot.columns) == 8:
        df_annot.columns=['annotator', 'bunch', 'filename', 'mark',
              'label', 'offset1', 'offset2', 'span']
    else:
        df_annot.columns = ['code', 'span', 'label']
        df_annot['filename']  ='xx'
    return df_annot
