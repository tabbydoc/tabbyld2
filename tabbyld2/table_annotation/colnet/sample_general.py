"""
lookup general samples <class, entity> pairs from DBPedia
"""
# -*- coding: utf-8 -*-

import os
import sys
import argparse
from util_kb import query_general_entities

current_path = os.path.dirname(os.path.realpath(sys.argv[0]))
parser = argparse.ArgumentParser()
parser.add_argument(
    '--io_dir',
    type=str,
    default=os.path.join(current_path, 'in_out'),
    help='Directory of output')
FLAGS, unparsed = parser.parse_known_args()


def read_cls_ents():
    print('   Step #1: Read candidate classes and their special entities')
    cls_par_entities = dict()
    with open(os.path.join(FLAGS.io_dir, 'particular_pos_samples.csv'), 'r') as f:
        for line in f.readlines():
            line_tmp = line.strip().split('","')
            line_tmp[0] = line_tmp[0][1:]
            line_tmp[-1] = line_tmp[-1][:-1]
            cls_par_entities[line_tmp[0]] = line_tmp[1:]
    return cls_par_entities


def query_gen_ents(cls_par_entities):
    print('   Step #2: Query general entities')
    cls_gen_entities = query_general_entities(cls_par_entities)
    return cls_gen_entities


def write_gen_samples(cls_gen_entities):
    print('   Step #3: Output general samples')
    with open(os.path.join(FLAGS.io_dir, 'general_pos_samples.csv'), 'w', encoding="utf-8") as f:
        for cls in cls_gen_entities.keys():
            entities = cls_gen_entities[cls]
            ent_s = ''
            for ent in entities:
                ent_s += f'"{ent}",'
            if len(ent_s) > 0:
                f.write(f'"{cls}",{ent_s[:-1]}\n')
            else:
                f.write(f'"{cls}"\n')


if __name__ == '__main__':
    cls_ents = read_cls_ents()
    cls_gen_ents = query_gen_ents(cls_ents)
    write_gen_samples(cls_gen_ents)
