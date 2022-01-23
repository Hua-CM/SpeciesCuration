# -*- coding: utf-8 -*-
# @Time : 2020/8/8 3:14
# @Author : Zhongyi Hua
# @FileName: query_species2000_colDB.py
# @Usage: 
# @Note:
# @E-mail: njbxhzy@hotmail.com

import pandas as pd
from collections import defaultdict


class ColDBQuery:
    def __init__(self, DB_path, query_path):
        self.tb_taxon = pd.read_table(DB_path)
        self.querylst = ColDBQuery._read_(query_path)
        self.species_dict, self.reverse_dict = self.generate_dicts()

    @staticmethod
    def _read_(query_path):
        with open(query_path) as f_in:
            a = f_in.read().splitlines()
        return a

    def generate_dicts(self):
        species_dict = defaultdict()

        for _item in self.tb_taxon.itertuples():
            if _item.rank in ('species', 'subspecies', 'variety'):
                species_dict.setdefault(_item.scientificName,
                                        {'ID': _item.ID, 'status': _item.status, 'parentID': _item.parentID})
                """ # for subspecies
                _tmp_list = _item.scientificName.split()
                _tmp_name = _tmp_list[0] + ' ' + _tmp_list[1] + ' subsp. ' + _tmp_list[2] if len(_tmp_list) != 4 else ' '.join(_tmp_list)
                subspecies_dict.setdefault(_tmp_name,
                                           {'ID': _item.ID, 'status': _item.status, 'parentID': _item.parentID})
                """
        reverse_dict = {_item['ID']: _species for _species, _item in species_dict.items()}
        return species_dict, reverse_dict

    def query_species(self, query_name):
        query_res = self.species_dict.get(query_name, 'Not in species2000')
        if query_res == 'Not in species2000':
            return query_res
        else:
            if query_res.get('status') in ('provisionally accepted', 'accepted', 'ambiguous synonym'):
                return query_name
            # 'ambiguous synonym' just keep it
            elif query_res.get('status') == 'synonym':
                return self.reverse_dict.get(query_res.get('parentID'))
            else:
                return "Please check manually"

    def query(self):
        res_lst = []
        for _species in self.querylst:
            res_lst.append({'raw': _species,
                            'curated': self.query_species(_species)})
        return pd.DataFrame(res_lst)


def main():
    import argparse
    parser = argparse.ArgumentParser(description="This is the script for fix scientific name based on species2000")
    parser.add_argument('-i', '--input', required=True,
                        help='<file_path> imput path')
    parser.add_argument('-d', '--database', required=True,
                        help='<file_path> Species2000 taxa file')
    parser.add_argument('-o', '--output', required=True,
                        help='<file_path> result path')
    args = parser.parse_args()
    queryIns = ColDBQuery(args.database, args.input)
    tb1 = queryIns.query()
    tb1.to_csv(args.output, sep='\t', index=False)


if __name__ == '__main__':
    main()
