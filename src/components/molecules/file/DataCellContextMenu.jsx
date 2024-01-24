import React, {Fragment, useEffect, useState} from 'react';
import PropTypes from 'prop-types';
import {Transition} from '@headlessui/react';
import {usePopper} from 'react-popper';
import {FontAwesomeIcon} from '@fortawesome/react-fontawesome';
import {faChevronRight} from '@fortawesome/free-solid-svg-icons';

/**
 * The context menu for a data table cell.
 *
 * @return {*} The component.
 */
export default function DataCellContextMenu({show, onClose, position, context, onFilter}) {
  const [showFilterPopup, setShowFilterPopup] = useState(false);

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

  const [filterPopupButtonElement, setFilterPopupButtonElement] = useState();
  const [filterPopupDialogElement, setFiltertPopupDialogElement] = useState();
  const {styles: filterPopupStyles, attributes: filterPopupAttributes} = usePopper(
    filterPopupButtonElement,
    filterPopupDialogElement,
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

  useEffect(() => {
    const handleClickOutside = (event) => {
      if (mainPopupDialogElement && !mainPopupDialogElement.contains(event.target)) {
        setShowFilterPopup(false);
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
                  ref={setFilterPopupButtonElement}
                  className={
                    'hover:bg-green-600 hover:text-white text-gray-800 group flex w-full ' +
                    'items-center h-8 px-4 text-sm justify-between space-x-2'
                  }
                  onClick={() => setShowFilterPopup((prev) => !prev)}
                >
                  <span className="truncate">Filter...</span>
                  <FontAwesomeIcon icon={faChevronRight} className="h-3 w-3" />
                </button>
                {showFilterPopup && (
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
                      ref={setFiltertPopupDialogElement}
                      className={
                        'min-w-[14rem] max-w-[20rem] bg-white shadow-lg ring-1 ring-gray-800/5 ' +
                        'focus:outline-none divide-y divide-gray-300 z-50'
                      }
                      style={{...filterPopupStyles.popper}}
                      {...filterPopupAttributes.popper}
                    >
                      <div className="pb-2">
                        <div>
                          <button
                            className={
                              'hover:bg-green-600 hover:text-white text-gray-800 group flex w-full ' +
                              'items-center h-8 px-4 text-sm'
                            }
                            onClick={() => {
                              onFilter?.(context.value, 'eq');
                              setShowFilterPopup(false);
                              onClose?.();
                            }}
                          >
                            <span className="min-w-fit">Equals...</span>
                          </button>
                        </div>
                        <div>
                          <button
                            className={
                              'hover:bg-green-600 hover:text-white text-gray-800 group flex w-full ' +
                              'items-center h-8 px-4 text-sm'
                            }
                            onClick={() => {
                              onFilter?.(context.value, 'ne');
                              setShowFilterPopup(false);
                              onClose?.();
                            }}
                          >
                            <span className="min-w-fit">Not Equals...</span>
                          </button>
                        </div>
                        <div>
                          <button
                            className={
                              'hover:bg-green-600 hover:text-white text-gray-800 group flex w-full ' +
                              'items-center h-8 px-4 text-sm'
                            }
                            onClick={() => {
                              onFilter?.(context.value, 'gt');
                              setShowFilterPopup(false);
                              onClose?.();
                            }}
                          >
                            <span className="min-w-fit">Greater than...</span>
                          </button>
                        </div>
                        <div>
                          <button
                            className={
                              'hover:bg-green-600 hover:text-white text-gray-800 group flex w-full ' +
                              'items-center h-8 px-4 text-sm'
                            }
                            onClick={() => {
                              onFilter?.(context.value, 'ge');
                              setShowFilterPopup(false);
                              onClose?.();
                            }}
                          >
                            <span className="min-w-fit">Greater than or Equals...</span>
                          </button>
                        </div>
                        <div>
                          <button
                            className={
                              'hover:bg-green-600 hover:text-white text-gray-800 group flex w-full ' +
                              'items-center h-8 px-4 text-sm'
                            }
                            onClick={() => {
                              onFilter?.(context.value, 'lt');
                              setShowFilterPopup(false);
                              onClose?.();
                            }}
                          >
                            <span className="min-w-fit">Less than...</span>
                          </button>
                        </div>
                        <div>
                          <button
                            className={
                              'hover:bg-green-600 hover:text-white text-gray-800 group flex w-full ' +
                              'items-center h-8 px-4 text-sm'
                            }
                            onClick={() => {
                              onFilter?.(context.value, 'le');
                              setShowFilterPopup(false);
                              onClose?.();
                            }}
                          >
                            <span className="min-w-fit">Less than or Equals...</span>
                          </button>
                        </div>
                      </div>
                    </div>
                  </Transition>
                )}
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
