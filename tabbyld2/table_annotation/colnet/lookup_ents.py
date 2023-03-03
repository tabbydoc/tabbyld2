import os.path
import sys

from sample_lookup import read_exist_ent_cls, lookup_ent_cls
from tabbyld2.config import ResultPath

source_tables_dir = ResultPath.CSV_FILE_PATH
if not os.path.exists(source_tables_dir):
    print(f'{source_tables_dir} does not exist')
    sys.exit(1)

current_path = os.path.dirname(os.path.realpath(sys.argv[0]))
ents_file = os.path.join(current_path, 'in_out', 'lookup_entities.csv')
cls_file = os.path.join(current_path, 'in_out', 'lookup_classes.csv')
control_file = os.path.join(current_path, 'in_out', 'column_gt_fg.csv')

if not os.path.exists(ents_file):
    print("lookup_entities.csv создан пустым")
    with open(ents_file, 'w') as f:
        pass

if not os.path.exists(cls_file):
    print("lookup_classes.csv создан пустым")
    with open(cls_file, 'w') as f:
        pass

if not os.path.exists(control_file):
    print("Нет контрольного файла! (column_gt_fg.csv)")
    sys.exit(0)


def read_csv_table():
    source_tables = os.listdir(ResultPath.CSV_FILE_PATH)
    col_cells = dict()
    with open(control_file, 'r') as f:
        table_data = f.readlines()
    for tab_num, table in enumerate(source_tables, 0):
        with open(os.path.join(ResultPath.CSV_FILE_PATH, table), 'r') as f:
            table_content = f.readlines()
            meta_data = table_data[tab_num].split(",")
            table_name, col_id = meta_data[0], meta_data[1]
            column_name = f"{table_name} {col_id}"
            # column_name = table_content[0].split(",")[int(col_id)].strip()
            column_content = []
            for i in range(1, len(table_content)):
                row_content = table_content[i].split(",")
                column_content.append(row_content[int(col_id)].strip())
        col_cells[column_name] = column_content
    return col_cells


def new_lookup():
    col_cells = read_csv_table()
    cls_count, entities = read_exist_ent_cls()
    cls_count, ent_cls = lookup_ent_cls(col_cells, entities, cls_count)

    with open(ents_file, 'w', encoding="utf-8") as out_f:
        for ent in ent_cls.keys():
            str_cls = ''
            for c in ent_cls[ent]:
                str_cls += ('"%s",' % c)
            if len(str_cls) > 0:
                out_f.write('"%s",%s\n' % (ent, str_cls[:-1]))
            else:
                out_f.write('"%s"\n' % ent)

    with open(cls_file, 'a', encoding="utf-8") as out_f:
        for cls in cls_count.keys():
            out_f.write('"%s","%d"\n' % (cls, cls_count[cls]))
