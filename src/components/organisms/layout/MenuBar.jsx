import React from 'react';
import FileMenu from './FileMenu';
import EditMenu from './EditMenu';
import HelpMenu from './HelpMenu';

/**
 * The default window menu bar. Contains the menu items and search bar.
 *
 * @return {*} The component.
 */
export default function MenuBar() {
  return (
    <div className="bg-gray-100 text-gray-800 w-full h-8 flex">
      <FileMenu />
      <EditMenu />
      <HelpMenu />
    </div>
  );
}
