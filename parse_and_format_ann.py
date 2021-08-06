#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jun 28 10:54:31 2021

@author: antonio
"""
import re
from parse import parse_ann

isF = lambda x: 'f' in x.lower()
isN = lambda x: 'n' in x.lower()
isO = lambda x: 'o' in x.lower()
isR = lambda x: 'r' in x.lower()
isH = lambda x: 'h' in x.lower()

def _normalize_str(string, min_upper=5):
    '''
    Lowercase and remove whitespaces from given string
    '''
    # Lowercase
    string_lower = ' '.join(list(map(lambda x: x.lower() if len(x)>min_upper else x, string.split(' '))))
    # Remove whitespaces
    str_bs = re.sub('\s+', ' ', string_lower).strip()
    return str_bs


def brat_to_tsv(path, labels_to_ignore = ['ENFERMEDAD','ANTIINFECCIOSO','LAB-TEST',
                                          '_REJ_SPECIES', '_SUG_SPECIES']):
    '''
    Parse ANN. Add useful columns. Remove useless columns

    Parameters
    ----------
    path : str
        path to Brat directory.
    labels_to_ignore : list, optional
        DESCRIPTION. The default is ['ENFERMEDAD','ANTIINFECCIOSO','LAB-TEST',
                                       '_REJ_SPECIES', '_SUG_SPECIES'].

    Returns
    -------
    tsv : pandas DataFrame
        Dataframe with columns ['_id_', 'span_norm','code_BRAT', 'isN', 'isF', 
                                'isO', 'isR'].

    '''
    df = parse_ann(path, labels_to_ignore=labels_to_ignore,
                   with_notes=True)
    
    # if len(set(df.label.values)) > 1:
        # labels_to_ignore = labels_to_ignore + list(set(df.label.values) - set(['SPECIES']))
        # tsv = brat_to_tsv(path, labels_to_ignore)

    # Create unique identifier
    df['_id_'] = df[['filename','label','span','offset1', 'offset2']].agg('#'.join, axis=1)
    
    # Generate span_norm column
    span_norm = df['span'].apply(lambda x: _normalize_str(x))
    df = df.assign(span_norm=span_norm.values)
    
    # Drop useless columns
    tsv = df.drop(['annotator', 'bunch', 'filename', 'mark', 'offset1', 
                   'offset2','span'], axis=1)[['_id_','label', 'span_norm','code']]
    tsv.columns = ['_id_', 'label', 'span_norm','note_BRAT']
    
    return tsv
