import React, {Fragment, useState} from 'react';
import {Menu, Transition} from '@headlessui/react';
import {usePopper} from 'react-popper';
import AboutDialog from '../help/AboutDialog';

/**
 * The help menu with help operations.
 *
 * @return {*} The component
 */
export default function HelpMenu() {
  const [showAboutDialog, setShowAboutDialog] = useState(false);

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
    <>
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
                Help
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
                className={'w-56 bg-white shadow-lg ring-1 ring-gray-800/5 focus:outline-none divide-y divide-gray-300'}
                style={styles.popper}
                {...attributes.popper}
              >
                <div className="pb-2">
                  <Menu.Item>
                    {({active}) => (
                      <button
                        className={`${
                          active ? 'bg-green-600 text-white' : 'text-gray-800'
                        } group flex w-full items-center h-8 px-4 text-sm`}
                        onClick={() => setShowAboutDialog(true)}
                      >
                        About
                      </button>
                    )}
                  </Menu.Item>
                </div>
              </Menu.Items>
            </Transition>
          </>
        )}
      </Menu>
      <AboutDialog isOpen={showAboutDialog} onClose={() => setShowAboutDialog(false)} />
    </>
  );
}
