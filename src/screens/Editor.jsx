import React, {useState, useEffect, useCallback} from 'react';
import {useDispatch} from 'react-redux';
import {Tab} from '@headlessui/react';
import {FontAwesomeIcon} from '@fortawesome/react-fontawesome';
import {faTimes} from '@fortawesome/free-solid-svg-icons';
import {useMap} from '@uidotdev/usehooks';
import BorderTemplate from '../components/templates/BorderTemplate';
import FileView from '../components/organisms/file/FileView';
import BackgroundView from '../components/organisms/layout/BackgroundView';
import GettingStartedView from '../components/organisms/layout/GettingStartedView';
import filesSlice from '../store/slices/files';

/**
 * The landing page of the application.
 *
 * @return {*} The component.
 */
export default function Editor() {
  const dispatch = useDispatch();

  const [selectedTab, setSelectedTab] = useState(0);
  const [showGettingStarted, setShowGettingStarted] = useState(true);
  const files = useMap();

  const addFile = useCallback((path, name) => {
    files.set(path, {
      name,
      table: null,
      loading: true,
      error: null,
    });
  }, []);

  const setFileLoaded = useCallback((path, table) => {
    files.set(path, {
      ...files.get(path),
      loading: false,
      table,
    });
  }, []);

  const setFileError = useCallback((path, error) => {
    files.set(path, {
      ...files.get(path),
      loading: false,
      error,
    });
  }, []);

  const removeFile = useCallback((path) => {
    files.delete(path);
  }, []);

  useEffect(() => {
    window.electron.ipcMain
      .invoke('file:getRecentFiles')
      .then((recentFiles) => dispatch(filesSlice.actions.setRecentFiles(recentFiles)));

    window.electron.ipcMain.on('file:recentFilesChanged', (recentFiles) =>
      dispatch(filesSlice.actions.setRecentFiles(recentFiles)),
    );

    window.electron.ipcMain.on('file:opening', ({name, path}) => {
      setShowGettingStarted(false);
      addFile(path, name);
      setSelectedTab(Array.from(files.keys()).length - 1);
    });

    window.electron.ipcMain.on('error:parsingFileFailed', ({path}) => {
      setFileError(path, 'error:parsingFileFailed');
    });

    window.electron.ipcMain.on('error:fileNotFound', ({path}) => {
      setFileError(path, 'error:fileNotFound');
    });

    window.electron.ipcMain.on('file:opened', ({path, table}) => {
      setFileLoaded(path, table);
    });

    window.electron.ipcMain.on('file:closed', (path) => {
      removeFile(path);
      setSelectedTab(0);
    });
  }, []);

  return (
    <BorderTemplate>
      {showGettingStarted || files.size > 0 ? (
        <div className="bg-white text-gray-800 w-full h-full flex flex-col">
          <Tab.Group selectedIndex={selectedTab} onChange={(index) => setSelectedTab(index)}>
            <Tab.List
              className={
                'bg-gray-100 px-2 pt-4 border-t border-b flex overflow-x-auto overflow-y-hidden ' +
                'scrollbar-thin scrollbar-thumb-gray-400 scrollbar-track-gray-200'
              }
            >
              {showGettingStarted && (
                <Tab
                  className={({selected}) =>
                    'bg-white flex items-center justify-between w-fit h-10 max-w-[250px] ' +
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
              {Array.from(files.keys()).map((path) => (
                <Tab
                  key={path}
                  className={({selected}) =>
                    'bg-white flex items-center justify-between w-fit h-10 max-w-[250px] ' +
                    `px-2 space-x-6 ${
                      selected ? 'border-t-2 border-t-green-600' : 'border-t border-b'
                    } border-l border-r select-none`
                  }
                >
                  <span className="truncate text-sm">{files.get(path).name}</span>
                  <div
                    className="text-gray-800 hover:text-gray-600 focus:outline-none flex items-center justify-center"
                    onClick={() => {
                      window.electron.ipcMain.send('file:close', path);
                    }}
                  >
                    <FontAwesomeIcon icon={faTimes} className="w-4 h-4" />
                  </div>
                </Tab>
              ))}
            </Tab.List>
            <Tab.Panels className="w-full h-full">
              {showGettingStarted && (
                <Tab.Panel className="h-full w-full">
                  <GettingStartedView />
                </Tab.Panel>
              )}
              {Array.from(files.keys()).map((path) => (
                <Tab.Panel key={path} className="h-full w-full" unmount={false}>
                  {({selected}) => (
                    <div className="w-full h-full flex flex-col">
                      <FileView
                        active={selected}
                        loading={files.get(path).loading}
                        error={files.get(path).error}
                        table={files.get(path).table}
                        fileName={files.get(path).name}
                        filePath={path}
                      />
                    </div>
                  )}
                </Tab.Panel>
              ))}
            </Tab.Panels>
          </Tab.Group>
        </div>
      ) : (
        <BackgroundView />
      )}
    </BorderTemplate>
  );
}
