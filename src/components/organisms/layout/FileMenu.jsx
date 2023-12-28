import React, {Fragment, useState, useEffect} from 'react';
import {Menu, Transition} from '@headlessui/react';
import {usePopper} from 'react-popper';

/**
 * The file menu with file operations.
 *
 * @return {*} The component
 */
export default function FileMenu() {
  const [fileOpen, setFileOpen] = useState(false);

  useEffect(() => {
    window.electron.ipc.on('openedFile', () => {
      setFileOpen(true);
    });

    window.electron.ipc.on('closedFile', () => {
      setFileOpen(false);
    });
  }, []);

  useEffect(() => {
    const handleCtrlO = (event) => {
      if (event.ctrlKey && event.code === 'KeyO') {
        window.electron.ipc.invoke('openFile');
      }
    };

    window.addEventListener('keydown', handleCtrlO);
    return () => window.removeEventListener('keydown', handleCtrlO);
  }, []);

  useEffect(() => {
    const handleCtrlN = (event) => {
      if (event.ctrlKey && event.code === 'KeyN') {
        window.electron.ipc.send('newWindow');
      }
    };

    window.addEventListener('keydown', handleCtrlN);
    return () => window.removeEventListener('keydown', handleCtrlN);
  }, []);

  const [popupButtonElement, setPopupButtonElement] = useState();
  const [popupDialogElement, setPopupDialogElement] = useState();
  const {styles, attributes} = usePopper(popupButtonElement, popupDialogElement, {
    placement: 'bottom-end',
    modifiers: [
      {
        name: 'flip',
        options: {
          fallbackPlacements: ['bottom-start', 'top-end', 'top-start', 'left', 'right'],
        },
      },
    ],
  });

  return (
    <Menu as="div" className="relative inline-block text-left">
      {({open}) => (
        <>
          <div>
            <Menu.Button
              ref={setPopupButtonElement}
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
              ref={setPopupDialogElement}
              className={
                'w-56 bg-white shadow-lg ring-1 ring-gray-800/5 focus:outline-none divide-y divide-gray-300 z-50'
              }
              style={styles.popper}
              {...attributes.popper}
            >
              <div className="pb-2">
                <Menu.Item>
                  {({active}) => (
                    <button
                      className={`${
                        active ? 'bg-green-600 text-white' : 'text-gray-800'
                      } group flex w-full items-center h-8 px-4 text-sm justify-between space-x-2`}
                      onClick={() => window.electron.ipc.send('newWindow')}
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
                      onClick={() => window.electron.ipc.send('closeWindow')}
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
                      onClick={() => window.electron.ipc.invoke('openFile')}
                    >
                      <span className="truncate">Open File...</span>
                      <span>Ctrl+O</span>
                    </button>
                  )}
                </Menu.Item>

                <Menu.Item>
                  {({active}) => (
                    <button
                      className={`${
                        active ? 'bg-green-600 text-white' : 'text-gray-800'
                      } group flex w-full items-center h-8 px-4 text-sm disabled:opacity-50`}
                      onClick={() => window.electron.ipc.send('closeFile')}
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
                      onClick={() => window.electron.ipc.send('exitApp')}
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
