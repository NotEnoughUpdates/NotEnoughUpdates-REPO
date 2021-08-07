const core = require("@actions/core");
const github = require("@actions/github");
const resolve = require('path').resolve;
const fs = require('fs');

async function run() {
    try {
        const token = core.getInput("repo-token");
        const octokit = github.getOctokit(token);
        
        console.log(resolve('../../../items/'))
        console.log(fs.readdirSync(resolve('../../../items/')));
    } catch (err) {
        core.setFailed(err.message);
    }
}
  
  run()
  