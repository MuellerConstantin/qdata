import React, {Fragment, useEffect, useState} from 'react';
import PropTypes from 'prop-types';
import {Dialog, Transition} from '@headlessui/react';
import Button from '../../atoms/Button';

import LogoTextDark from '../../../assets/images/logo-text-dark.svg';

/**
 * Dialog for viewing about information.
 *
 * @return {*} The component
 */
export default function AboutDialog({onClose, isOpen}) {
  const [appVersion, setAppVersion] = useState(null);
  const [archInfo, setArchInfo] = useState(null);
  const [electronVersion, setElectronVersion] = useState(null);
  const [nodeVersion, setNodeVersion] = useState(null);
  const [v8Version, setV8Version] = useState(null);
  const [osInfo, setOsInfo] = useState(null);

  useEffect(() => {
    window.electron.ipc.invoke('getAppVersion').then((appVersion) => setAppVersion(appVersion));
    window.electron.ipc.invoke('getArchInfo').then((archInfo) => setArchInfo(archInfo));
    window.electron.ipc.invoke('getElectronVersion').then((electronVersion) => setElectronVersion(electronVersion));
    window.electron.ipc.invoke('getNodeVersion').then((nodeVersion) => setNodeVersion(nodeVersion));
    window.electron.ipc.invoke('getV8Version').then((v8Version) => setV8Version(v8Version));
    window.electron.ipc.invoke('getOsInfo').then((osInfo) => setOsInfo(osInfo));
  }, []);

  return (
    <Transition appear show={isOpen} as={Fragment}>
      <Dialog as="div" onClose={onClose} className="fixed inset-0 z-10 overflow-y-auto">
        <div className="h-screen overflow-hidden p-4 flex items-center justify-center">
          <Transition.Child
            as={Fragment}
            enter="ease-out duration-300"
            enterFrom="opacity-0"
            enterTo="opacity-100"
            leave="ease-in duration-200"
            leaveFrom="opacity-100"
            leaveTo="opacity-0"
          >
            <Dialog.Overlay className="fixed inset-0 bg-gray-800 opacity-60" />
          </Transition.Child>
          <Transition.Child
            as={Fragment}
            enter="ease-out duration-300"
            enterFrom="opacity-0 scale-95"
            enterTo="opacity-100 scale-100"
            leave="ease-in duration-200"
            leaveFrom="opacity-100 scale-100"
            leaveTo="opacity-0 scale-95"
          >
            <Dialog.Panel
              className={
                'inline-block max-h-[calc(100%-2rem)] h-fit w-full max-w-md overflow-hidden text-left ' +
                'transition-all transform bg-white shadow-xl rounded bg-white text-gray-800 ' +
                'flex flex-col space-y-4 pt-4'
              }
            >
              <div
                className={
                  'grow overflow-y-auto scrollbar-thin scrollbar-thumb-gray-600 ' +
                  'scrollbar-track-gray-200 p-4 flex flex-col items-center space-y-4'
                }
              >
                <img className="h-12 w-auto drag-none" src={LogoTextDark} alt="QData Logo" />
                <div className="space-y-1 text-center w-full">
                  <Dialog.Title as="h3" className="text-lg font-semibold leading-6 text-center">
                    About QData
                  </Dialog.Title>
                  <div className="text-sm">
                    Version&nbsp;<span>{appVersion}</span>&nbsp;(<span>{archInfo}</span>)
                  </div>
                  <div className="text-sm">Copyright &copy; {new Date().getFullYear()} Constantin Müller</div>
                </div>
                <div className="w-full text-sm space-y-1">
                  <div className="font-semibold">System Details:</div>
                  <div className="bg-gray-100 p-1 shadow-inner">
                    <div>Electron:&nbsp;{electronVersion}</div>
                    <div>Node:&nbsp;{nodeVersion}</div>
                    <div>V8:&nbsp;{v8Version}</div>
                    <div>OS:&nbsp;{osInfo}</div>
                  </div>
                </div>
              </div>
              <div className="flex justify-end p-4 border-t-2">
                <Button onClick={onClose} className="!bg-green-600 focus:!outline-green-100 !text-white !px-8">
                  Close
                </Button>
              </div>
            </Dialog.Panel>
          </Transition.Child>
        </div>
      </Dialog>
    </Transition>
  );
}

AboutDialog.propTypes = {
  onClose: PropTypes.func.isRequired,
  isOpen: PropTypes.bool.isRequired,
};
