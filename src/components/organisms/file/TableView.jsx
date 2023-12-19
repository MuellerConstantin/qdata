import React from 'react';
import PropTypes from 'prop-types';

/**
 * Component for viewing tabular data.
 *
 * @return {*} The component
 */
export default function TableView({table}) {
  return (
    <div className="relative overflow-auto scrollbar-thin scrollbar-thumb-gray-600 scrollbar-track-gray-200">
      <table className="w-full text-sm text-left text-gray-800 border">
        <thead className="text-gray-800 bg-gray-100 font-semibold w-full">
          <tr>
            {table.columns.map((column) => (
              <th key={column} className="px-4 py-2">
                {column}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {table.data.map((row, rowIndex) => (
            <tr key={rowIndex} className="bg-white border-b hover:bg-gray-50">
              {row.map((cell, cellIndex) => (
                <td key={cellIndex} className="px-4 py-2 max-w-[200px]">
                  {cell}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

TableView.propTypes = {
  table: PropTypes.shape({
    columns: PropTypes.arrayOf(PropTypes.string).isRequired,
    data: PropTypes.arrayOf(PropTypes.arrayOf(PropTypes.any)).isRequired,
  }).isRequired,
};
