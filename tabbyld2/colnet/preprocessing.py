import argparse
import os
import sys

from sample_general import read_cls_ents, query_gen_ents, write_gen_samples
from sample_particular import read_candidate_classes, read_ent_and_they_cls, generate_pos_sample, generate_neg_samples, \
    out_negative_samples
from sample_lookup import read_table_cells, read_exist_ent_cls, lookup_ent_cls, write_ents_cls
from util_kb import super_classes
from util_t2d import read_col_gt


current_path = os.path.dirname(os.path.realpath(sys.argv[0]))
parser = argparse.ArgumentParser()
parser.add_argument(
    '--io_dir',
    type=str,
    default=os.path.join(current_path, 'in_out'),
    help='Directory of input/output')
FLAGS, unparsed = parser.parse_known_args()


def extract_classes_columns():
    # Читаем намера таблиц и их супер классы из файла col_class_checked_fg
    col_classes = read_col_gt()
    # Дополняем этот словарь 'окей' классами из DBPedia
    col_classes = super_classes(col_classes)
    # Записываем в файл с строгим форматированием
    with open(os.path.join(FLAGS.io_dir, 'column_gt_extend_fg.csv'), 'w', encoding="utf-8") as f:
        for col in col_classes.keys():
            joined_str = '","'.join(col_classes[col])
            classes_str = f'"{joined_str}"'
            f.write(f'"{col}", "{classes_str}"\n')


if __name__ == '__main__':
    print('Stage #1: extract column ground truth classes of columns of tables(T2Dv2)')
    extract_classes_columns()

    print('Stage #2: generate samples for training')
    print('Lookup new Samples')
    col_cells = read_table_cells()
    cls_count, entities = read_exist_ent_cls()
    cls_count, ent_cls = lookup_ent_cls(col_cells, entities, cls_count)
    write_ents_cls(cls_count, ent_cls)

    print('Generate positive and negative samples')
    cand_classes = read_candidate_classes()
    ent_cls = read_ent_and_they_cls()
    pos_samples = generate_pos_sample(cand_classes, ent_cls)
    neg_samples = generate_neg_samples(pos_samples)
    out_negative_samples(pos_samples, neg_samples)

    print('Generate general samples')
    cls_ents = read_cls_ents()
    cls_gen_ents = query_gen_ents(cls_ents)
    write_gen_samples(cls_gen_ents)
