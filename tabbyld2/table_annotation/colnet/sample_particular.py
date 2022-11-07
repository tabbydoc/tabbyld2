"""
generate samples (entities) for each class
"""
import os
import sys
import argparse

current_path = os.path.dirname(os.path.realpath(sys.argv[0]))
parser = argparse.ArgumentParser()
parser.add_argument(
    '--io_dir',
    type=str,
    default=os.path.join(current_path, 'in_out'),
    help='Directory of input/output')
parser.add_argument(
    '--class_count_threshold',
    type=int,
    default=5,
    help='entity threshold for candidate classes')
FLAGS, unparsed = parser.parse_known_args()


def read_candidate_classes():
    print('   Step #1: Read candidate classes')
    candidate_classes = set()
    with open(os.path.join(FLAGS.io_dir, 'lookup_classes.csv'), 'r') as f:
        for line in f.readlines():
            line_tmp = line.strip().split('","')
            cls_name = line_tmp[0][1:]
            candidate_classes.add(cls_name)
    return candidate_classes


def read_ent_and_they_cls():
    print('   Step #2: Read entities and their classes')
    ent_cls = dict()
    with open(os.path.join(FLAGS.io_dir, 'lookup_entities.csv')) as f:
        for line in f.readlines():
            line_tmp = line.strip().split('","')
            line_tmp[0] = line_tmp[0][1:]
            line_tmp[-1] = line_tmp[-1][:-1]
            ent = line_tmp[0]
            ent_cls[ent] = line_tmp[1:]
    return ent_cls


def generate_pos_sample(candidate_classes, ent_cls):
    print('''   Step #3: build class-entities dictionary and output (Positive Samples)''')
    candidate_classes2 = set()
    with open(os.path.join(FLAGS.io_dir, 'particular_pos_samples.csv'), 'w') as f:
        for cls in candidate_classes:
            ent_str = ''
            ent_num = 0
            for ent in ent_cls.keys():
                if cls in ent_cls.get(ent):
                    ent_str += ('"%s",' % ent)
                    ent_num += 1
            if ent_num >= FLAGS.class_count_threshold:
                candidate_classes2.add(cls)
                f.write('"%s",%s\n' % (cls, ent_str[:-1]))
    return candidate_classes2


def generate_neg_samples(candidate_classes2):
    print('''   Step #4: get negative samples''')
    with open(os.path.join(FLAGS.io_dir, 'lookup_col_classes.csv'), 'r') as f:
        col_cls_lines = f.readlines()
    cls_neg_entities = dict()
    for cls1 in candidate_classes2:
        joint_classes = set()
        for cls2 in candidate_classes2:
            if not cls2 == cls1:
                for line in col_cls_lines:
                    if ('"%s"' % cls1) in line and ('"%s"' % cls2) in line:
                        joint_classes.add(cls2)
                        break
        with open(os.path.join(FLAGS.io_dir, 'lookup_entities.csv'), 'r', encoding="utf-8") as f:
            lines = f.readlines()
            for line in lines:
                line_tmp = line.strip().split('","')
                line_tmp[0] = line_tmp[0][1:]
                line_tmp[-1] = line_tmp[-1][:-1]
                classes = set(line_tmp[1:])
                ent = line_tmp[0]
                if cls1 not in classes and len(classes.intersection(joint_classes)) > 0:
                    if cls1 in cls_neg_entities:
                        cls_neg_entities[cls1].add(ent)
                    else:
                        cls_neg_entities[cls1] = {ent}
    return cls_neg_entities


def out_negative_samples(candidate_classes2, cls_neg_entities):
    print('''   Step #5: output negative samples''')
    with open(os.path.join(FLAGS.io_dir, 'particular_neg_samples.csv'), 'w', encoding="utf-8") as f:
        for cls in candidate_classes2:
            neg_entities = cls_neg_entities[cls]
            ent_str = ''
            for ent in neg_entities:
                ent_str += ('"%s",' % ent)
            f.write('"%s",%s\n' % (cls, ent_str))


if __name__ == '__main__':
    cand_classes = read_candidate_classes()
    ent_cls = read_ent_and_they_cls()
    pos_samples = generate_pos_sample(cand_classes, ent_cls)
    neg_samples = generate_neg_samples(pos_samples)
    out_negative_samples(pos_samples, neg_samples)
