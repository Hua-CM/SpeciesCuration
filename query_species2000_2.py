# -*- coding: utf-8 -*-
# @Time : 2020/8/8 11:17
# @Author : Zhongyi Hua
# @FileName: query_species2000_2.py
# @Usage: 
# @Note: Recommend RAM larger than 16G to use this script
# @E-mail: njbxhzy@hotmail.com

import pandas as pd


def query_species(query_name):

    def get_sci(_dict, _idx):
        if _dict['taxonRank'][_idx] == 'species':
            _sci_name = ' '.join([
                query_dict['genus'][_idx],
                query_dict['specificEpithet'][_idx],
            ])
            return _sci_name
        elif _dict['taxonRank'][_idx] == 'infraspecies':
            _sci_name = ' '.join([
                query_dict['genus'][_idx],
                query_dict['specificEpithet'][_idx],
                query_dict['verbatimTaxonRank'][_idx],
                query_dict['infraspecificEpithet'][_idx]
            ])
            return _sci_name

    name_list = query_name.split(' ')
    try:
        if len(name_list) == 2:
            query_result = species2019[species2019['scientificName'].str.match(query_name)]
            query_dict = query_result[query_result['verbatimTaxonRank'].isna()].to_dict('list')
            if query_result.empty:
                return 'Not in species2000'
            elif 'accepted name' in query_dict['taxonomicStatus']:
                tmp_idx = query_dict['taxonomicStatus'].index('accepted name')
                sci_name = get_sci(query_dict, tmp_idx)
                return sci_name
            else:
                query_dict = species2019[species2019['taxonID'] == query_dict['acceptedNameUsageID'][0]].to_dict('list')
                sci_name = get_sci(query_dict, 0)
                return sci_name
        elif len(name_list) == 4:
            query_result = species2019[species2019['scientificName'].str.match(' '.join(name_list[0:2]))]
            query_dict = query_result[query_result['infraspecificEpithet'] == name_list[3]].to_dict('list')
            if query_result.empty:
                return 'Not in species2000'
            elif 'accepted name' in query_dict['taxonomicStatus']:
                tmp_idx = query_dict['taxonomicStatus'].index('accepted name')
                sci_name = get_sci(query_dict, tmp_idx)
                return sci_name
            else:
                query_dict = species2019[species2019['taxonID'] == query_dict['acceptedNameUsageID'][0]].to_dict('list')
                sci_name = get_sci(query_dict, 0)
                return sci_name
        else:
            return 'Check name'
    except:
        return 'Check name'


def query_main(input_path, output_path):
    tb1 = pd.read_table(input_path, names=['raw_name'])
    tb1['fix_name'] = tb1['raw_name'].apply(query_species)
    tb1.to_csv(output_path, sep='\t', index=False)


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description="This is the script for fix scientific name based on species2000")
    parser.add_argument('-i', '--input', required=True,
                        help='<file_path> imput path')
    parser.add_argument('-d', '--database', required=True,
                        help='<file_path> Species2000 taxa file')
    parser.add_argument('-o', '--output', required=True,
                        help='<file_path> result path')
    args = parser.parse_args()
    species2019 = pd.read_table(args.database)
    query_main(args.input, args.output)
