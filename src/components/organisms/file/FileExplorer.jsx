import React, {useEffect, useState} from 'react';
import {FontAwesomeIcon} from '@fortawesome/react-fontawesome';
import {faTimes, faExclamationTriangle} from '@fortawesome/free-solid-svg-icons';
import Button from '../../atoms/Button';
import TableView from './TableView';

import Watermark from '../../../assets/images/watermark.svg';

/**
 * Component for viewing the contents of QVD files.
 *
 * @return {*} The component
 */
export default function FileExplorer() {
  const [fileName, setFileName] = useState(null);
  const [table, setTable] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    window.electron.ipc.on('openingFile', ({name}) => {
      setLoading(true);
      setError(null);
      setFileName(name);
    });

    window.electron.ipc.on('openingFileFailed', ({error}) => {
      setLoading(false);
      setError(error);
    });

    window.electron.ipc.on('openedFile', ({table}) => {
      setLoading(false);
      setTable(table);
    });

    window.electron.ipc.on('closedFile', () => {
      setLoading(false);
      setFileName(null);
      setError(null);
      setTable(null);
    });
  }, []);

  return (
    <div className="bg-white text-gray-800 w-full h-full flex flex-col">
      {fileName && (
        <>
          <div className="bg-gray-100 px-2 pt-2 border-t border-b h-12">
            <div
              className={
                'bg-white flex items-center justify-between w-fit h-10 max-w-[250px] min-w-[100px] ' +
                'px-2 space-x-6 border-t-2 border-t-green-600 border-t border-l border-r select-none'
              }
            >
              <span className="truncate text-sm">{fileName}</span>
              <button
                className="text-gray-800 hover:text-gray-600 focus:outline-none flex items-center justify-center"
                onClick={() => window.electron.ipc.send('closeFile')}
              >
                <FontAwesomeIcon icon={faTimes} className="w-4 h-4" />
              </button>
            </div>
          </div>
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
                <div className="flex flex-col items-center max-w-[500px] space-y-4">
                  <FontAwesomeIcon icon={faExclamationTriangle} className="w-12 h-12 text-amber-500" />
                  <div className="text-center">
                    The file is not displayed in the explorer because it is either corrupted or uses an unsupported QVD
                    encoding.
                  </div>
                  <Button className="!px-8" onClick={() => window.electron.ipc.send('closeFile')}>
                    Close File
                  </Button>
                </div>
              </div>
            ) : (
              <TableView table={table} />
            )}
          </div>
        </>
      )}
      {!fileName && (
        <div className="flex justify-center items-center h-full w-full space-x-2 select-none p-4">
          <div className="flex flex-col items-center max-w-[500px] space-y-4">
            <img src={Watermark} alt="Logo" className="w-auto h-64 drag-none object-contain" />
            <table className="border-separate border-spacing-y-2">
              <tbody>
                <tr>
                  <td className="text-right pr-2">Open Window</td>
                  <td className="text-left pl-2 flex items-center space-x-1 text-xs">
                    <div className="bg-gray-100 py-0.5 px-2 rounded border shadow">Ctrl</div>
                    <div>+</div>
                    <div className="bg-gray-100 py-0.5 px-2 rounded border shadow">N</div>
                  </td>
                </tr>
                <tr>
                  <td className="text-right pr-2">Open File</td>
                  <td className="text-left pl-2 flex items-center space-x-1 text-xs">
                    <div className="bg-gray-100 py-0.5 px-2 rounded border shadow">Ctrl</div>
                    <div>+</div>
                    <div className="bg-gray-100 py-0.5 px-2 rounded border shadow">O</div>
                  </td>
                </tr>
                <tr>
                  <td className="text-right pr-2">Exit</td>
                  <td className="text-left pl-2 flex items-center space-x-1 text-xs">
                    <div className="bg-gray-100 py-0.5 px-2 rounded border shadow">Alt</div>
                    <div>+</div>
                    <div className="bg-gray-100 py-0.5 px-2 rounded border shadow">F4</div>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}
