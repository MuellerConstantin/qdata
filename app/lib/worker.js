const ipc = require('@node-ipc/node-ipc').default;

/**
 * Host class for the worker processes.
 */
class WorkerHost {
  static _instance = null;

  /**
   * Constructs a new host and initializes the IPC server.
   *
   * @param {string} id The identifier of the host.
   * @param {number} retry The number of milliseconds to wait before retrying a connection.
   */
  constructor(id, retry = 1500) {
    if (WorkerHost._instance !== null) {
      throw new Error('WorkerHost is a singleton');
    }

    WorkerHost._instance = this;

    ipc.config.id = id;
    ipc.config.retry = retry;
    ipc.config.silent = true;

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
    if (WorkerHost._instance === null) {
      WorkerHost._instance = new WorkerHost(id, retry);
    }

    return WorkerHost._instance;
  }

  /**
   * Starts the IPC server.
   *
   * @return {Promise<void>} A promise that resolves when the IPC server is started.
   */
  start() {
    return new Promise((resolve) => {
      ipc.serve(() => {
        ipc.server.on('start', () => {
          console.log('Worker host is listening');
          resolve();
        });

        ipc.server.on('message', (data, socket) => {
          if (data.type === 'worker_register') {
            console.log(`Worker '${data.payload}' registered`);
            this._registeredWorkers.set(data.payload, socket);
          }
        });

        ipc.server.on('socket.disconnected', (socket) => {
          for (const [id, workerSocket] of this._registeredWorkers.entries()) {
            if (workerSocket === socket) {
              console.log(`Worker '${id}' disconnected`);
              this._registeredWorkers.delete(id);
              break;
            }
          }
        });
      });

      ipc.server.start();
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
    ipc.server.on('message', (data) => {
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
    ipc.server.broadcast('message', {from: this._hostId, type, payload});
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
    ipc.server.emit(socket, 'message', {from: this._hostId, type, payload});
  }
}

/**
 * Client class for the worker processes.
 */
class WorkerClient {
  /**
   * Constructs a new client and initializes the IPC server.
   */
  constructor() {
    this._hostId = null;
  }

  /**
   * Connects to the IPC server.
   *
   * @param {string} clientId Identifier of the client to connect as.
   * @param {string} hostId Identifier of the host to connect to.
   * @param {number} retry The number of milliseconds to wait before retrying a connection.
   * @return {Promise<void>} A promise that resolves when the connection is established.
   */
  connect(clientId, hostId, retry = 1500) {
    ipc.config.id = clientId;
    ipc.config.retry = retry;
    ipc.config.silent = true;

    this._hostId = hostId;
    this._clientId = clientId;

    return new Promise((resolve) => {
      ipc.connectTo(hostId, () => {
        ipc.of[hostId].on('connect', () => {
          console.log(`Worker connected to host '${hostId}'`);
          this.emit('worker_register', clientId);
          resolve();
        });

        ipc.of[hostId].on('disconnect', () => {
          console.log(`Worker disconnected from host '${hostId}'`);
        });
      });
    });
  }

  /**
   * Allows the client to receive messages from the host.
   *
   * @param {string} type The type of message to receive.
   * @param {function(any): void} callback The callback to execute when a message is received.
   */
  on(type, callback) {
    ipc.of[this._hostId].on('message', (data) => {
      if (data.type === type) {
        callback(data.payload, data.from);
      }
    });
  }

  /**
   * Sends a message to the host.
   *
   * @param {string} type The type of message to send.
   * @param {any} payload The payload of the message.
   */
  emit(type, payload) {
    ipc.of[this._hostId].emit('message', {from: this._clientId, type, payload});
  }
}

module.exports = {WorkerHost, WorkerClient};
