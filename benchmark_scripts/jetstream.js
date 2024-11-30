const utils = require('./utils.js')

async function perfTest(context, commands) {
  await commands.measure.start(
    'https://browserbench.org/JetStream2.2/');

  await commands.wait.byXpath('//a[text()="Start Test"]', 2 * 60 * 1000)
  await commands.js.run('JetStream.start()');

  const score = await utils.waitForThrottled(commands,
    'document.getElementById("result-summary")?.childNodes[0]?.textContent',
    10 * 60)

  console.log('got result =', score)
  commands.measure.addObject({ 'jetstream': parseFloat(score) });
  await commands.screenshot.take('result')
};

module.exports = {
  test: perfTest
};
