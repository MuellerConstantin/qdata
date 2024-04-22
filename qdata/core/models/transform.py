"""
Contains the models related to data manipulation and display.
"""

from enum import Enum

class DataFrameFilterOperation(Enum):
    """
    Operations for filtering a DataFrame.
    """
    EQUAL = "eq"
    NOT_EQUAL = "ne"
    GREATER_THAN = "gt"
    GREATER_THAN_OR_EQUAL = "ge"
    LESS_THAN = "lt"
    LESS_THAN_OR_EQUAL = "le"
    BEGINS_WITH = "bw"
    ENDS_WITH = "ew"

class DataFrameFilter:
    """
    Filter for a DataFrame.
    """
    def __init__(self, column: str, operation: DataFrameFilterOperation, value: object):
        self._column = column
        self._operation = operation
        self._value = value

    @property
    def column(self) -> str:
        """
        Get the column to filter on.
        """
        return self._column

    @property
    def operation(self) -> DataFrameFilterOperation:
        """
        Get the operation to perform.
        """
        return self._operation

    @property
    def value(self) -> object:
        """
        Get the value to compare against.
        """
        return self._value
