const utils = require('./utils.js')

async function perfTest(context, commands) {
  await commands.measure.start(
    'https://browserbench.org/MotionMark1.3');

  await commands.wait.byXpath('//button[text()="Run Benchmark"]', 2 * 60 * 1000)
  await commands.click.byIdAndWait('start-button');

  const score = await utils.waitForThrottled(commands,
    'document.querySelector(".score")?.textContent', 10 * 60)

  const error = await commands.js.run(
    "return document.querySelector('.confidence').textContent.slice(1, -1)")

  console.log('got result =', score, 'std =', error)

  commands.measure.addObject(
    {
      'motionmark': parseFloat(score.split(' @')[0]),
      'motionmark_error': parseFloat(error)
    });

  await commands.screenshot.take('result')
};

module.exports = {
  test: perfTest
};
