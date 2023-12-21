import React, {useCallback, useEffect, useRef, useState} from 'react';
import PropTypes from 'prop-types';
import {TableVirtuoso} from 'react-virtuoso';

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
    className="w-full text-sm text-left text-gray-800 table-auto border-spacing-0"
    {...props}
    style={{borderCollapse: 'separate'}}
  />
);

const TableHead = React.forwardRef((props, ref) => (
  <thead className="text-gray-800 bg-gray-100 font-semibold w-full" {...props} ref={ref} />
));

TableHead.displayName = 'TableHead';

const TableRow = (props) => <tr className="bg-white border-b hover:bg-gray-50" {...props} />;

/**
 * Component for viewing tabular data.
 *
 * @return {*} The component
 */
export default function TableView({table}) {
  const [selected, _setSelected] = useState(null);
  const selectedRef = useRef(selected);

  const setSelected = useCallback((value) => {
    selectedRef.current = value;
    _setSelected(value);
  }, []);

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
    <TableVirtuoso
      data={table.data}
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
            <th key={column} className="px-4 py-2">
              {column}
            </th>
          ))}
        </tr>
      )}
      itemContent={(rowIndex, row) => (
        <>
          {row.map((value, columnIndex) => (
            <td
              key={columnIndex}
              className={`px-4 py-2 ${
                selected && rowIndex === selected[0] && columnIndex === selected[1] ? 'bg-gray-200' : ''
              }`}
              onClick={() => setSelected([rowIndex, columnIndex])}
            >
              {value}
            </td>
          ))}
        </>
      )}
    />
  );
}

TableView.propTypes = {
  table: PropTypes.shape({
    columns: PropTypes.arrayOf(PropTypes.string).isRequired,
    data: PropTypes.arrayOf(PropTypes.arrayOf(PropTypes.any)).isRequired,
  }).isRequired,
};
