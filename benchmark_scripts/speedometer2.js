const utils = require('./utils.js')

async function perfTest(context, commands) {
  const URL = 'https://www.browserbench.org/Speedometer2.1'
  const getResults = 'document.getElementById("result-number")?.textContent';

  // One warm up iteration:
  await commands.navigate(`${URL}?iterationCount=1`);
  await commands.js.run('startTest()');
  await utils.waitForThrottled(commands, getResults);

  await commands.measure.start(`${URL}?iterationCount=100'`);
  await commands.js.run('startTest()');

  const value = await utils.waitForThrottled(commands, getResults);
  const error = await commands.js.run(
    'return document.getElementById("confidence-number").textContent.substr(2)')
  console.log('got result = ', value, 'std =', error)
  commands.measure.addObject(
    {
      'speedometer2.1': parseFloat(value),
      'speedometer2.1_error': parseFloat(error)
    });
  await commands.screenshot.take('result')
};

module.exports = {
  test: perfTest
};
