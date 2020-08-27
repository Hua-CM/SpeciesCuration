# -*- coding: utf-8 -*-
# @Time : 2020/8/10 1:22
# @Author : Zhongyi Hua
# @FileName: api_sp2000_CN.py
# @Usage:
# @Note:
# @E-mail: njbxhzy@hotmail.com

import requests
import pandas as pd
import json


def query_name(latin_name, user_key):
    print(latin_name)
    raw_result = json.loads(
        requests.get(
            f'http://www.sp2000.org.cn/api/v2/getSpeciesByScientificName?apiKey={user_key}&scientificName={latin_name}'
                    ).text
    )
    if raw_result['data']['species'] is None:
        return {'raw_name': latin_name,
                'sci_name': 'Not in species 2000'}
    elif len(raw_result['data']['species']) == 1:
        sci_name = raw_result['data']['species'][0]['accepted_name_info']['scientificName']
        if not latin_name == sci_name:
            # name_code = raw_result['data']['species'][0]['name_code']
            formal_result = json.loads(
               requests.get(
                   f'http://www.sp2000.org.cn/api/v2/getSpeciesByScientificName?apiKey={user_key}&scientificName={sci_name}'
               ).text
             )
            species_info = formal_result['data']['species'][0]['accepted_name_info']
        else:
            species_info = raw_result['data']['species'][0]['accepted_name_info']
        return {'raw_name': latin_name,
                'sci_name': sci_name,
                'phylum': species_info['taxonTree']['phylum'],
                'family':  species_info['taxonTree']['family'],
                'genus': species_info['taxonTree']['genus'],
                'synonym': ';'.join([_['synonym'] for _ in species_info['Synonyms']] if species_info.get('Synonyms') else ''),
                'org_name_c':  species_info['chineseName']
                }
    else:
        sci_dict = {_['scientific_name']: idx for idx, _ in enumerate(raw_result['data']['species'])}
        if sci_dict.get(latin_name):
            species_info = raw_result['data']['species'][sci_dict.get(latin_name)]['accepted_name_info']
            return {'raw_name': latin_name,
                    'sci_name': species_info['scientificName'],
                    'phylum': species_info['taxonTree']['phylum'],
                    'family':  species_info['taxonTree']['family'],
                    'genus': species_info['taxonTree']['genus'],
                    'synonym': ';'.join([_['synonym'] for _ in species_info['Synonyms']] if species_info.get('Synonyms') else ''),
                    'org_name_c':  species_info['chineseName']
                    }
        else:
            return {'raw_name': latin_name,
                    'sci_name': 'check manually'}


def query_batch(name_list, user_key):
    result_list = []
    for name in name_list:
        result_list.append(query_name(name, user_key))
    return pd.DataFrame(result_list)


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description="This is the script for querying accepted  name from species2000 china"
                                                 "using API")
    parser.add_argument('-i', '--input', required=True,
                        help='<file_path> input path. One species name per line')
    parser.add_argument('-o', '--output', required=True,
                        help='<file_path> output path')
    parser.add_argument('-k', '--key', required=True,
                        help='<char> user key for API service')
    args = parser.parse_args()
    with open(args.input) as f:
        query_list = f.read().strip().split('\n')
        query_result = query_batch(query_list, args.key)
        query_result.to_csv(args.output, sep='\t', index=False)
