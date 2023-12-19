import React, {useEffect, useState} from 'react';
import {FontAwesomeIcon} from '@fortawesome/react-fontawesome';
import {faTimes} from '@fortawesome/free-solid-svg-icons';

/**
 * Component for viewing the contents of a QVD file.
 *
 * @return {*} The component
 */
export default function QvdView() {
  const [fileName, setFileName] = useState(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    window.electron.ipc.on('openingFile', ({name}) => {
      setFileName(name);
      setLoading(true);
    });

    window.electron.ipc.on('openedFile', () => {
      setLoading(false);
    });

    window.electron.ipc.on('closedFile', () => {
      setFileName(null);
      setLoading(false);
    });
  }, []);

  return (
    <div className="bg-white text-gray-800 w-full h-full flex flex-col">
      <div className="bg-gray-100 px-2 pt-2 border-t border-b h-10">
        {fileName && (
          <div
            className={
              'bg-white rounded-t flex items-center justify-center w-fit h-8 max-w-[250px] ' +
              'px-2 space-x-2 border-b-2 border-b-green-600 border-t border-l border-r'
            }
          >
            <span className="truncate text-sm">{fileName}</span>
            <button
              className="text-gray-800 hover:text-gray-600 focus:outline-none"
              onClick={() => window.electron.ipc.send('closeFile')}
            >
              <FontAwesomeIcon icon={faTimes} />
            </button>
          </div>
        )}
      </div>
      <div
        className={
          'flex flex-col grow h-0 overflow-y-auto scrollbar-thin scrollbar-thumb-gray-600 scrollbar-track-gray-200'
        }
      >
        {fileName ? (
          loading ? (
            <div className="text-center p-2">Loading file...</div>
          ) : (
            <div className="text-center p-2">File loaded successfully.</div>
          )
        ) : (
          <div className="text-center p-2">No content to display.</div>
        )}
      </div>
    </div>
  );
}
