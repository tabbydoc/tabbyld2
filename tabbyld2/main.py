import os
import json
import tabbyld2.parser as pr
import tabbyld2.utility as utl
import tabbyld2.pipeline as pl
from datetime import datetime
from tabbyld2.config import ResultPath
from tabbyld2.tabular_data_model import TableModel


if __name__ == '__main__':
    start_full_time = datetime.now()
    # Save a set of source tables in the json format
    pr.save_json_dataset(ResultPath.CSV_FILE_PATH, ResultPath.JSON_FILE_PATH)
    # Cycle through table files
    for root, dirs, files in os.walk(ResultPath.JSON_FILE_PATH):
        for file in files:
            if utl.allowed_file(file, {"json"}):
                print("File '" + str(file) + "' processing started!")
                try:
                    with open(ResultPath.JSON_FILE_PATH + file, "r", encoding="utf-8") as fp:
                        # Deserialize a source table in the json format (create a table model)
                        table = TableModel.deserialize_source_table(utl.remove_suffix_in_filename(file), json.load(fp))
                except json.decoder.JSONDecodeError:
                    print("Error decoding json table file!")
                if table is not None:
                    # Preprocessing table
                    table = pl.pipeline_preprocessing(table, file)
                    # Solve CEA task
                    table = pl.pipeline_cell_entity_annotation(table, file)
                    # Solve CTA task
                    table = pl.pipeline_column_type_annotation(table, file)
    print("***************************************************")
    print("Full time: " + str(datetime.now() - start_full_time))
