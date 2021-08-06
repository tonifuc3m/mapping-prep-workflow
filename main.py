#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jun 28 10:50:28 2021

@author: antonio
"""
# import pandas as pd
import argparse
import os
# import numpy as np
from parse_and_format_ann import brat_to_tsv
import add_codes_and_sug
import format_sug_and_remove_already_mapped
import unicodedata 
import string

def argparser():
    
    parser = argparse.ArgumentParser(description='process user given parameters')
    parser.add_argument("-d", "--datapath", required = True, dest = "datapath", 
                        help = "absolute path to brat files of one bunch")
    parser.add_argument("-a", "--mapped_tsv", required = True, dest = "mapped_tsv", 
                        help = "absolute path to TSV with ALREADY mapped annotations. It has 4 columns: _id_,label,span_norm,code")
    parser.add_argument("-l", "--labels_to_ignore", required = False, 
                        dest = "labels_to_ignore", nargs='+',
                        default = ['_SUG_SINTOMA', '_SUG_ENFERMEDAD', '_SUG_FARMACO',
                                   '_SUG_PROCEDIMIENTO'],
                        help = "Brat labels")
    parser.add_argument("-o", "--outpath", required = True, dest = "outpath", 
                        help = "absolute path to output directory")
    
    args = parser.parse_args()
    return args.datapath, args.mapped_tsv, args.labels_to_ignore, args.outpath

def remove_accents(data):
    return ''.join(x for x in unicodedata.normalize('NFKD', data) if x in string.printable)

def main(path, already_mapped_tsv_path, labels_to_ignore, outpath):
    ### 1. Parse and format annotations
    tsv = brat_to_tsv(path, labels_to_ignore = labels_to_ignore)
    
    ### 2. Add already mapped codes and suggestions
    tsv_with_sug = add_codes_and_sug.main(tsv, already_mapped_tsv_path, outpath)
    
    ### 3. Keep codes in Brat. Remove rows already mapped (with no code in 
    ### Brat). Merge both types of suggestions. Priority: 1) Linneaus, 2) translated
    tsv_with_sug_ok = format_sug_and_remove_already_mapped.main(tsv_with_sug, outpath)
    
    ### 4. Reorder columns
    tsv_with_sug_ok['span_norm_lower'] = tsv_with_sug_ok['span_norm'].apply(lambda x: remove_accents(x.lower()))
    tsv_final = tsv_with_sug_ok.sort_values(by=['span_norm_lower'])

    ### 5. Save this and send to annotator
    tsv_final.drop_duplicates(['label','span_norm'])[['_id_','label','span_norm','frequency','note_BRAT','code_already_mapped','code_sug','sug_description','FINAL_CODE']].\
        to_csv(os.path.join(outpath, 'this_bunch_no_mapping.tsv'), sep='\t', 
                    header=True, index=False)
    print(f'[OUTPUT] TSV with the entities of this bunch ready to be normalized here: {os.path.join(outpath, "this_bunch_no_mapping.tsv")}')
    
    
if __name__ == '__main__':
    
    path, already_mapped_tsv_path, labels_to_ignore, outpath = argparser()
    main(path, already_mapped_tsv_path, labels_to_ignore, outpath)
    print(f'[TODO] Concat {os.path.join(outpath, "this_bunch_already_mapped.tsv")} and {os.path.join(outpath, "this_bunch_no_mapping.tsv")}')
    print('[TODO] Upload TSV to Google Spreadsheet with proper format')

    

