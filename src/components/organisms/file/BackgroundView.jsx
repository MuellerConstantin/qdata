import React from 'react';

import Watermark from '../../../assets/images/watermark.svg';

/**
 * This view is shown when there is no file opened.
 *
 * @return {*} The component.
 */
export default function BackgroundView() {
  return (
    <div className="flex justify-center items-center h-full w-full space-x-2 select-none p-4">
      <div className="flex flex-col items-center max-w-[500px] space-y-4">
        <img src={Watermark} alt="Logo" className="w-auto h-64 drag-none object-contain" />
        <table className="border-separate border-spacing-y-2">
          <tbody>
            <tr>
              <td className="text-right pr-2">New Window</td>
              <td className="text-left pl-2 flex items-center space-x-1 text-xs">
                <div className="bg-gray-100 py-0.5 px-2 rounded border shadow">Ctrl</div>
                <div>+</div>
                <div className="bg-gray-100 py-0.5 px-2 rounded border shadow">N</div>
              </td>
            </tr>
            <tr>
              <td className="text-right pr-2">Open File</td>
              <td className="text-left pl-2 flex items-center space-x-1 text-xs">
                <div className="bg-gray-100 py-0.5 px-2 rounded border shadow">Ctrl</div>
                <div>+</div>
                <div className="bg-gray-100 py-0.5 px-2 rounded border shadow">O</div>
              </td>
            </tr>
            <tr>
              <td className="text-right pr-2">Exit</td>
              <td className="text-left pl-2 flex items-center space-x-1 text-xs">
                <div className="bg-gray-100 py-0.5 px-2 rounded border shadow">Alt</div>
                <div>+</div>
                <div className="bg-gray-100 py-0.5 px-2 rounded border shadow">F4</div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  );
}
