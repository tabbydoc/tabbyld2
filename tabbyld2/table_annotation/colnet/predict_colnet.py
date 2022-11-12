"""
Predict with ColNet
"""
import os
import sys
import argparse
import numpy as np
import tensorflow as tf
import tensorflow.compat.v1 as v1
from gensim.models import Word2Vec
from util_strings import Word2Wec_path
from util_t2d import read_t2d_cells
from util_cnn import ordered_cells2synthetic_columns
from util_cnn import sequence2matrix
from util_cnn import synthetic_columns2sequence
from util_cnn import random_cells2synthetic_columns
from util_cnn import permutation_cells2synthetic_columns

current_path = os.path.dirname(os.path.realpath(sys.argv[0]))
parser = argparse.ArgumentParser()

parser.add_argument(
    '--model_dir',
    type=str,
    default=Word2Wec_path,
    help='Directory of word2vec model')
parser.add_argument(
    '--synthetic_column_size',
    type=int,
    default=4,
    help='Size of synthetic column')
parser.add_argument(
    '--synthetic_column_type',
    type=int,
    default=1,
    # -1 def,
    help='synthetic column num to sample for each column; '
         '>=1: sample a number; 0: sliding window; -1: permutation combination and voting')
parser.add_argument(
    '--sequence_size',
    type=int,
    default=15,
    help='Length of word sequence of entity unit')
parser.add_argument(
    '--cnn_evaluate',
    type=str,
    default=os.path.join(current_path, 'in_out\\cnn\\cnn_1_2_1.00'),
    help='Directory of trained models')
parser.add_argument(
    '--io_dir',
    type=str,
    default=os.path.join(current_path, 'in_out'),
    help='Directory of input/output')

FLAGS, unparsed = parser.parse_known_args()
print(FLAGS)
print('load word2vec model ...')
w2v_model = Word2Vec.load(os.path.join(FLAGS.model_dir, 'word2vec_gensim'))


def predict(test_x, classifier_name):
    checkpoint_dir = os.path.join(FLAGS.cnn_evaluate, classifier_name, 'checkpoints')
    checkpoint_file = tf.train.latest_checkpoint(checkpoint_dir)

    graph = tf.Graph()
    with graph.as_default():
        session_conf = v1.ConfigProto(allow_soft_placement=False, log_device_placement=False)
        sess = v1.Session(config=session_conf)
        with sess.as_default():
            # Load the saved meta graph and restore variables
            saver = v1.train.import_meta_graph("{}.meta".format(checkpoint_file))
            saver.restore(sess, checkpoint_file)
            input_x = sess.graph.get_operation_by_name("input_x").outputs.pop()
            dropout_keep_prob = sess.graph.get_operation_by_name("dropout_keep_prob").outputs.pop()
            probabilities = sess.graph.get_operation_by_name("output/probabilities").outputs.pop()
            predictions = sess.graph.get_operation_by_name("output/predictions").outputs.pop()

            test_p = sess.run(probabilities, {input_x: test_x, dropout_keep_prob: 0.5})

    return test_p[:, 1]


def predict_colnet():
    print('Step #1: reading cnn classifiers')
    cnn_classifiers = set()
    for cls_name in os.listdir(FLAGS.cnn_evaluate):
        cnn_classifiers.add(cls_name)

    print('Step #2: reading col_cells and col_lookup_classes')
    col_cells = read_t2d_cells()
    col_lookup_classes = dict()
    with open(os.path.join(FLAGS.io_dir, 'lookup_col_classes.csv')) as f:
        for line in f.readlines():
            line_tmp = line.strip().split('","')
            if len(line_tmp) > 1:
                col = line_tmp[0][1:]
                line_tmp[-1] = line_tmp[-1][:-1]
                col_lookup_classes[col] = set(line_tmp[1:])
            else:
                col = line_tmp[0][1:-1]
                col_lookup_classes[col] = set()

    print('Step #3: predicting column by column')
    col_class_p = dict()
    for col_i, col in enumerate(col_cells.keys()):
        cells = col_cells[col]
        if FLAGS.synthetic_column_type >= 0:
            if FLAGS.synthetic_column_type > 0:
                units = random_cells2synthetic_columns(cells, FLAGS.synthetic_column_size, FLAGS.synthetic_column_type)
            else:
                units = ordered_cells2synthetic_columns(cells, FLAGS.synthetic_column_size)
        else:
            units = permutation_cells2synthetic_columns(cells)

        X = np.zeros((len(units), FLAGS.sequence_size, w2v_model.vector_size, 1))
        # X = np.random.sample((len(units), FLAGS.sequence_size, w2v_model.vector_size, 1))
        for i, unit in enumerate(units):
            seq = synthetic_columns2sequence(unit, FLAGS.sequence_size)
            X[i] = sequence2matrix(seq, FLAGS.sequence_size, w2v_model)

        if col in col_lookup_classes:
            for classifier in col_lookup_classes[col]:
                if classifier in cnn_classifiers:
                    col_class = '"%s","%s"' % (col, classifier)
                    p = predict(X, classifier)
                    score = np.mean(p)
                    # print(score)
                    col_class_p[col_class] = score
        else:
            print("No annotation in lookup_col_classes.csv for " + str(col))

        if col_i % 5 == 0:
            print('     column %d predicted' % col_i)

    print('Step #4: saving predictions')
    out_file_name = 'p_%s.csv' % os.path.basename(FLAGS.cnn_evaluate)
    full_path = os.path.join(FLAGS.io_dir, 'predictions')
    if not os.path.exists(full_path):
        os.makedirs(full_path)
    with open(os.path.join(full_path, out_file_name), 'w') as f:
        for col_class in col_class_p.keys():
            f.write('%s,"%.2f"\n' % (col_class, col_class_p[col_class]))


if __name__ == '__main__':
    predict_colnet()
