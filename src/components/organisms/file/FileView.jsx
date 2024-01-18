import React, {useState, useEffect, useCallback} from 'react';
import PropTypes from 'prop-types';
import {FontAwesomeIcon} from '@fortawesome/react-fontawesome';
import {faExclamationTriangle} from '@fortawesome/free-solid-svg-icons';
import useStatus from '../../../hooks/useStatus';
import Button from '../../atoms/Button';
import DataTable from '../../molecules/file/DataTable';

/**
 * Renders an error message.
 *
 * @param {string} err The error.
 * @param {string} path The path of the file.
 * @return {*} The component.
 */
function renderError(err, path) {
  switch (err) {
    case 'error:parsingFileFailed': {
      return (
        <>
          <FontAwesomeIcon icon={faExclamationTriangle} className="w-12 h-12 text-amber-500" />
          <div className="text-center">
            The file is not displayed in the explorer because it is either corrupted or uses an unsupported QVD
            encoding.
          </div>
          <Button className="!px-8" onClick={() => window.electron.ipc.send('file:close', path)}>
            Close File
          </Button>
        </>
      );
    }
    case 'error:fileNotFound': {
      return (
        <>
          <FontAwesomeIcon icon={faExclamationTriangle} className="w-12 h-12 text-amber-500" />
          <div className="text-center">
            The path to the file does not exist anymore. The file might have been moved or deleted.
          </div>
          <Button className="!px-8" onClick={() => window.electron.ipc.send('file:close', path)}>
            Close File
          </Button>
        </>
      );
    }
    default: {
      return (
        <>
          <FontAwesomeIcon icon={faExclamationTriangle} className="w-12 h-12 text-amber-500" />
          <div className="text-center">An unknown error occurred while opening the file. Please try again.</div>
          <Button className="!px-8" onClick={() => window.electron.ipc.send('file:close', path)}>
            Close File
          </Button>
        </>
      );
    }
  }
}

/**
 * Component for viewing the contents of QVD files.
 *
 * @return {*} The component.
 */
export default function FileView({loading, error, table, filePath, active}) {
  const {setLoading, setTotalRows, setTotalColumns, setFiltered} = useStatus();

  const [selectedValue, setSelectedValue] = useState(null);
  const [tableFiltered, setTableFiltered] = useState(null);
  const [tableShape, setTableShape] = useState(null);

  const handleCtrlC = useCallback(
    (event) => {
      if (event.ctrlKey && event.code === 'KeyC') {
        if (active && selectedValue) {
          navigator.clipboard.writeText(selectedValue);
        }
      }
    },
    [selectedValue, active],
  );

  useEffect(() => {
    window.addEventListener('keydown', handleCtrlC);
    return () => window.removeEventListener('keydown', handleCtrlC);
  }, [handleCtrlC]);

  useEffect(() => {
    if (active) {
      setLoading(loading);
    }
  }, [active, loading]);

  useEffect(() => {
    if (active) {
      setTotalRows(tableShape?.[0]);
      setTotalColumns(tableShape?.[1]);
    }
  }, [active, tableShape]);

  useEffect(() => {
    if (active) {
      setFiltered(tableFiltered);
    }
  }, [active, tableFiltered]);

  useEffect(() => {
    return () => {
      setLoading(null);
      setTotalRows(null);
      setTotalColumns(null);
      setFiltered(null);
    };
  }, []);

  return (
    <div
      className={
        'flex flex-col grow h-0 overflow-y-auto scrollbar-thin scrollbar-thumb-gray-600 ' +
        'scrollbar-track-gray-200 px-2 py-4'
      }
    >
      {loading ? (
        <div className="flex justify-center">
          <div role="status">
            <svg
              aria-hidden="true"
              className="w-8 h-8 text-gray-200 animate-spin fill-green-600"
              viewBox="0 0 100 101"
              fill="none"
              xmlns="http://www.w3.org/2000/svg"
            >
              <path
                /* eslint-disable-next-line max-len */
                d="M100 50.5908C100 78.2051 77.6142 100.591 50 100.591C22.3858 100.591 0 78.2051 0 50.5908C0 22.9766 22.3858 0.59082 50 0.59082C77.6142 0.59082 100 22.9766 100 50.5908ZM9.08144 50.5908C9.08144 73.1895 27.4013 91.5094 50 91.5094C72.5987 91.5094 90.9186 73.1895 90.9186 50.5908C90.9186 27.9921 72.5987 9.67226 50 9.67226C27.4013 9.67226 9.08144 27.9921 9.08144 50.5908Z"
                fill="currentColor"
              />
              <path
                /* eslint-disable-next-line max-len */
                d="M93.9676 39.0409C96.393 38.4038 97.8624 35.9116 97.0079 33.5539C95.2932 28.8227 92.871 24.3692 89.8167 20.348C85.8452 15.1192 80.8826 10.7238 75.2124 7.41289C69.5422 4.10194 63.2754 1.94025 56.7698 1.05124C51.7666 0.367541 46.6976 0.446843 41.7345 1.27873C39.2613 1.69328 37.813 4.19778 38.4501 6.62326C39.0873 9.04874 41.5694 10.4717 44.0505 10.1071C47.8511 9.54855 51.7191 9.52689 55.5402 10.0491C60.8642 10.7766 65.9928 12.5457 70.6331 15.2552C75.2735 17.9648 79.3347 21.5619 82.5849 25.841C84.9175 28.9121 86.7997 32.2913 88.1811 35.8758C89.083 38.2158 91.5421 39.6781 93.9676 39.0409Z"
                fill="currentFill"
              />
            </svg>
            <span className="sr-only">Loading...</span>
          </div>
        </div>
      ) : error ? (
        <div className="flex justify-center items-center h-full w-full space-x-2 p-4">
          <div className="flex flex-col items-center max-w-[500px] space-y-4">{renderError(error, filePath)}</div>
        </div>
      ) : (
        <DataTable
          table={table}
          onSelect={(value) => setSelectedValue(value)}
          onFilter={(filter) => setTableFiltered(!!filter)}
          onShape={(shape) => setTableShape(shape)}
        />
      )}
    </div>
  );
}

FileView.propTypes = {
  active: PropTypes.bool,
  loading: PropTypes.bool,
  error: PropTypes.any,
  table: PropTypes.object,
  fileName: PropTypes.string,
  filePath: PropTypes.string,
};
