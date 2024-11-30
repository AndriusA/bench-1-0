const execa = require('execa')

async function waitForThrottled(commands, condition, timeoutSeconds = 15 * 60) {
  for (let i = 0; i < timeoutSeconds; ++i) {
    result = await commands.js.run(`return (${condition})`)
    if (result != null && result != '')
      return result
    await commands.wait.byTime(1000)
  }
  return false
}

function getBrowserAttr(context) {
  const options = context.options
  binaryPath = null
  args = null
  if (options.safari?.binaryPath) {
    binaryPath = options.safari.binaryPath
    args = options.safari.args
  } else if  (options.firefox?.binaryPath) {
    binaryPath = options.firefox.binaryPath
    args = options.firefox.args
  } else if(options.edge?.binaryPath) {
    binaryPath = options.edge.binaryPath
    args = options.chrome.args
  } else if(options.chrome?.binaryPath) {
    binaryPath = options.chrome.binaryPath
    args = options.chrome.args
  } else {
    console.log(options)
    throw new Error('Browser is not supported ' + options.browser)
  }

  return {
    type: options.browser,
    binaryPath: binaryPath,
    args: args,
  }
}

async function getMemoryMetrics(context) {
  const attr = getBrowserAttr(context)
  // TODO: change python3
  let cmd = `python3 get_memory_metrics.py ${attr.type}`
  if (attr.args != null && attr.args[0].startsWith('user-data'))
    cmd += ` "${attr.args[0]}"`
  console.log(cmd)
  const { stdout } = await execa.command(cmd, { shell: true });
  console.log(stdout)
  return JSON.parse(stdout)
}

module.exports = {
  waitForThrottled: waitForThrottled,
  getMemoryMetrics: getMemoryMetrics,
};
