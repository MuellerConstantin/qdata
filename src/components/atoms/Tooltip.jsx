import React, {useState, Fragment} from 'react';
import PropTypes from 'prop-types';
import {usePopper} from 'react-popper';
import {Transition} from '@headlessui/react';

/**
 * Simple tooltip component.
 *
 * @return {*} The component.
 */
export default function Tooltip({text, anchorRef, show}) {
  const [popupDialogElement, setPopupDialogElement] = useState();

  const {styles, attributes} = usePopper(anchorRef, popupDialogElement, {
    placement: 'bottom-start',
    modifiers: [
      {
        name: 'flip',
        options: {
          fallbackPlacements: ['bottom-end', 'top-end', 'top-start', 'left', 'right'],
        },
      },
      {
        name: 'offset',
        options: {
          offset: [10, 10],
        },
      },
    ],
  });

  if (show) {
    return (
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
            'w-fit max-w-[20rem] bg-gray-800 opacity-90 text-white shadow-lg ring-1 ring-gray-400 rounded ' +
            'focus:outline-none divide-y divide-gray-300 z-50'
          }
          style={{...styles.popper}}
          {...attributes.popper}
        >
          <div className="p-1 text-xs truncate">{text}</div>
        </div>
      </Transition>
    );
  } else {
    return null;
  }
}

Tooltip.propTypes = {
  text: PropTypes.string,
  anchorRef: PropTypes.object,
  show: PropTypes.bool,
};
