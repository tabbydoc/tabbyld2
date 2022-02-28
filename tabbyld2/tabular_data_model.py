from enum import Enum
from abc import ABC, abstractmethod
from typing import Any, Callable, Iterator, Optional, Tuple
import tabbyld2.cleaner as cln
from tabbyld2.knowledge_graph_model import EntityModel, EntityRankingMethod, ClassModel, ClassRankingMethod


class ContextDirection(Enum):
    left = 0
    right = 1
    top = 2
    bottom = 3


class AbstractColumnCellModel(ABC):
    __slots__ = ()

    @abstractmethod
    def annotate_cell(self) -> str:
        """
        Annotate table cell based on ranked candidate entities.
        """
        pass


class ColumnCellModel(AbstractColumnCellModel):
    __slots__ = ("_source_value", "_cleared_value", "_label", "_candidate_entities", "_annotation")

    def __init__(self, source_value: Any = None, cleared_value: str = None, label: str = None,
                 candidate_entities: Tuple[EntityModel, ...] = None, annotation: str = None):
        self._source_value = source_value
        self._cleared_value = cleared_value
        self._label = label
        self._candidate_entities = candidate_entities
        self._annotation = annotation

    @property
    def source_value(self):
        return self._source_value

    @property
    def cleared_value(self):
        return self._cleared_value

    @property
    def label(self):
        return self._label

    @property
    def candidate_entities(self):
        return self._candidate_entities

    @property
    def annotation(self):
        return self._annotation

    def annotate_cell(self):
        if self.candidate_entities is not None:
            max_score = 0
            for candidate_entity in self.candidate_entities:
                if candidate_entity.final_score > max_score:
                    max_score = candidate_entity.final_score
                    self._annotation = candidate_entity.uri


class AbstractTableColumnModel(ABC):
    __slots__ = ()

    @abstractmethod
    def annotate_column(self) -> str:
        """
        Annotate table column based on ranked candidate classes.
        """
        pass


class TableColumnModel(AbstractTableColumnModel):
    __slots__ = ("_header_name", "_cells", "_column_type", "_candidate_classes", "_annotation")

    def __init__(self, header_name: Any = None, cells: Tuple[ColumnCellModel, ...] = None, column_type: str = None,
                 candidate_classes: Tuple[ClassModel, ...] = None, annotation: str = None):
        self._header_name = header_name
        self._cells = cells
        self._column_type = column_type
        self._candidate_classes = candidate_classes
        self._annotation = annotation

    @property
    def header_name(self):
        return self._header_name

    @property
    def cells(self):
        return self._cells

    @property
    def column_type(self):
        return self._column_type

    @property
    def candidate_classes(self):
        return self._candidate_classes

    @property
    def annotation(self):
        return self._annotation

    def annotate_column(self):
        if self.candidate_classes is not None:
            max_score = 0
            for candidate_class in self.candidate_classes:
                if candidate_class.final_score > max_score:
                    max_score = candidate_class.final_score
                    self._annotation = candidate_class.uri


class AbstractTableModel(ABC):
    __slots__ = ()

    @property
    @abstractmethod
    def columns_number(self) -> int:
        """
        Get number of columns.
        """
        pass

    @property
    @abstractmethod
    def rows_number(self) -> int:
        """
        Get number of rows.
        """
        pass

    @abstractmethod
    def column(self, column_index: int, *, include_header: bool = False) -> Tuple[Any, ...]:
        """
        Get column cells for specified index. This method could include or exclude header cells from result.
        :param column_index: target cell column index in range [0; columns_number)
        :param include_header: flag to include or exclude header cells from result
        :return: table cells content ordered top-to-bottom
        """
        pass

    @abstractmethod
    def row(self, row_index: int) -> Tuple[Any, ...]:
        """
        Get row cells for specified row index.
        :param row_index: target cell row index in range [0; rows_number)
        :return: table cells content ordered left-to-right
        """
        pass

    @abstractmethod
    def cell(self, row_index: int, column_index: int) -> Any:
        """
        Get cell content by row and column number.
        :param row_index: target cell row index in range [0; rows_number)
        :param column_index: target cell column index in range [0; columns_number)
        :return: specified cell content (mention)
        """
        pass

    @abstractmethod
    def context(self, row_index: int, column_index: int, direction: ContextDirection) -> Tuple[Any, ...]:
        """
        Get cell local context in specified direction.
        Result cells are ordered by distance from No header cells are included in result.
        :param row_index: target cell row index
        :param column_index: target cell column index
        :param direction: desired context direction
        :return: specified cell local context
        """
        pass


class TableModel(AbstractTableModel):
    __slots__ = ("_table_name", "_columns", "_columns_number", "_rows_number")

    def __init__(self, table_name: Any = None, columns: Tuple[TableColumnModel, ...] = None):
        self._table_name = table_name
        self._columns = columns
        self._columns_number = len(self.columns) if len(self.columns) != 0 else 0
        self._rows_number = len(self.columns[0].cells) if len(self.columns[0].cells) != 0 else 0

    @property
    def table_name(self):
        return self._table_name

    @property
    def columns(self):
        return self._columns

    @property
    def columns_number(self):
        return self._columns_number

    @property
    def rows_number(self):
        return self._rows_number

    def _validate_indices(self, column_index: Optional[int] = None, row_index: Optional[int] = None):
        """
        Validates the existence of column and row indices.
        :param column_index: column index
        :param row_index: row index
        """
        if column_index is not None and (column_index < 0 or column_index >= self.columns_number):
            raise ValueError(f"Column index should be in range [0, {self.columns_number})!")
        if row_index is not None and (row_index < 0 or row_index >= self.rows_number):
            raise ValueError(f"Row index should be in range [0, {self.rows_number})!")

    def _row_iterator(self, row: int, *, column_start: int = 0, column_end: Optional[int] = None,
                      cell_filter: Callable[[int, int], bool] = lambda row, column: True) -> Iterator[Any]:
        """
        Iterates table over specified row from column_start to column_end (defaults to table size).
        Cells on which cell_filter returns False are ignored.
        :param row: row index
        :param column_start: column start index
        :param column_end: column end index
        :param cell_filter: cell filter
        """
        if column_end is None:
            column_end = self.columns_number - 1
        step = 1 if column_start < column_end else -1
        for column in range(column_start, column_end + step, step):
            if cell_filter(row, column):
                yield self.cell(column, row)

    def _column_iterator(self, column: int, *, row_start: int = 0, row_end: Optional[int] = None,
                         cell_filter: Callable[[int, int], bool] = lambda row, column: True) -> Iterator[Any]:
        """
        Iterates table over specified column from row_start to row_end (defaults to table size).
        Cells on which cell_filter returns False are ignored.
        :param column: column index
        :param row_start: row start index
        :param row_end: row end index
        :param cell_filter: cell filter
        """
        if row_end is None:
            row_end = self.rows_number - 1
        step = 1 if row_start < row_end else -1
        for row in range(row_start, row_end + step, step):
            if cell_filter(row, column):
                yield self.cell(column, row)

    def column(self, column_index: int, *, include_header: bool = False) -> Tuple[Any, ...]:
        return tuple(self._column_iterator(column_index))

    def row(self, row_index: int) -> Tuple[Any, ...]:
        return tuple(self._row_iterator(row_index))

    def cell(self, column_index: int, row_index: int) -> Any:
        self._validate_indices(column_index, row_index)

        return self.columns[column_index].cells[row_index].cleared_value if \
            self.columns[column_index].cells[row_index].cleared_value is not None else \
            self.columns[column_index].cells[row_index].source_value

    def context(self, row_index: int, column_index: int, direction: ContextDirection) -> Tuple[Any, ...]:
        pass

    def clean(self, include_header: bool = False):
        """
        Cleans table data.
        :param include_header: flag to include or exclude header cells from result
        """
        for column in self.columns:
            if include_header:
                fixed_header_name = cln.fix_text(column.header_name)
                column._header_name = cln.remove_multiple_spaces(fixed_header_name)
            for cell in column.cells:
                if cell.source_value is not None:
                    fixed_value = cln.fix_text(cell.source_value)
                    cleared_value = cln.remove_garbage_characters(fixed_value)
                    cell._cleared_value = cln.remove_multiple_spaces(cleared_value)
                    if not cell.cleared_value:
                        cell._cleared_value = None

    def serialize_cleared_table(self):
        """
        Serialize cleared tubular data in the form of dict
        :return: cleared table dict
        """
        serialized_cleared_table = list()
        for i in range(self.rows_number):
            item = dict()
            for column in self.columns:
                item[column.header_name] = column.cells[i].cleared_value
            serialized_cleared_table.append(item)

        return serialized_cleared_table

    def serialize_recognized_named_entities(self):
        """
        Serialize recognized named entities for table cells in the form of dict
        :return: recognized named entities dict
        """
        serialized_recognized_named_entities = list()
        for i in range(self.rows_number):
            item = dict()
            for column in self.columns:
                item[column.header_name] = column.cells[i].label
            serialized_recognized_named_entities.append(item)

        return serialized_recognized_named_entities

    def serialize_classified_columns(self):
        """
        Serialize classified table columns in the form of dict
        :return: classified columns dict
        """
        serialized_classified_columns = dict()
        for column in self.columns:
            serialized_classified_columns[column.header_name] = column.column_type

        return serialized_classified_columns

    def serialize_candidate_entities_for_cells(self):
        """
        Serialize candidate entities for table cells in the form of dict
        :return: candidate entities dict
        """
        serialized_candidate_entities = dict()
        for column in self.columns:
            cells = dict()
            for cell in column.cells:
                candidate_entities = list()
                if cell.cleared_value is not None:
                    if cell.candidate_entities is not None:
                        for candidate_entity in cell.candidate_entities:
                            candidate_entities.append(candidate_entity.uri)
                        cells[cell.cleared_value] = candidate_entities
                    else:
                        cells[cell.cleared_value] = None
            serialized_candidate_entities[column.header_name] = cells

        return serialized_candidate_entities

    def serialize_ranked_candidate_entities(self, method: str = None):
        """
        Serialize ranked candidate entities in the form of dict
        :param method: flag to select ranking method
        :return: ranked candidate entities dict
        """
        serialized_ranked_candidate_entities = dict()
        for column in self.columns:
            cells = dict()
            for cell in column.cells:
                candidate_entities = dict()
                if cell.candidate_entities is not None:
                    for candidate_entity in cell.candidate_entities:
                        if method == EntityRankingMethod.STRING_SIMILARITY:
                            candidate_entities[candidate_entity.uri] = candidate_entity.string_similarity
                        if method == EntityRankingMethod.NER_BASED_SIMILARITY:
                            candidate_entities[candidate_entity.uri] = candidate_entity.ner_based_similarity
                        if method == EntityRankingMethod.HEADING_BASED_SIMILARITY:
                            candidate_entities[candidate_entity.uri] = candidate_entity.heading_based_similarity
                        if method == EntityRankingMethod.ENTITY_EMBEDDINGS_BASED_SIMILARITY:
                            candidate_entities[candidate_entity.uri] = candidate_entity.\
                                entity_embeddings_based_similarity
                        if method == EntityRankingMethod.CONTEXT_BASED_SIMILARITY:
                            candidate_entities[candidate_entity.uri] = candidate_entity.context_based_similarity
                        if method == EntityRankingMethod.SCORES_AGGREGATION:
                            candidate_entities[candidate_entity.uri] = candidate_entity.final_score
                cells[cell.cleared_value] = candidate_entities
            serialized_ranked_candidate_entities[column.header_name] = cells

        return serialized_ranked_candidate_entities

    def serialize_annotated_cells(self):
        """
        Serialize annotated table cells in the form of dict
        :return: annotated cells dict
        """
        serialized_annotated_cells = dict()
        for column in self.columns:
            cells = dict()
            for cell in column.cells:
                cells[cell.cleared_value] = cell.annotation
            serialized_annotated_cells[column.header_name] = cells

        return serialized_annotated_cells

    def serialize_ranked_candidate_classes(self, method: str = None):
        """
        Serialize ranked candidate classes in the form of dict
        :param method: flag to select ranking method
        :return: ranked candidate classes dict
        """
        serialized_ranked_candidate_classes = dict()
        for column in self.columns:
            if column.candidate_classes is not None:
                candidate_classes = dict()
                for candidate_class in column.candidate_classes:
                    if method == ClassRankingMethod.MAJORITY_VOTING:
                        candidate_classes[candidate_class.uri] = candidate_class.majority_voting_score
                    if method == ClassRankingMethod.HEADING_SIMILARITY:
                        candidate_classes[candidate_class.uri] = candidate_class.heading_similarity
                    if method == ClassRankingMethod.COLUMN_TYPE_PREDICTION:
                        candidate_classes[candidate_class.uri] = candidate_class.column_type_prediction_score
                    if method == ClassRankingMethod.SCORES_AGGREGATION:
                        candidate_classes[candidate_class.uri] = candidate_class.final_score
                serialized_ranked_candidate_classes[column.header_name] = candidate_classes
            else:
                serialized_ranked_candidate_classes[column.header_name] = None

        return serialized_ranked_candidate_classes

    def serialize_annotated_columns(self):
        """
        Serialize annotated table columns in the form of dict
        :return: annotated columns dict
        """
        serialized_annotated_columns = dict()
        for column in self.columns:
            serialized_annotated_columns[column.header_name] = column.annotation

        return serialized_annotated_columns

    @staticmethod
    def deserialize_source_table(file_name: str = None, source_json_data: dict = None):
        """
        Deserialize a source table in the json format and create table model object.
        :return: TableModel object
        """
        columns = tuple()
        dicts = {k: [d[k] for d in source_json_data] for k in source_json_data[0]}
        for key, items in dicts.items():
            cells = tuple()
            for item in items:
                cells += (ColumnCellModel(item),)
            columns += (TableColumnModel(key, cells),)
        return TableModel(file_name, columns)
