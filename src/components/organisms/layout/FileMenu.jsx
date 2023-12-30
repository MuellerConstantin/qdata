import React, {Fragment, useState, useEffect} from 'react';
import {useSelector} from 'react-redux';
import {Menu, Transition} from '@headlessui/react';
import {usePopper} from 'react-popper';
import {FontAwesomeIcon} from '@fortawesome/react-fontawesome';
import {faChevronRight} from '@fortawesome/free-solid-svg-icons';

/**
 * The file menu with file operations.
 *
 * @return {*} The component.
 */
export default function FileMenu() {
  // eslint-disable-next-line no-unused-vars
  const recentFiles = useSelector((state) => state.files.recentFiles);

  const [fileOpen, setFileOpen] = useState(false);

  useEffect(() => {
    window.electron.ipc.on('file:opened', () => {
      setFileOpen(true);
    });

    window.electron.ipc.on('file:closed', () => {
      setFileOpen(false);
    });
  }, []);

  useEffect(() => {
    const handleCtrlO = (event) => {
      if (event.ctrlKey && event.code === 'KeyO') {
        window.electron.ipc.invoke('file:open');
      }
    };

    window.addEventListener('keydown', handleCtrlO);
    return () => window.removeEventListener('keydown', handleCtrlO);
  }, []);

  useEffect(() => {
    const handleCtrlN = (event) => {
      if (event.ctrlKey && event.code === 'KeyN') {
        window.electron.ipc.send('window:new');
      }
    };

    window.addEventListener('keydown', handleCtrlN);
    return () => window.removeEventListener('keydown', handleCtrlN);
  }, []);

  const [mainPopupButtonElement, setMainPopupButtonElement] = useState();
  const [mainPopupDialogElement, setMainPopupDialogElement] = useState();
  const {styles: mainPopupStyles, attributes: mainPopupAttributes} = usePopper(
    mainPopupButtonElement,
    mainPopupDialogElement,
    {
      placement: 'bottom-end',
      modifiers: [
        {
          name: 'flip',
          options: {
            fallbackPlacements: ['bottom-start', 'top-end', 'top-start', 'left', 'right'],
          },
        },
      ],
    },
  );

  const [recentPopupButtonElement, setRecentPopupButtonElement] = useState();
  const [recentPopupDialogElement, setRecentPopupDialogElement] = useState();
  const {styles: recentPopupStyles, attributes: recentPopupAttributes} = usePopper(
    recentPopupButtonElement,
    recentPopupDialogElement,
    {
      placement: 'right-start',
      modifiers: [
        {
          name: 'flip',
          options: {
            fallbackPlacements: ['left-start', 'bottom-start', 'bottom-end', 'left', 'right'],
          },
        },
      ],
    },
  );

  return (
    <Menu as="div" className="relative inline-block text-left">
      {({open}) => (
        <>
          <div>
            <Menu.Button
              ref={setMainPopupButtonElement}
              className={
                'flex w-full h-8 justify-center items-center px-2 text-sm text-gray-800 ' +
                `hover:bg-gray-300 focus:outline-none ${open ? 'bg-gray-300' : ''}`
              }
            >
              File
            </Menu.Button>
          </div>
          <Transition
            as={Fragment}
            enter="transition ease-out duration-100"
            enterFrom="transform opacity-0 scale-95"
            enterTo="transform opacity-100 scale-100"
            leave="transition ease-in duration-75"
            leaveFrom="transform opacity-100 scale-100"
            leaveTo="transform opacity-0 scale-95"
          >
            <Menu.Items
              ref={setMainPopupDialogElement}
              className={
                'w-56 bg-white shadow-lg ring-1 ring-gray-800/5 focus:outline-none divide-y divide-gray-300 z-50'
              }
              style={mainPopupStyles.popper}
              {...mainPopupAttributes.popper}
            >
              <div className="pb-2">
                <Menu.Item>
                  {({active}) => (
                    <button
                      className={`${
                        active ? 'bg-green-600 text-white' : 'text-gray-800'
                      } group flex w-full items-center h-8 px-4 text-sm justify-between space-x-2`}
                      onClick={() => window.electron.ipc.send('window:new')}
                    >
                      <span className="truncate">New Window</span>
                      <span>Ctrl+N</span>
                    </button>
                  )}
                </Menu.Item>
                <Menu.Item>
                  {({active}) => (
                    <button
                      className={`${
                        active ? 'bg-green-600 text-white' : 'text-gray-800'
                      } group flex w-full items-center h-8 px-4 text-sm disabled:opacity-50`}
                      onClick={() => window.electron.ipc.send('window:close')}
                    >
                      <span className="truncate">Close Window</span>
                    </button>
                  )}
                </Menu.Item>
              </div>
              <div className="pb-2">
                <Menu.Item>
                  {({active}) => (
                    <button
                      className={`${
                        active ? 'bg-green-600 text-white' : 'text-gray-800'
                      } group flex w-full items-center h-8 px-4 text-sm justify-between space-x-2`}
                      onClick={() => window.electron.ipc.invoke('file:open')}
                    >
                      <span className="truncate">Open File...</span>
                      <span>Ctrl+O</span>
                    </button>
                  )}
                </Menu.Item>
                <Menu.Item className="w-full">
                  {({active}) => (
                    <Menu as="div" className="relative inline-block text-left">
                      {({open}) => (
                        <>
                          <div>
                            <Menu.Button
                              ref={setRecentPopupButtonElement}
                              className={`${
                                active ? 'bg-green-600 text-white' : 'text-gray-800'
                              } group flex w-full items-center h-8 px-4 text-sm justify-between space-x-2`}
                            >
                              <span className="truncate">Open Recent...</span>
                              <FontAwesomeIcon icon={faChevronRight} className="h-3 w-3" />
                            </Menu.Button>
                          </div>
                          <Transition
                            as={Fragment}
                            enter="transition ease-out duration-100"
                            enterFrom="transform opacity-0 scale-95"
                            enterTo="transform opacity-100 scale-100"
                            leave="transition ease-in duration-75"
                            leaveFrom="transform opacity-100 scale-100"
                            leaveTo="transform opacity-0 scale-95"
                          >
                            <Menu.Items
                              ref={setRecentPopupDialogElement}
                              className={
                                'w-fit max-w-[500px] bg-white shadow-lg ring-1 ring-gray-800/5 ' +
                                'focus:outline-none divide-y divide-gray-300 z-50'
                              }
                              style={recentPopupStyles.popper}
                              {...recentPopupAttributes.popper}
                            >
                              <div className="pb-2">
                                {recentFiles?.length > 0 &&
                                  recentFiles.map((recentFile) => (
                                    <Menu.Item key={recentFile}>
                                      {({active}) => (
                                        <button
                                          className={`${
                                            active ? 'bg-green-600 text-white' : 'text-gray-800'
                                          } group flex w-full items-center h-8 px-4 text-sm justify-between space-x-2`}
                                          onClick={() => window.electron.ipc.invoke('file:openRecentFile', recentFile)}
                                        >
                                          <span className="truncate space-x-2">
                                            <span className="text-green-600 group-hover:text-white">
                                              {recentFile.replace(/^.*[\\/]/, '')}
                                            </span>
                                            <span>{recentFile.replace(/[\\/]\w+\.\w+$/, '')}</span>
                                          </span>
                                        </button>
                                      )}
                                    </Menu.Item>
                                  ))}
                              </div>
                              <div className="pb-2">
                                <Menu.Item>
                                  {({active}) => (
                                    <button
                                      className={`${
                                        active ? 'bg-green-600 text-white' : 'text-gray-800'
                                      } group flex w-full items-center h-8 px-4 text-sm justify-between space-x-2`}
                                      onClick={() => window.electron.ipc.send('file:clearRecentFiles')}
                                    >
                                      <span className="truncate">Clear Recently Opened...</span>
                                    </button>
                                  )}
                                </Menu.Item>
                              </div>
                            </Menu.Items>
                          </Transition>
                        </>
                      )}
                    </Menu>
                  )}
                </Menu.Item>
                <Menu.Item>
                  {({active}) => (
                    <button
                      className={`${
                        active ? 'bg-green-600 text-white' : 'text-gray-800'
                      } group flex w-full items-center h-8 px-4 text-sm disabled:opacity-50`}
                      onClick={() => window.electron.ipc.send('file:close')}
                      disabled={!fileOpen}
                    >
                      <span className="truncate">Close File</span>
                    </button>
                  )}
                </Menu.Item>
              </div>
              <div className="pb-2">
                <Menu.Item>
                  {({active}) => (
                    <button
                      className={`${
                        active ? 'bg-green-600 text-white' : 'text-gray-800'
                      } group flex w-full items-center h-8 px-4 text-sm justify-between space-x-2`}
                      onClick={() => window.electron.ipc.send('app:exit')}
                    >
                      <span className="truncate">Exit</span>
                      <span>Alt+F4</span>
                    </button>
                  )}
                </Menu.Item>
              </div>
            </Menu.Items>
          </Transition>
        </>
      )}
    </Menu>
  );
}
