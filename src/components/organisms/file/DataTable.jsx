import React, {useCallback, useEffect, useRef, useState, useMemo} from 'react';
import PropTypes from 'prop-types';
import {TableVirtuoso} from 'react-virtuoso';
import {FontAwesomeIcon} from '@fortawesome/react-fontawesome';
import {faFilter, faTimes, faSort, faSortUp, faSortDown} from '@fortawesome/free-solid-svg-icons';

const TableWrapper = React.forwardRef((props, ref) => (
  <div
    className={
      'relative h-full w-full overflow-auto scrollbar-thin scrollbar-thumb-gray-600 ' +
      'scrollbar-track-gray-200 border select-none'
    }
    {...props}
    ref={ref}
  />
));

TableWrapper.displayName = 'TableWrapper';

const Table = (props) => (
  <table
    className="w-full text-sm text-left text-gray-800 table-auto border-spacing-0 border-collapse"
    {...props}
    style={{borderCollapse: 'separate'}}
  />
);

const TableHead = React.forwardRef((props, ref) => (
  <thead className="text-white bg-gray-600 font-semibold w-full" {...props} ref={ref} />
));

TableHead.displayName = 'TableHead';

const TableRow = (props) => <tr className="bg-white border-b hover:bg-gray-50" {...props} />;

/**
 * Component for viewing tabular data.
 *
 * @return {*} The component.
 */
export default function DataTable({table}) {
  const [filter, _setFilter] = useState([]);
  const [sort, _setSort] = useState({});
  const [selected, _setSelected] = useState(null);
  const selectedRef = useRef(selected);

  const setSelected = useCallback((value) => {
    selectedRef.current = value;
    _setSelected(value);
  }, []);

  const addFilter = useCallback(
    (value) => {
      _setFilter((prev) => [...prev, value]);
    },
    [filter],
  );

  const removeFilter = useCallback(
    (index) => {
      _setFilter((prev) => prev.filter((_, filterIndex) => filterIndex !== index));
    },
    [_setFilter],
  );

  const setSort = useCallback((column, type) => {
    if (!type) {
      _setSort((prev) => {
        const newSort = {...prev};
        delete newSort[column];
        return newSort;
      });
    } else {
      _setSort((prev) => ({...prev, [column]: type}));
    }
  }, []);

  const data = useMemo(() => {
    let preparedTable;

    if (filter.length === 0) {
      preparedTable = table.data.slice();
    } else {
      preparedTable = table.data.slice().filter((row) => {
        return filter.every(({column, value}) => {
          const columnIndex = table.columns.indexOf(column);
          return row[columnIndex] === value;
        });
      });
    }

    const sortColumns = Object.keys(sort);

    if (sortColumns.length > 0) {
      preparedTable.sort((a, b) => {
        for (const column of sortColumns) {
          const columnIndex = table.columns.indexOf(column);
          const aValue = a[columnIndex];
          const bValue = b[columnIndex];

          if (!isNaN(aValue) && !isNaN(bValue)) {
            const aNumber = Number(aValue);
            const bNumber = Number(bValue);

            if (aNumber < bNumber) {
              return sort[column] === 'asc' ? -1 : 1;
            } else if (aNumber > bNumber) {
              return sort[column] === 'asc' ? 1 : -1;
            }
          } else {
            if (aValue < bValue) {
              return sort[column] === 'asc' ? -1 : 1;
            } else if (aValue > bValue) {
              return sort[column] === 'asc' ? 1 : -1;
            }
          }
        }

        return 0;
      });
    }

    return preparedTable;
  }, [filter, sort, table]);

  useEffect(() => {
    const handleCtrlC = (event) => {
      if (event.ctrlKey && event.code === 'KeyC' && selectedRef.current) {
        const [row, column] = selectedRef.current;
        const value = table.data[row][column];
        navigator.clipboard.writeText(value);
      }
    };

    window.addEventListener('keydown', handleCtrlC);
    return () => window.removeEventListener('keydown', handleCtrlC);
  }, []);

  const TableScrollSeekPlaceholder = (props) => {
    return (
      <tr {...props}>
        {table.columns.map((column) => (
          <th key={column} className="px-4 py-2">
            <div className="h-4 w-full bg-gray-200 rounded animate-pulse" />
          </th>
        ))}
      </tr>
    );
  };

  return (
    <div className="h-full w-full flex flex-col space-y-2">
      {filter?.length > 0 && (
        <div
          className={
            'flex space-x-2 overflow-x-auto overflow-y-visible scrollbar-thin scrollbar-thumb-gray-600 ' +
            'scrollbar-track-gray-200 pb-2 select-none'
          }
        >
          {filter.map(({column, value}, index) => (
            <div
              key={index}
              className={
                'space-x-2 flex items-center justify-center text-gray-800 border ' + 'bg-gray-100 p-1 text-xs rounded'
              }
            >
              <FontAwesomeIcon icon={faFilter} className="h-3 w-3" />
              <span className="truncate">{column}</span>
              <button
                className="text-gray-800 hover:text-gray-600 focus:outline-none flex items-center justify-center"
                onClick={() => removeFilter(index)}
              >
                <FontAwesomeIcon icon={faTimes} className="w-4 h-4" />
              </button>
            </div>
          ))}
        </div>
      )}
      <TableVirtuoso
        data={data}
        scrollSeekConfiguration={{
          enter: (velocity) => Math.abs(velocity) > 50,
          exit: (velocity) => Math.abs(velocity) < 10,
        }}
        components={{
          Scroller: TableWrapper,
          Table: Table,
          TableHead: TableHead,
          TableRow: TableRow,
          ScrollSeekPlaceholder: TableScrollSeekPlaceholder,
        }}
        fixedHeaderContent={() => (
          <tr>
            {table.columns.map((column) => (
              <th key={column} className="px-4 py-2 border">
                <div className="flex items-center justify-center space-x-1">
                  <span>{column}</span>
                  <div
                    className="flex items-center cursor-pointer"
                    onClick={() => {
                      if (sort[column] === 'asc') {
                        setSort(column, 'desc');
                      } else if (sort[column] === 'desc') {
                        setSort(column, null);
                      } else {
                        setSort(column, 'asc');
                      }
                    }}
                  >
                    {sort[column] === 'asc' && <FontAwesomeIcon icon={faSortUp} className="w-3 h-3" />}
                    {sort[column] === 'desc' && <FontAwesomeIcon icon={faSortDown} className="w-3 h-3" />}
                    {sort[column] !== 'asc' && sort[column] !== 'desc' && (
                      <FontAwesomeIcon icon={faSort} className="w-3 h-3" />
                    )}
                  </div>
                </div>
              </th>
            ))}
          </tr>
        )}
        itemContent={(rowIndex, row) => (
          <>
            {row.map((value, columnIndex) => (
              <td
                key={columnIndex}
                className={`px-4 py-2 border ${
                  selected && rowIndex === selected[0] && columnIndex === selected[1] ? 'bg-gray-200' : ''
                }`}
                onClick={() => setSelected([rowIndex, columnIndex])}
                onDoubleClick={() => addFilter({column: table.columns[columnIndex], value})}
              >
                {value}
              </td>
            ))}
          </>
        )}
      />
    </div>
  );
}

DataTable.propTypes = {
  table: PropTypes.shape({
    columns: PropTypes.arrayOf(PropTypes.string).isRequired,
    data: PropTypes.arrayOf(PropTypes.arrayOf(PropTypes.any)).isRequired,
  }).isRequired,
};
