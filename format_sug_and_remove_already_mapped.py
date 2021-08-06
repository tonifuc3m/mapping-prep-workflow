#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jun 28 10:59:22 2021

@author: antonio
"""
import os
import numpy as np
import pandas as pd
import re 

end_parenth = re.compile("\((.+)\)$")
def get_meaningful_description(x, pattern=end_parenth):
    real_description = x
    for item in x.split(', '):
        if pattern.search(item)!=None:
            real_description = item
            break
    return real_description


def main(tsv_with_sug, outpath, snomed_path='./data/SpanishSnomed.tsv'):
    '''
    
    Parameters
    ---------
    tsv_with_sug: pandas DataFrame
        columns: ['_id_','label', 'span_norm', 'code_BRAT', 'isN', 'isF', 'isO','isR','isH',
       'code_already_mapped', 'code_sug', 'span_norm_en', 'code_sug_from_en',
       'code_sug_link', 'code_sug_from_en_link', 'code_sug_scientific_name',
       'code_sug_common_name', 'code_sug_from_en_scientific_name',
       'code_sug_from_en_common_name', 'FINAL_CODE']
    '''
    
    ## 4.1 Merge three types of suggestions
    ## Priority: 1) NER (code_ner), 2) PharmaCoNER (code_pharmaconer), 
    ## 3) BARR (code_barr), 4) TEMUnormalizer (code_TEMU)
    # 4.1.1 If there is NER suggestion, put other suggestion to np.nan()
    idx_with_NER_suggestions = tsv_with_sug.loc[tsv_with_sug['code_ner'].isna()==False,:].index
    tsv_with_sug.loc[idx_with_NER_suggestions, \
                       ['code_pharmaconer','code_barr', 'code_TEMU']] = np.nan
    
    # 4.1.2 If there is PharmaCoNER suggestion, put other suggestion to np.nan()
    idx_with_phner_suggestions = tsv_with_sug.loc[tsv_with_sug['code_pharmaconer'].isna()==False,:].index
    tsv_with_sug.loc[idx_with_phner_suggestions,['code_barr', 'code_TEMU']] = np.nan
    
    # 4.1.3 If there is BARR suggestions, put TEMUnormalizer suggestion to np.nan()
    idx_with_phner_suggestions = tsv_with_sug.loc[tsv_with_sug['code_barr'].isna()==False,:].index
    tsv_with_sug.loc[idx_with_phner_suggestions,['code_TEMU']] = np.nan

    
    # 4.1.3 Merge suggestions
    tsv_with_sug['code_sug'] = tsv_with_sug[['code_pharmaconer', 'code_ner', 'code_barr', 'code_TEMU']].\
        apply(lambda x: ','.join(x.dropna().astype(str)), axis=1)
        
        
    # 4.1.4 Add suggestion description
    snomed = pd.read_csv(snomed_path, sep='\t', header=None, names=['sug_description', 'code_sug'])
    aux = pd.merge(tsv_with_sug, snomed, how='left', on=['code_sug'])
    id_description = aux[['_id_', 'sug_description']].groupby(['_id_'])['sug_description'].apply(lambda x: get_meaningful_description(', '.join(x)) if(np.all(pd.notnull(x))) else x.values[0])
    tsv_with_sug_descrip = tsv_with_sug.merge(id_description, on=['_id_']).copy()
    
    # 4.2 Remove useless columns
    tsv_with_sug_ok = tsv_with_sug_descrip[['_id_', 'label', 'span_norm', 'frequency',
                                    'note_BRAT', 'code_already_mapped','code_sug', 'sug_description']].copy()
        
    ## 4.3 Remove rows with code_already_mapped
    idx_already_mapped = tsv_with_sug_ok.loc[tsv_with_sug_ok['code_already_mapped'].isna()==False,:].index
    tsv_already_mapped = tsv_with_sug_ok.loc[idx_already_mapped, :].copy()
    tsv_already_mapped['FINAL_CODE'] = tsv_already_mapped['code_already_mapped']
    tsv_already_mapped.sort_values(by=['span_norm']).drop_duplicates(['label','span_norm']).\
        to_csv(os.path.join(outpath, 'this_bunch_already_mapped.tsv'),
               sep='\t', header=True, index=False)
    print(f'[OUTPUT] TSV with the entities of this bunch that were already normalized here: {os.path.join(outpath, "this_bunch_already_mapped.tsv")}. These entities need to be validated')

    
    tsv_not_mapped = tsv_with_sug_ok.drop(idx_already_mapped).copy()
    tsv_not_mapped['FINAL_CODE'] = ''
    
    return tsv_not_mapped