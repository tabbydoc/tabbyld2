import os
import json
import tabbyld2.parser as pr
import tabbyld2.utility as utl
import tabbyld2.cleaner as cln
import tabbyld2.annotator as ant
import tabbyld2.column_classifier as cc
import tabbyld2.candidate_generation as cg


# Path for source tables in CSV format
CSV_FILE_PATH = str(utl.get_project_root()) + "/source_tables/"
# Path to save source tables in the form json files
JSON_FILE_PATH = str(utl.get_project_root()) + "/results/json/"
# Path to save processing results and their provenance in the form json files
PROVENANCE_PATH = str(utl.get_project_root()) + "/results/provenance/"

# Paths of result provenance
CLEARED_DATA_PATH = "/cleared_data/"
RECOGNIZED_DATA_PATH = "/recognized_data/"
CLASSIFIED_DATA_PATH = "/classified_data/"

CANDIDATE_ENTITIES_PATH = "/candidate_entities/"
CANDIDATE_CLASSES_PATH = "/candidate_classes/"
CANDIDATE_PROPERTIES_PATH = "/candidate_properties/"

RANKED_CANDIDATE_ENTITIES = "/ranked_candidate_entities/"
RANKED_CANDIDATE_ENTITIES_BY_SS = "/ranked_candidate_entities_by_ss/"
RANKED_CANDIDATE_ENTITIES_BY_NS = "/ranked_candidate_entities_by_ns/"
RANKED_CANDIDATE_ENTITIES_BY_HS = "/ranked_candidate_entities_by_hs/"
RANKED_CANDIDATE_ENTITIES_BY_ESS = "/ranked_candidate_entities_by_ess/"
RANKED_CANDIDATE_ENTITIES_BY_CS = "/ranked_candidate_entities_by_cs/"

RANKED_CANDIDATE_CLASSES_BY_MV = "/ranked_candidate_classes_by_mv/"
RANKED_CANDIDATE_CLASSES_BY_HS = "/ranked_candidate_classes_by_hs/"
RANKED_CANDIDATE_CLASSES_BY_CN = "/ranked_candidate_classes_by_cn/"

ANNOTATED_CELL_DATA_PATH = "/annotated_cell_data/"
ANNOTATED_COLUMN_DATA_PATH = "/annotated_column_data/"
ANNOTATED_PROPERTY_DATA_PATH = "/annotated_property_data/"

if __name__ == '__main__':
    # Saving a set of source tables in the json format
    pr.save_json_dataset(CSV_FILE_PATH, JSON_FILE_PATH)

    for root, dirs, files in os.walk(JSON_FILE_PATH):
        for file in files:
            if utl.allowed_file(file, {"json"}):
                # Data cleaning
                cleared_data = cln.clean(JSON_FILE_PATH + file)
                if cleared_data:
                    # Forming path to file
                    path = PROVENANCE_PATH + utl.remove_suffix_in_filename(file) + CLEARED_DATA_PATH
                    # Checking the existence of path to save data cleaning results
                    utl.check_directory(path)
                    # Writing json file with cleared tabular data
                    with open(path + file, "w") as outfile:
                        json.dump(cleared_data, outfile, indent=4)

                # Recognition of named entities in source table (dict)
                recognized_data = cc.recognize_named_entities(cleared_data)
                if recognized_data:
                    # Forming path to file
                    path = PROVENANCE_PATH + utl.remove_suffix_in_filename(file) + RECOGNIZED_DATA_PATH
                    # Checking the existence of path to save named entity recognition results
                    utl.check_directory(path)
                    # Writing json file with named entity recognition results
                    with open(path + file, "w") as outfile:
                        json.dump(recognized_data, outfile, indent=4)

                # Classification of columns in source table (dict) based on recognized named entities
                classified_data = cc.classify_recognized_named_entities(recognized_data)
                classified_data = cc.classify_columns(classified_data)
                # Identifying a subject column among categorical columns
                classified_data = cc.define_subject_column(cleared_data, classified_data)
                if classified_data:
                    # Forming path to file
                    path = PROVENANCE_PATH + utl.remove_suffix_in_filename(file) + CLASSIFIED_DATA_PATH
                    # Checking the existence of path to save column classification results
                    utl.check_directory(path)
                    # Writing json file with named column classification results
                    with open(path + file, "w") as outfile:
                        json.dump(classified_data, outfile, indent=4)

                print("*********************************************************")

                # Finding candidate entities for all cells of categorical columns including a subject column
                candidate_entity_data = cg.get_candidate_entities_for_table(cleared_data, classified_data)
                if candidate_entity_data:
                    # Forming path to file
                    path = PROVENANCE_PATH + utl.remove_suffix_in_filename(file) + CANDIDATE_ENTITIES_PATH
                    # Checking the existence of path to save candidate entity lookup results
                    utl.check_directory(path)
                    # Writing json file with candidate entity lookup results
                    with open(path + file, "w") as outfile:
                        json.dump(candidate_entity_data, outfile, indent=4)

                print("*********************************************************")

                # Ranking candidate entities by string similarity and
                # writing json file with candidate entity ranking results
                ranked_candidate_entities_by_ss = ant.ranking_candidate_entities_by_ss(candidate_entity_data)
                if ranked_candidate_entities_by_ss:
                    path = PROVENANCE_PATH + utl.remove_suffix_in_filename(file) + RANKED_CANDIDATE_ENTITIES_BY_SS
                    utl.check_directory(path)
                    with open(path + file, "w") as outfile:
                        json.dump(ranked_candidate_entities_by_ss, outfile, indent=4)

                # Ranking candidate entities by NER based similarity and
                # writing json file with candidate entity ranking results
                ranked_candidate_entities_by_ns = ant.ranking_candidate_entities_by_ns(candidate_entity_data,
                                                                                       recognized_data)
                if ranked_candidate_entities_by_ns:
                    path = PROVENANCE_PATH + utl.remove_suffix_in_filename(file) + RANKED_CANDIDATE_ENTITIES_BY_NS
                    utl.check_directory(path)
                    with open(path + file, "w") as outfile:
                        json.dump(ranked_candidate_entities_by_ns, outfile, indent=4)

                # Ranking candidate entities by heading based similarity and
                # writing json file with candidate entity ranking results
                ranked_candidate_entities_by_hs = ant.ranking_candidate_entities_by_hs(candidate_entity_data)
                if ranked_candidate_entities_by_hs:
                    path = PROVENANCE_PATH + utl.remove_suffix_in_filename(file) + RANKED_CANDIDATE_ENTITIES_BY_HS
                    utl.check_directory(path)
                    with open(path + file, "w") as outfile:
                        json.dump(ranked_candidate_entities_by_hs, outfile, indent=4)

                # Ranking candidate entities by entity embeddings based semantic similarity and
                # writing json file with candidate entity ranking results
                ranked_candidate_entities_by_ess = ant.ranking_candidate_entities_by_ess(candidate_entity_data)
                if ranked_candidate_entities_by_ess:
                    path = PROVENANCE_PATH + utl.remove_suffix_in_filename(file) + RANKED_CANDIDATE_ENTITIES_BY_ESS
                    utl.check_directory(path)
                    with open(path + file, "w") as outfile:
                        json.dump(ranked_candidate_entities_by_ess, outfile, indent=4)

                # Ranking candidate entities by context based similarity and
                # writing json file with candidate entity ranking results
                ranked_candidate_entities_by_cs = ant.ranking_candidate_entities_by_cs(candidate_entity_data)
                if ranked_candidate_entities_by_cs:
                    path = PROVENANCE_PATH + utl.remove_suffix_in_filename(file) + RANKED_CANDIDATE_ENTITIES_BY_CS
                    utl.check_directory(path)
                    with open(path + file, "w") as outfile:
                        json.dump(ranked_candidate_entities_by_cs, outfile, indent=4)

                # Aggregating scores (ranks) for cell values (mentions) obtained based on five heuristics
                final_ranked_candidate_entities = ant.aggregate_ranked_candidate_entities(
                    ranked_candidate_entities_by_ss, ranked_candidate_entities_by_ns, ranked_candidate_entities_by_hs,
                    ranked_candidate_entities_by_ess, ranked_candidate_entities_by_cs)
                if final_ranked_candidate_entities:
                    # Forming path to file
                    path = PROVENANCE_PATH + utl.remove_suffix_in_filename(file) + RANKED_CANDIDATE_ENTITIES
                    # Checking the existence of path to save results of aggregated scores for candidate entities
                    utl.check_directory(path)
                    # Writing json file with finally ranking results for candidate entities
                    with open(path + file, "w") as outfile:
                        json.dump(final_ranked_candidate_entities, outfile, indent=4)

                # Annotating cell values (mentions) based on ranked list of candidate entities
                annotated_cell_data = ant.annotate_cells(final_ranked_candidate_entities)
                if annotated_cell_data:
                    print("Cells for '" + file + "' are annotated.")
                    # Forming path to file
                    path = PROVENANCE_PATH + utl.remove_suffix_in_filename(file) + ANNOTATED_CELL_DATA_PATH
                    # Checking the existence of path to save results of annotating cell values
                    utl.check_directory(path)
                    # Writing json file with results of annotating cell values
                    with open(path + file, "w") as outfile:
                        json.dump(annotated_cell_data, outfile, indent=4)

                print("*********************************************************")

                # Ranking candidate classes for categorical columns by majority voting method
                ranked_classes_by_mv = ant.ranking_candidate_classes_by_mv(annotated_cell_data, classified_data)
                if ranked_classes_by_mv:
                    # Forming path to file
                    path = PROVENANCE_PATH + utl.remove_suffix_in_filename(file) + RANKED_CANDIDATE_CLASSES_BY_MV
                    # Checking for existence of path to save class ranking results
                    utl.check_directory(path)
                    # Writing json file with class ranking results
                    with open(path + file, "w") as outfile:
                        json.dump(ranked_classes_by_mv, outfile, indent=4)
