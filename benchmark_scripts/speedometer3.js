const utils = require('./utils.js')

async function perfTest(context, commands) {
  const URL = 'https://www.browserbench.org/Speedometer3.0?startAutomatically=true'
  const getResults = 'document.getElementById("result-number")?.textContent';

  // One warm up iteration:
  await commands.navigate(`${URL}&iterationCount=1`);
  await utils.waitForThrottled(commands, getResults, 3 * 60);

  await commands.measure.start(`${URL}&iterationCount=10`);

  const value = await utils.waitForThrottled(commands, getResults, 10 * 60);
  const error = await commands.js.run(
    'return document.getElementById("confidence-number").textContent.substr(2)')

  console.log('got result = ', value, 'error =', error)
  commands.measure.addObject(
    {
      'speedometer3_avg': parseFloat(value),
      'speedometer3_error': parseFloat(error)
    });
  const raw = await commands.js.run('return JSON.parse(window.benchmarkClient._formattedJSONResult({ modern: true })).Score.values')
  commands.measure.addObject(
    {
      'speedometer3': raw,
    });

  await commands.screenshot.take('result')
};

module.exports = {
  test: perfTest
};
