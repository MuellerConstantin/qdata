import React from 'react';
import PropTypes from 'prop-types';
import {TableVirtuoso} from 'react-virtuoso';

const TableWrapper = React.forwardRef((props, ref) => (
  <div
    className={
      'relative h-full w-full overflow-auto scrollbar-thin scrollbar-thumb-gray-600 ' +
      'scrollbar-track-gray-200 border'
    }
    {...props}
    ref={ref}
  />
));

TableWrapper.displayName = 'TableWrapper';

const Table = (props) => (
  <table className="w-full text-sm text-left text-gray-800" {...props} style={{borderCollapse: 'separate'}} />
);

const TableHead = (props) => <thead className="text-gray-800 bg-gray-100 font-semibold w-full" {...props} />;

const TableRow = (props) => <tr className="bg-white border-b hover:bg-gray-50" {...props} />;

/**
 * Component for viewing tabular data.
 *
 * @return {*} The component
 */
export default function TableView({table}) {
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
      itemContent={(index, row) => (
        <>
          {row.map((cell, cellIndex) => (
            <td key={cellIndex} className="px-4 py-2">
              {cell}
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
