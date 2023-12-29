import React from 'react';
import {useSelector} from 'react-redux';
import {FontAwesomeIcon} from '@fortawesome/react-fontawesome';
import {faArrowUpRightFromSquare, faArrowRightFromBracket, faFolderOpen} from '@fortawesome/free-solid-svg-icons';

import LogoTextDark from '../../../assets/images/logo-text-dark.svg';

/**
 * This view is shown by default when the application is opened.
 *
 * @return {*} The component.
 */
export default function GettingStartedView() {
  const recentFiles = useSelector((state) => state.files.recentFiles);

  return (
    <div className="flex justify-center items-center h-full w-full p-12 select-none">
      <div className="h-full w-full space-y-8">
        <div className="space-y-1">
          <img src={LogoTextDark} alt="QData" className="h-24 w-auto -ml-2 drag-none" />
          <div className="text-4xl font-light">Getting Started</div>
        </div>
        <div className="w-full grid grid-cols-2 gap-4">
          <div className="space-y-4">
            <div className="text-2xl">Start</div>
            <div className="space-y-2">
              <div
                className="flex items-center justify-left space-x-2 hover:cursor-pointer w-fit"
                onClick={() => window.electron.ipc.send('newWindow')}
              >
                <FontAwesomeIcon icon={faArrowUpRightFromSquare} className="h-5 w-5 text-green-600" />
                <span>New Window</span>
              </div>
              <div
                className="flex items-center justify-left space-x-2 hover:cursor-pointer w-fit"
                onClick={() => window.electron.ipc.invoke('openFile')}
              >
                <FontAwesomeIcon icon={faFolderOpen} className="h-5 w-5 text-green-600" />
                <span>Open File...</span>
              </div>
              <div
                className="flex items-center justify-left space-x-2 hover:cursor-pointer w-fit"
                onClick={() => window.electron.ipc.send('exitApp')}
              >
                <FontAwesomeIcon icon={faArrowRightFromBracket} className="h-5 w-5 text-green-600" />
                <span>Exit</span>
              </div>
            </div>
          </div>
          <div className="space-y-4">
            <div className="text-2xl">Recent</div>
            {(!recentFiles || recentFiles.length <= 0) && <div className="space-y-2">No recent files yet.</div>}
            {recentFiles && recentFiles.length > 0 && (
              <div className="space-y-2">
                {recentFiles.slice(0, 5).map((recentFile) => (
                  <div
                    key={recentFile}
                    className={
                      'group flex items-center justify-left space-x-2 hover:cursor-pointer ' + 'w-fit max-w-full'
                    }
                    onClick={() => window.electron.ipc.invoke('openRecentFile', recentFile)}
                  >
                    <span className="truncate space-x-2">
                      <span className="text-green-600 group-hover:underline">{recentFile.replace(/^.*[\\/]/, '')}</span>
                      <span className="group-hover:underline">{recentFile.replace(/[\\/]\w+\.\w+$/, '')}</span>
                    </span>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
