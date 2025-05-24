# -*- coding: utf-8 -*-
# @Time : 2020/8/8 3:14
# @Author : Zhongyi Hua
# @FileName: query_species2000_colDB.py
# @Usage: 
# @Note:
# @E-mail: njbxhzy@hotmail.com
import argparse
from collections import defaultdict

import pandas as pd


class ColDBQuery:
    def __init__(self, db_path, query_path):
        self.tb_taxon = pd.read_table(db_path)
        self.querylst = ColDBQuery._read_(query_path)
        self.species_dict, self.reverse_dict = self.generate_dicts()

    @staticmethod
    def _read_(query_path):
        with open(query_path, encoding='utf-8') as f_in:
            contents = f_in.read().splitlines()
        return contents

    def generate_dicts(self):
        species_dict = defaultdict()

        for _item in self.tb_taxon.itertuples():
            if _item.rank in ('species', 'subspecies', 'variety'):
                species_dict.setdefault(_item.scientificName,
                                        {'ID': _item.ID, 'status': _item.status, 'parentID': _item.parentID, 'authorship': _item.authorship})
                """ # for subspecies
                _tmp_list = _item.scientificName.split()
                _tmp_name = _tmp_list[0] + ' ' + _tmp_list[1] + ' subsp. ' + _tmp_list[2] if len(_tmp_list) != 4 else ' '.join(_tmp_list)
                subspecies_dict.setdefault(_tmp_name,
                                           {'ID': _item.ID, 'status': _item.status, 'parentID': _item.parentID})
                """
        reverse_dict = {_item['ID']: _species for _species, _item in species_dict.items()}
        return species_dict, reverse_dict

    def query_one_species(self, query_name):
        """Query accepted name for one species in species2000 database.

        Args:
            query_name (str): _description_

        Returns:
            str: _description_
        """
        query_res = self.species_dict.get(query_name, 'Not in species2000')
        if query_res == 'Not in species2000':
            return 'Not in Species2000, most likely a spelling error.'
        else:
            if query_res.get('status') in ('provisionally accepted', 'accepted', 'ambiguous synonym'):
                return query_name
            # 'ambiguous synonym' just keep it
            elif query_res.get('status') == 'synonym':
                if accepted_name:= self.reverse_dict.get(query_res.get('parentID')):
                    return accepted_name
                else:
                    return 'There are homonymous species named by different authors.'
            else:
                return 'Please check manually'
    
    def query_authorship(self, query_name):
        """Query authorship for one species in species2000 database."""
        try:
            query_res = self.species_dict.get(query_name).get('authorship')
        except:
            query_res = "Please check manually"
        return query_res


    def query_all(self):
        """_summary_

        Returns:
            _type_: _description_
        """
        res_lst = []
        for _species in self.querylst:
            tmp_dct = {'raw': _species,
                       'curated': self.query_one_species(_species)}
            if tmp_dct.get('curated') not in ('Not in Species2000, most likely a spelling error.',
                                              'Please check manually',
                                              'There are homonymous species named by different authors.'):
                tmp_dct['authorship'] = self.query_authorship(tmp_dct.get('curated'))
            res_lst.append(tmp_dct)
        return pd.DataFrame(res_lst)


def main():
    
    parser = argparse.ArgumentParser(description="This is the script for fix scientific name based on species2000")
    parser.add_argument('-i', '--input', required=True,
                        help='<file_path> input NameUsage.tsv file path')
    parser.add_argument('-d', '--database', required=True,
                        help='<file_path> Species2000 taxa file')
    parser.add_argument('-o', '--output', required=True,
                        help='<file_path> result path') 

    args = parser.parse_args()
    queryIns = ColDBQuery(args.database, args.input)
    tb1 = queryIns.query_all()
    tb1.to_csv(args.output, sep='\t', index=False)


if __name__ == '__main__':
    main()
