from abc import ABC, abstractmethod
from enum import Enum
from operator import attrgetter
from typing import Any, Callable, Dict, Iterator, List, Optional, Tuple, Union, Iterable

from tabbyld2.datamodel.knowledge_graph_model import ClassModel, ClassRankingMethod, EntityModel, EntityRankingMethod
from tabbyld2.preprocessing.cleaner import fix_text, remove_garbage_characters, remove_multiple_spaces
from tabbyld2.preprocessing.labels import LiteralLabel, NamedEntityLabel


class AbstractColumnCellModel(ABC):
    __slots__ = ()

    @abstractmethod
    def annotate_cell(self) -> str:
        """
        Annotate table cell based on ranked candidate entities
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

    def set_cleared_value(self, cleared_value: Optional[str]):
        self._cleared_value = cleared_value

    def set_label(self, label: Union[LiteralLabel, NamedEntityLabel]):
        self._label = label

    def set_candidate_entities(self, candidate_entities: List[EntityModel]):
        self._candidate_entities = candidate_entities

    def annotate_cell(self):
        if self.candidate_entities is not None:
            self._annotation = max(self.candidate_entities, key=attrgetter("_final_score")).uri


class AbstractTableColumnModel(ABC):
    __slots__ = ()

    @abstractmethod
    def annotate_column(self) -> str:
        """
        Annotate table column based on ranked candidate classes
        """
        pass


class TableColumnModel(AbstractTableColumnModel):
    __slots__ = ("_header_name", "_cells", "_column_type", "_candidate_classes", "_annotation")

    def __init__(self, header_name: str = None, cells: Tuple[ColumnCellModel, ...] = None, column_type: str = None,
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

    def set_header_name(self, header_name: str):
        self._header_name = header_name

    def set_column_type(self, column_type: str):
        self._column_type = column_type

    def annotate_column(self):
        if self.candidate_classes is not None:
            self._annotation = max(self.candidate_classes, key=attrgetter("_final_score")).uri


class AbstractTableModel(ABC):
    __slots__ = ()

    @property
    @abstractmethod
    def columns_number(self) -> int:
        """
        Get number of columns
        """
        pass

    @property
    @abstractmethod
    def rows_number(self) -> int:
        """
        Get number of rows
        """
        pass

    @abstractmethod
    def column(self, column_index: int, *, include_header: bool = False) -> Tuple[Any, ...]:
        """
        Get column cells for specified index. This method could include or exclude header cells from result
        :param column_index: target cell column index in range [0; columns_number)
        :param include_header: flag to include or exclude header cells from result
        :return: table cells content ordered top-to-bottom
        """
        pass

    @abstractmethod
    def row(self, row_index: int) -> Tuple[Any, ...]:
        """
        Get row cells for specified row index
        :param row_index: target cell row index in range [0; rows_number)
        :return: table cells content ordered left-to-right
        """
        pass

    @abstractmethod
    def cell(self, row_index: int, column_index: int) -> Any:
        """
        Get cell content by row and column number
        :param row_index: target cell row index in range [0; rows_number)
        :param column_index: target cell column index in range [0; columns_number)
        :return: specified cell content (mention)
        """
        pass

    @abstractmethod
    def context(self, row_index: int, column_index: int, include_header: bool = False) -> Tuple[str, ...]:
        """
        Get cell local context by row and column
        :param row_index: target cell row index
        :param column_index: target cell column index
        :param include_header: flag to include or exclude header cells from result
        :return: specified cell local context
        """
        pass

    @abstractmethod
    def clean(self, include_header: bool = False) -> None:
        """
        Cleans table data
        :param include_header: flag to include or exclude header cells from result
        """
        pass

    @abstractmethod
    def serialize_cleared_table(self) -> List[dict]:
        """
        Serialize cleared tubular data in the form of dict
        :return: cleared table dict
        """
        pass

    @abstractmethod
    def serialize_recognized_named_entities(self) -> List[dict]:
        """
        Serialize recognized named entities for table cells in the form of dict
        :return: recognized named entities dict
        """
        pass

    @abstractmethod
    def serialize_classified_columns(self) -> Dict[str, str]:
        """
        Serialize classified table columns in the form of dict
        :return: classified columns dict
        """
        pass

    @abstractmethod
    def serialize_candidate_entities_for_cells(self) -> Dict[str, Dict[str, List[str]]]:
        """
        Serialize candidate entities for table cells in the form of dict
        :return: candidate entities dict
        """
        pass

    @abstractmethod
    def serialize_ranked_candidate_entities(self, method: str = None) -> Dict[str, Dict[str, Dict[str, float]]]:
        """
        Serialize ranked candidate entities in the form of dict
        :param method: flag to select ranking method
        :return: ranked candidate entities dict
        """
        pass

    @abstractmethod
    def serialize_annotated_cells(self) -> Dict[str, Dict[str, str]]:
        """
        Serialize annotated table cells in the form of dict
        :return: annotated cells dict
        """
        pass

    @abstractmethod
    def serialize_ranked_candidate_classes(self, method: str = None) -> Dict[str, Dict[str, float]]:
        """
        Serialize ranked candidate classes in the form of dict
        :param method: flag to select ranking method
        :return: ranked candidate classes dict
        """
        pass

    @abstractmethod
    def serialize_annotated_columns(self) -> Dict[str, str]:
        """
        Serialize annotated table columns in the form of dict
        :return: annotated columns dict
        """
        pass


class TableModel(AbstractTableModel):
    __slots__ = ("_table_name", "_columns", "_header_indexes", "_columns_number", "_rows_number")

    def __init__(self, table_name: str, columns: Tuple[TableColumnModel, ...], header_indexes: Optional[Iterable[int]] = None):
        self._table_name = table_name
        self._columns = columns
        self._header_indexes = tuple(header_indexes) if header_indexes is not None else ()
        self._columns_number = len(self.columns) if len(self.columns) != 0 else 0
        self._rows_number = len(self.columns[0].cells) if len(self.columns[0].cells) != 0 else 0

    @property
    def table_name(self):
        return self._table_name

    @property
    def columns(self):
        return self._columns

    @property
    def header_indexes(self):
        return self._header_indexes

    @property
    def columns_number(self):
        return self._columns_number

    @property
    def rows_number(self):
        return self._rows_number

    def set_header_indexes(self, rows: Iterable[int]):
        self._header_indexes = tuple(rows)

    def _validate_indices(self, column_index: Optional[int] = None, row_index: Optional[int] = None):
        """
        Validates the existence of column and row indices
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
        Cells on which cell_filter returns False are ignored
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

    def _column_iterator(self, column: int, *, include_header: bool = False, row_start: int = 0, row_end: Optional[int] = None,
                         cell_filter: Callable[[int, int], bool] = lambda row, column: True) -> Iterator[Any]:
        """
        Iterates table over specified column from row_start to row_end (defaults to table size).
        Cells on which cell_filter returns False are ignored
        :param column: column index
        :param include_header: flag to include or exclude header cells from result
        :param row_start: row start index
        :param row_end: row end index
        :param cell_filter: cell filter
        """
        if row_end is None:
            row_end = self.rows_number - 1
        step = 1 if row_start < row_end else -1
        for row in range(row_start, row_end + step, step):
            if cell_filter(row, column):
                if include_header:
                    yield self.cell(column, row)
                elif row not in self.header_indexes:
                    yield self.cell(column, row)

    def column(self, column_index: int, *, include_header: bool = False) -> Tuple[Any, ...]:
        return tuple(self._column_iterator(column_index, include_header=include_header))

    def row(self, row_index: int) -> Tuple[Any, ...]:
        return tuple(self._row_iterator(row_index))

    def cell(self, column_index: int, row_index: int) -> Any:
        self._validate_indices(column_index, row_index)
        cleared_value = self.columns[column_index].cells[row_index].cleared_value
        return cleared_value if cleared_value is not None else self.columns[column_index].cells[row_index].source_value

    def context(self, row_index: int, column_index: int, include_header: bool = False) -> Tuple[str, ...]:
        context = {*self.row(row_index), *self.column(column_index, include_header=include_header)}
        context.remove(self.cell(column_index, row_index))
        return tuple(context)

    def clean(self, include_header: bool = False) -> None:
        for column in self.columns:
            if include_header:
                column.set_header_name(remove_multiple_spaces(fix_text(column.header_name)))
            for cell in column.cells:
                if cell.source_value is not None:
                    cell.set_cleared_value(remove_multiple_spaces(remove_garbage_characters(fix_text(cell.source_value))))
                    if not cell.cleared_value:
                        cell.set_cleared_value(None)

    def serialize_cleared_table(self) -> List[dict]:
        return [{column.header_name: column.cells[i].cleared_value for column in self.columns} for i in range(self.rows_number)]

    def serialize_recognized_named_entities(self) -> List[dict]:
        return [{column.header_name: column.cells[i].label for column in self.columns} for i in range(self.rows_number)]

    def serialize_classified_columns(self) -> Dict[str, str]:
        return {column.header_name: column.column_type for column in self.columns}

    def serialize_candidate_entities_for_cells(self) -> Dict[str, Dict[str, List[str]]]:
        serialized_candidate_entities = {}
        for column in self.columns:
            cells = {}
            for cell in column.cells:
                if cell.cleared_value is not None and cell.candidate_entities is not None:
                    cells[cell.cleared_value] = [candidate_entity.uri for candidate_entity in cell.candidate_entities]
                else:
                    cells[cell.cleared_value] = None
            serialized_candidate_entities[column.header_name] = cells
        return serialized_candidate_entities

    def serialize_ranked_candidate_entities(self, method: str = None) -> Dict[str, Dict[str, Dict[str, float]]]:
        serialized_ranked_candidate_entities = {}
        for column in self.columns:
            cells = {}
            for cell in column.cells:
                candidate_entities = {}
                if cell.candidate_entities is not None:
                    for candidate_entity in cell.candidate_entities:
                        if method == EntityRankingMethod.STRING_SIMILARITY:
                            candidate_entities[candidate_entity.uri] = candidate_entity.string_similarity
                        if method == EntityRankingMethod.NER_BASED_SIMILARITY:
                            candidate_entities[candidate_entity.uri] = candidate_entity.ner_based_similarity
                        if method == EntityRankingMethod.HEADING_BASED_SIMILARITY:
                            candidate_entities[candidate_entity.uri] = candidate_entity.heading_based_similarity
                        if method == EntityRankingMethod.ENTITY_EMBEDDINGS_BASED_SIMILARITY:
                            candidate_entities[candidate_entity.uri] = candidate_entity.entity_embeddings_based_similarity
                        if method == EntityRankingMethod.CONTEXT_BASED_SIMILARITY:
                            candidate_entities[candidate_entity.uri] = candidate_entity.context_based_similarity
                        if method == EntityRankingMethod.SCORES_AGGREGATION:
                            candidate_entities[candidate_entity.uri] = candidate_entity.final_score
                cells[cell.cleared_value] = candidate_entities
            serialized_ranked_candidate_entities[column.header_name] = cells
        return serialized_ranked_candidate_entities

    def serialize_annotated_cells(self) -> Dict[str, Dict[str, str]]:
        return {column.header_name: {cell.cleared_value: cell.annotation for cell in column.cells} for column in self.columns}

    def serialize_ranked_candidate_classes(self, method: str = None) -> Dict[str, Dict[str, float]]:
        serialized_ranked_candidate_classes = {}
        for column in self.columns:
            if column.candidate_classes is not None:
                candidate_classes = {}
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

    def serialize_annotated_columns(self) -> Dict[str, str]:
        return {column.header_name: column.annotation for column in self.columns}
