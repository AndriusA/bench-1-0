async function perfTest(context, commands) {
  await commands.measure.start('https://web.basemark.com/');
  await commands.click.byClassNameAndWait('btn');

  while (true) {
    await commands.wait.byTime(3000)
    value = await commands.js.run(
      "return document.getElementsByClassName('overall-score')[1]?.textContent")
    if (value && value != '') {
      console.log('got result', value)
      commands.measure.addObject({ 'basemark': parseFloat(value) });
      break;
    }
  }
  await commands.screenshot.take('result')
};

module.exports = {
  test: perfTest
};
