const {ipcRenderer, contextBridge} = require('electron');

contextBridge.exposeInMainWorld('electron', {
  ipcMain: {
    send: (channel, args) => ipcRenderer.send(channel, args),
    on: (channel, func) => ipcRenderer.on(channel, (event, args) => func(args)),
    invoke: (channel, args) => ipcRenderer.invoke(channel, args),
  },
});
