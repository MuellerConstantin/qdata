const {IPCModule} = require('@node-ipc/node-ipc');

/**
 * Host class for the worker processes.
 */
class WorkerHost {
  static _instance = undefined;

  /**
   * Constructs a new host and initializes the IPC server.
   *
   * @param {string} id The identifier of the host.
   * @param {number} retry The number of milliseconds to wait before retrying a connection.
   */
  constructor(id, retry = 1500) {
    if (WorkerHost._instance !== undefined) {
      throw new Error('WorkerHost is a singleton');
    }

    WorkerHost._instance = this;

    if (id === undefined) {
      throw new Error('WorkerHost requires an identifier');
    }

    this._ipcModule = new IPCModule();

    this._ipcModule.config.id = id;
    this._ipcModule.config.retry = retry;
    this._ipcModule.config.silent = true;

    this._hostId = id;
    this._registeredWorkers = new Map();
  }

  /**
   * Retrieves the singleton instance of the host.
   *
   * @param {string} id The identifier of the host.
   * @param {number} retry The number of milliseconds to wait before retrying a connection.
   * @return {WorkerHost} The singleton instance of the host.
   */
  static getInstance(id, retry = 1500) {
    if (WorkerHost._instance === undefined) {
      WorkerHost._instance = new WorkerHost(id, retry);
    }

    return WorkerHost._instance;
  }

  /**
   * Retrieves the identifier of the host.
   */
  get id() {
    return this._hostId;
  }

  /**
   * Starts the IPC server.
   *
   * @return {Promise<void>} A promise that resolves when the IPC server is started.
   */
  start() {
    return new Promise((resolve) => {
      this._ipcModule.serve(() => {
        this._ipcModule.server.on('start', () => {
          console.log('Worker host is listening');
          resolve();
        });

        this._ipcModule.server.on('message', (data, socket) => {
          if (data.type === 'worker_register') {
            console.log(`Worker '${data.payload}' registered`);
            this._registeredWorkers.set(data.payload, socket);
          }
        });

        this._ipcModule.server.on('socket.disconnected', (socket) => {
          for (const [id, workerSocket] of this._registeredWorkers.entries()) {
            if (workerSocket === socket) {
              console.log(`Worker '${id}' disconnected`);
              this._registeredWorkers.delete(id);
              break;
            }
          }
        });
      });

      this._ipcModule.server.start();
    });
  }

  /**
   * Allows the host to receive messages from a (specific) worker.
   *
   * @param {string} type The type of message to receive.
   * @param {function(any, any): void} callback The callback to execute when a message is received.
   * @param {string} worker Identifier of a specific worker if should only receive messages from that worker.
   */
  on(type, callback, worker) {
    this._ipcModule.server.on('message', (data) => {
      if (data.type === type && (worker === undefined || worker === data.from)) {
        callback(data.payload, data.from);
      }
    });
  }

  /**
   * Await a message from a (specific) worker.
   *
   * @param {string} type The type of message to receive.
   * @param {string} worker Identifier of a specific worker if should only await messages from that worker.
   * @return {Promise<{payload: any, from: any}>} A promise that resolves when a message is received.
   */
  join(type, worker) {
    return new Promise((resolve) => {
      this.on(
        type,
        (payload, from) => {
          resolve({payload, from});
        },
        worker,
      );
    });
  }

  /**
   * Broadcasts a message to all workers.
   *
   * @param {string} type The type of message to broadcast.
   * @param {any} payload The payload of the message.
   */
  broadcast(type, payload) {
    this._ipcModule.server.broadcast('message', {from: this._hostId, type, payload});
  }

  /**
   * Sends a message to a specific worker.
   *
   * @param {any} worker The identifier of the worker to send the message to.
   * @param {string} type The type of message to send.
   * @param {any} payload The payload of the message.
   */
  emit(worker, type, payload) {
    const socket = this._registeredWorkers.get(worker);
    this._ipcModule.server.emit(socket, 'message', {from: this._hostId, type, payload});
  }
}

/**
 * Manages the instances of all instantiated client workers.
 */
class WorkerClientManager {
  static _instance = undefined;

  /**
   * Constructs a new manager.
   */
  constructor() {
    if (WorkerClientManager._instance !== undefined) {
      throw new Error('WorkerClientManager is a singleton');
    }

    WorkerClientManager._instance = this;

    this._workers = new Map();
  }

  /**
   * Retrieves the singleton instance of the manager.
   *
   * @return {WorkerClientManager} The singleton instance of the manager.
   * @throws {Error} If the manager has not been initialized.
   */
  static getInstance() {
    if (WorkerClientManager._instance === undefined) {
      WorkerClientManager._instance = new WorkerClientManager();
    }

    return WorkerClientManager._instance;
  }

  /**
   * Retrieves a worker by its identifier.
   *
   * @param {string} id The identifier of the worker.
   * @return {WorkerClient|undefined} The worker with the given identifier.
   */
  getWorker(id) {
    return this._workers.get(id);
  }

  /**
   * Adds a worker client to the manager.
   *
   * @param {WorkerClient} worker The worker client to add.
   */
  addWorker(worker) {
    this._workers.set(worker.id, worker);
  }

  /**
   * Removes a worker client from the manager.
   *
   * @param {string} id The identifier of the worker client to remove.
   */
  removeWorker(id) {
    this._workers.delete(id);
  }
}

/**
 * Client class for the worker processes.
 */
class WorkerClient {
  /**
   * Constructs a new client and initializes the IPC server.
   *
   * @param {string} id Identifier of the client.
   */
  constructor(id) {
    if (id === undefined) {
      throw new Error('WorkerClient requires an identifier');
    }

    this._hostId = null;
    this._clientId = id;
    this._ipcModule = new IPCModule();

    this._ipcModule.config.id = id;

    WorkerClientManager.getInstance().addWorker(this);
  }

  /**
   * Connects to the IPC server.
   *
   * @param {string} hostId Identifier of the host to connect to.
   * @param {number} retry The number of milliseconds to wait before retrying a connection.
   * @return {Promise<void>} A promise that resolves when the connection is established.
   */
  connect(hostId, retry = 1500) {
    this._ipcModule.config.retry = retry;
    this._ipcModule.config.silent = true;

    this._hostId = hostId;

    return new Promise((resolve) => {
      this._ipcModule.connectTo(hostId, () => {
        this._ipcModule.of[hostId].on('connect', () => {
          console.log(`Worker connected to host '${hostId}'`);
          this.emit('worker_register', this._clientId);
          resolve();
        });

        this._ipcModule.of[hostId].on('disconnect', () => {
          console.log(`Worker disconnected from host '${hostId}'`);
        });
      });
    });
  }

  /**
   * Retrieves the identifier of the client.
   */
  get id() {
    return this._clientId;
  }

  /**
   * Allows the client to receive messages from the host.
   *
   * @param {string} type The type of message to receive.
   * @param {function(any): void} callback The callback to execute when a message is received.
   */
  on(type, callback) {
    this._ipcModule.of[this._hostId].on('message', (data) => {
      if (data.type === type) {
        callback(data.payload, data.from);
      }
    });
  }

  /**
   * Await a message from the host.
   *
   * @param {string} type The type of message to receive.
   * @return {Promise<{payload: any, from: any}>} A promise that resolves when a message is received.
   */
  join(type) {
    return new Promise((resolve) => {
      this.on(type, (payload, from) => {
        resolve({payload, from});
      });
    });
  }

  /**
   * Sends a message to the host.
   *
   * @param {string} type The type of message to send.
   * @param {any} payload The payload of the message.
   */
  emit(type, payload) {
    this._ipcModule.of[this._hostId].emit('message', {from: this._clientId, type, payload});
  }
}

module.exports = {WorkerHost, WorkerClient, WorkerClientManager};
