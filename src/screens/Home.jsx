import React, {useState, useEffect} from 'react';
import {useDispatch} from 'react-redux';
import {Tab} from '@headlessui/react';
import {FontAwesomeIcon} from '@fortawesome/react-fontawesome';
import {faTimes} from '@fortawesome/free-solid-svg-icons';
import BorderTemplate from '../components/templates/BorderTemplate';
import FileView from '../components/organisms/file/FileView';
import BackgroundView from '../components/organisms/file/BackgroundView';
import GettingStartedView from '../components/organisms/file/GettingStartedView';
import filesSlice from '../store/slices/files';

/**
 * The landing page of the application.
 *
 * @return {*} The component.
 */
export default function Home() {
  const dispatch = useDispatch();

  const [selectedTab, setSelectedTab] = useState(0);
  const [showGettingStarted, setShowGettingStarted] = useState(true);
  const [fileName, setFileName] = useState(null);
  const [table, setTable] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    window.electron.ipc
      .invoke('file:getRecentFiles')
      .then((recentFiles) => dispatch(filesSlice.actions.setRecentFiles(recentFiles)));

    window.electron.ipc.on('file:recentFilesChanged', (recentFiles) =>
      dispatch(filesSlice.actions.setRecentFiles(recentFiles)),
    );

    window.electron.ipc.on('file:opening', ({name}) => {
      setShowGettingStarted(false);
      setLoading(true);
      setError(null);
      setFileName(name);
    });

    window.electron.ipc.on('error:parsingFileFailed', () => {
      setLoading(false);
      setError('error:parsingFileFailed');
    });

    window.electron.ipc.on('error:fileNotFound', () => {
      setLoading(false);
      setError('error:fileNotFound');
    });

    window.electron.ipc.on('file:opened', ({table}) => {
      setLoading(false);
      setTable(table);
    });

    window.electron.ipc.on('file:closed', () => {
      setLoading(false);
      setFileName(null);
      setError(null);
      setTable(null);
    });
  }, []);

  return (
    <BorderTemplate>
      {showGettingStarted || fileName ? (
        <div className="bg-white text-gray-800 w-full h-full flex flex-col">
          <Tab.Group selectedIndex={selectedTab} onChange={(index) => setSelectedTab(index)}>
            <Tab.List className="bg-gray-100 px-2 pt-2 border-t border-b h-12 flex">
              {showGettingStarted && (
                <Tab
                  className={({selected}) =>
                    'bg-white flex items-center justify-between w-fit h-10 max-w-[250px] min-w-[100px] ' +
                    `px-2 space-x-6 ${
                      selected ? 'border-t-2 border-t-green-600' : 'border-t border-b'
                    } border-l border-r select-none`
                  }
                >
                  <span className="truncate text-sm">Getting Started</span>
                  <div
                    className="text-gray-800 hover:text-gray-600 focus:outline-none flex items-center justify-center"
                    onClick={() => setShowGettingStarted(false)}
                  >
                    <FontAwesomeIcon icon={faTimes} className="w-4 h-4" />
                  </div>
                </Tab>
              )}
              {fileName && (
                <Tab
                  className={({selected}) =>
                    'bg-white flex items-center justify-between w-fit h-10 max-w-[250px] min-w-[100px] ' +
                    `px-2 space-x-6 ${
                      selected ? 'border-t-2 border-t-green-600' : 'border-t border-b'
                    } border-l border-r select-none`
                  }
                >
                  <span className="truncate text-sm">{fileName}</span>
                  <div
                    className="text-gray-800 hover:text-gray-600 focus:outline-none flex items-center justify-center"
                    onClick={() => {
                      window.electron.ipc.send('file:close');
                      setSelectedTab(0);
                    }}
                  >
                    <FontAwesomeIcon icon={faTimes} className="w-4 h-4" />
                  </div>
                </Tab>
              )}
            </Tab.List>
            <Tab.Panels className="w-full h-full">
              {showGettingStarted && (
                <Tab.Panel className="h-full w-full">
                  <GettingStartedView />
                </Tab.Panel>
              )}
              {fileName && (
                <Tab.Panel className="h-full w-full">
                  <div className="w-full h-full flex flex-col">
                    <FileView loading={loading} error={error} table={table} fileName={fileName} />
                  </div>
                </Tab.Panel>
              )}
            </Tab.Panels>
          </Tab.Group>
        </div>
      ) : (
        <BackgroundView />
      )}
    </BorderTemplate>
  );
}
