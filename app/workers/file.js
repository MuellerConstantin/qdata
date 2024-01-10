const {QvdFile} = require('qvd4js');
const {WorkerClient} = require('../lib/worker');

(async () => {
  const clientId = process.argv[2];
  const filePath = process.argv[3];

  const worker = new WorkerClient();
  await worker.connect(clientId, 'HOST');

  console.log(`Loading file '${filePath}' in worker '${clientId}'`);

  try {
    const file = await QvdFile.load(filePath);
    worker.emit('done', file);
  } catch (err) {
    console.error(`Error loading file '${filePath}' in worker '${clientId}'`);
    worker.emit('error', err);
  }
})();
