const core = require("@actions/core");
const github = require("@actions/github");
const resolve = require('path').resolve;
const fs = require('fs');

async function run() {
    try {
        const token = core.getInput("repo-token");
        const octokit = github.getOctokit(token);
        
        //console.log(resolve('./items/'))
        const items = fs.readdirSync(resolve('./items/'));
        for(const i in items){
            const item = items[i];
            console.log(item)
            const file = require(resolve('./items/' + item))
            if(typeof file.internalname == 'undefined'){
                core.setFailed(file + " Does not have mandetory field internalname");
            } else if(typeof file.displayname == 'undefined'){
                core.setFailed(file + " Does not have mandetory field displayname");
            }
        }
    } catch (err) { 
        core.setFailed(err.message);
    }
}
  
run()
  