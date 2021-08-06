#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jun 28 10:57:52 2021

@author: antonio
"""
import pandas as pd
import numpy as np
import os
#from googletrans import Translator
import pickle
#from mstranslator import Translator
from TEMUNormalizer import TEMUnormalizer

def save_obj(directory, obj, name):
    '''Helper function using pickle to save and load objects'''
    with open(directory + name + '.pkl', 'wb+') as f:
        pickle.dump(obj, f, pickle.HIGHEST_PROTOCOL)

def load_obj(directory, name):
    '''Helper function using pickle to save and load objects'''
    with open(directory + name + ".pkl", "rb") as f:
        return pickle.load(f)
    

def add_code_old_tsv(df, already_mapped_tsv_path, code_label='code_already_mapped'):
    
    # Get current column names
    current_cols = list(df.columns)

    # Load big TSV with codes
    already_mapped = pd.read_csv(already_mapped_tsv_path, sep='\t', header=0)
    already_mapped = already_mapped.drop(['_id_'], axis=1).\
        drop_duplicates(['label','span_norm'])
    already_mapped['code'] = already_mapped['code'].fillna('').astype(str)

    # Merge
    df = df.merge(already_mapped, how='left', 
                    on=['label','span_norm']).copy()
    current_cols.append(code_label)
    df.columns = current_cols
    
    return df
   


def main(tsv, already_mapped_tsv_path, outpath):
    
    ## 2.1 Add already mapped codes
    tsv_with_old_codes = add_code_old_tsv(tsv, already_mapped_tsv_path)
    
    ## 2.3 Add PharmacoNER suggestions
    pharmaconer = pd.read_csv('./data/pharmaconer.tsv',
                              sep='\t', header=None, names=['span_norm', 'code_pharmaconer'], dtype=str)
    tsv_with_old_codes = pd.merge(tsv_with_old_codes, pharmaconer, how='left', on=['span_norm']).copy()
    
    ## 2.4 Add NER suggestions
    ner = pd.read_csv('./data/NER.tsv',
                      sep='\t', header=None, names=['span_norm', 'code_ner'], dtype=str)
    tsv_with_old_codes = pd.merge(tsv_with_old_codes, ner, how='left', on=['span_norm']).copy()
    
    ## 2.5 Add BARR suggestions
    barr = pd.read_csv('./data/BARR.tsv',
                      sep='\t', header=None, names=['span_norm', 'code_barr'], dtype=str)
    tsv_with_old_codes = pd.merge(tsv_with_old_codes, barr, how='left', on=['span_norm']).copy()
    
    ## 2.6 Add TEMUNormalizer suggestions
    reference_dict = TEMUnormalizer.loadDict('./data/SpanishSnomed.tsv')
    termdic = {k:'' for k in tsv_with_old_codes.span_norm.values}
    termdic = TEMUnormalizer.directMatch(termdic,reference_dict)
    termdic = TEMUnormalizer.fuzzyMatch(termdic,reference_dict,93)
    termdic_clean = {k:v[0][0][0] if v!='' else '' for (k,v) in termdic.items()}
    temun = tsv_with_old_codes['span_norm'].map(termdic_clean)
    tsv_with_old_codes = tsv_with_old_codes.assign(code_TEMU=temun.values)
    
    ## 2.6 Frecuencia aparición span_norm
    span_norm_count = tsv_with_old_codes.groupby(['span_norm'])['span_norm'].count()
    span_norm_count.name = 'frequency'
    tsv_with_old_codes = pd.merge(tsv_with_old_codes, span_norm_count, how='left', on=['span_norm']).copy()    
    
    ## Order alphabetically and to_csv
    tsv_with_old_codes.sort_values(by=['span_norm']).\
        to_csv(os.path.join(outpath, 'all_before_mapping.tsv'), sep='\t', header=True, index=False)
    print(f"[OUTPUT] DO NOT USE THIS. THIS IS ONLY FOR REFERENCE: TSV with all the entities of the bunch here: {os.path.join(outpath, 'all_before_mapping.tsv')}")
   
    return tsv_with_old_codes