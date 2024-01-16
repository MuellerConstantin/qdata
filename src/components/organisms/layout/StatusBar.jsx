import React from 'react';
import useStatus from '../../../hooks/useStatus';

/**
 * The default window status bar. Contains status information and controls.
 *
 * @return {*} The component.
 */
export default function StatusBar() {
  const {} = useStatus();

  return <div className="bg-gray-100 text-gray-800 w-full h-8 flex border-t px-2 items-center text-sm space-x-4" />;
}
