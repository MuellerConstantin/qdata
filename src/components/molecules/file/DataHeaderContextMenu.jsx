import React, {Fragment, useEffect, useState} from 'react';
import PropTypes from 'prop-types';
import {Transition} from '@headlessui/react';
import {usePopper} from 'react-popper';

/**
 * The context menu for a data table header.
 *
 * @return {*} The component.
 */
export default function DataHeaderContextMenu({show, onClose, position, context}) {
  const [mainPopupAnchorElement, setMainPopupAnchorElement] = useState();
  const [mainPopupDialogElement, setMainPopupDialogElement] = useState();

  const {styles: mainPopupStyles, attributes: mainPopupAttributes} = usePopper(
    mainPopupAnchorElement,
    mainPopupDialogElement,
    {
      placement: 'bottom-start',
      modifiers: [
        {
          name: 'flip',
          options: {
            fallbackPlacements: ['bottom-end', 'top-end', 'top-start', 'left', 'right'],
          },
        },
      ],
    },
  );

  useEffect(() => {
    const handleClickOutside = (event) => {
      if (mainPopupDialogElement && !mainPopupDialogElement.contains(event.target)) {
        onClose?.();
      }
    };

    document.addEventListener('click', handleClickOutside, true);
    document.addEventListener('contextmenu', handleClickOutside, true);

    return () => {
      document.removeEventListener('click', handleClickOutside, true);
      document.removeEventListener('contextmenu', handleClickOutside, true);
    };
  }, [onClose, mainPopupDialogElement]);

  if (show) {
    return (
      <>
        <Transition
          show
          as={Fragment}
          enter="transition ease-out duration-100"
          enterFrom="transform opacity-0 scale-95"
          enterTo="transform opacity-100 scale-100"
          leave="transition ease-in duration-75"
          leaveFrom="transform opacity-100 scale-100"
          leaveTo="transform opacity-0 scale-95"
        >
          <div
            ref={setMainPopupDialogElement}
            className={
              'min-w-[14rem] max-w-[20rem] bg-white shadow-lg ring-1 ring-gray-800/5 ' +
              'focus:outline-none divide-y divide-gray-300 z-50'
            }
            style={{...mainPopupStyles.popper}}
            {...mainPopupAttributes.popper}
          >
            <div className="pb-2">
              <div>
                <button
                  className={
                    'hover:bg-green-600 hover:text-white text-gray-800 group flex w-full ' +
                    'items-center h-8 px-4 text-sm justify-between space-x-2'
                  }
                  onClick={() => {
                    navigator.clipboard.writeText(context.column);
                    onClose?.();
                  }}
                >
                  <span className="truncate">Copy Column Name</span>
                </button>
              </div>
            </div>
          </div>
        </Transition>
        <div
          ref={setMainPopupAnchorElement}
          style={{position: 'fixed', left: position.x, top: position.y, visibility: 'hidden'}}
        />
      </>
    );
  } else {
    return null;
  }
}

DataHeaderContextMenu.propTypes = {
  show: PropTypes.bool,
  onClose: PropTypes.func,
  position: PropTypes.shape({
    x: PropTypes.number,
    y: PropTypes.number,
  }),
  context: PropTypes.shape({
    column: PropTypes.string,
  }),
};
