
const utils = require('./utils.js')
const fs = require('fs');
const URLS = fs.readFileSync('./scenarios/new-list.txt').toString().split("\n");

async function perfTest(context, commands) {
  for (url of URLS) {
    if (url == '') break;
    if (url.startsWith('#') || url.startsWith('/'))
      continue;

    await commands.js.run(`window.open('${url}', '_blank')`);
    await commands.wait.byTime(15 * 1000)
  }

  const memory_metrics = await utils.getMemoryMetrics(context)

  await commands.wait.byTime(45 * 1000)
  await commands.measure.start('memory');
  await commands.measure.stop();
  commands.measure.addObject(memory_metrics)
};

module.exports = {
  test: perfTest
};
