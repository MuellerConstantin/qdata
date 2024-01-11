const {QvdFile} = require('qvd4js');
const ESSerializer = require('esserializer');
const {WorkerClient} = require('../lib/worker');

(async () => {
  const clientId = process.argv[2];
  const filePath = process.argv[3];

  const worker = new WorkerClient();
  await worker.connect(clientId, 'HOST');

  console.log(`Loading file '${filePath}' in worker '${clientId}'`);

  try {
    const file = await QvdFile.load(filePath);
    const payload = ESSerializer.serialize(file);
    worker.emit('done', payload);
  } catch (err) {
    console.error(`Error loading file '${filePath}' in worker '${clientId}'`);
    worker.emit('error', err);
  }
})();