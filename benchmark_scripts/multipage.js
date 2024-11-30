
const fs = require('fs');
const URLS = fs.readFileSync('./scenarios/new-set.txt').toString().split("\n");

async function perfTest(context, commands) {
  for (url of URLS) {
    if (url.startsWith('#') || url.startsWith('/'))
      continue;
    if (url == '') break;
    await commands.measure.start(url);
  }
};

module.exports = {
  test: perfTest
};
