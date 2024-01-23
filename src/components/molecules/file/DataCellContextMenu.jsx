import React, {Fragment, useEffect, useState} from 'react';
import PropTypes from 'prop-types';
import {Transition} from '@headlessui/react';
import {usePopper} from 'react-popper';

/**
 * The context menu for a data table cell.
 *
 * @return {*} The component.
 */
export default function DataCellContextMenu({show, onClose, position, context, onFilter}) {
  const [popupAnchorElement, setPopupAnchorElement] = useState();
  const [popupDialogElement, setPopupDialogElement] = useState();

  const {styles, attributes} = usePopper(popupAnchorElement, popupDialogElement, {
    placement: 'bottom-start',
    modifiers: [
      {
        name: 'flip',
        options: {
          fallbackPlacements: ['bottom-end', 'top-end', 'top-start', 'left', 'right'],
        },
      },
    ],
  });

  useEffect(() => {
    const handleClickOutside = (event) => {
      if (popupDialogElement && !popupDialogElement.contains(event.target)) {
        onClose?.();
      }
    };

    document.addEventListener('click', handleClickOutside, true);
    document.addEventListener('contextmenu', handleClickOutside, true);

    return () => {
      document.removeEventListener('click', handleClickOutside, true);
      document.removeEventListener('contextmenu', handleClickOutside, true);
    };
  }, [onClose, popupDialogElement]);

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
            ref={setPopupDialogElement}
            className={
              'min-w-[14rem] max-w-[20rem] top-[20px] bg-white shadow-lg ring-1 ring-gray-800/5 ' +
              'focus:outline-none divide-y divide-gray-300 z-50 mt-2'
            }
            style={{...styles.popper}}
            {...attributes.popper}
          >
            <div className="pb-2">
              <div>
                <button
                  className={
                    'hover:bg-green-600 hover:text-white text-gray-800 group flex w-full ' +
                    'items-center h-8 px-4 text-sm justify-between space-x-2'
                  }
                  onClick={() => {
                    navigator.clipboard.writeText(context.value);
                    onClose?.();
                  }}
                >
                  <span className="truncate">Copy</span>
                  <span>Ctrl+C</span>
                </button>
              </div>
            </div>
            <div className="pb-2">
              <div>
                <button
                  className={
                    'hover:bg-green-600 hover:text-white text-gray-800 group flex w-full ' +
                    'items-center h-8 px-4 text-sm space-x-1'
                  }
                  onClick={() => {
                    onFilter?.(context.value);
                    onClose?.();
                  }}
                >
                  <span className="min-w-fit">Filter for</span>
                  <span className="truncate font-bold">{context.value}</span>
                </button>
              </div>
            </div>
          </div>
        </Transition>
        <div
          ref={setPopupAnchorElement}
          style={{position: 'fixed', left: position.x, top: position.y, visibility: 'hidden'}}
        />
      </>
    );
  } else {
    return null;
  }
}

DataCellContextMenu.propTypes = {
  show: PropTypes.bool,
  onClose: PropTypes.func,
  position: PropTypes.shape({
    x: PropTypes.number,
    y: PropTypes.number,
  }),
  context: PropTypes.shape({
    row: PropTypes.number,
    column: PropTypes.string,
    value: PropTypes.any,
  }),
  onFilter: PropTypes.func,
};
