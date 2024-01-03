import React from 'react';
import {FontAwesomeIcon} from '@fortawesome/react-fontawesome';
import {faTable} from '@fortawesome/free-solid-svg-icons';
import useStatus from '../../../hooks/useStatus';

/**
 * The default window status bar. Contains status information and controls.
 *
 * @return {*} The component.
 */
export default function StatusBar() {
  const {loading, totalRows, totalColumns, filtered} = useStatus();

  return (
    <div className="bg-gray-100 text-gray-800 w-full h-8 flex border-t px-2 items-center text-sm space-x-4">
      <div className="flex-grow">{loading ? 'Loading...' : 'Ready'}</div>
      {totalRows && totalColumns && (
        <div className="flex space-x-2 items-center">
          {filtered ? <div>Filtered</div> : <div>Full</div>}
          <FontAwesomeIcon icon={faTable} className="h-4 w-4" />
          <div className="flex-grow-0">
            {totalColumns}x{totalRows}
          </div>
        </div>
      )}
    </div>
  );
}
