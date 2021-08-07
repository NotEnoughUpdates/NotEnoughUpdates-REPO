const core = require("@actions/core");
const github = require("@actions/github");
const resolve = require('path').resolve;
const fs = require('fs');

async function run() {
    try {
        const token = core.getInput("repo-token");
        const octokit = github.getOctokit(token);
        
        const changed = await octokit.rest.pulls.listFiles({
            ...github.context.repo,
            pull_number: github.context.payload.pull_request.number,
        })
        console.log(changed)

        const items = fs.readdirSync(resolve('./items/'));
        for(const i in items){
            const item = items[i];
            const file = require(resolve('./items/' + item))
            if(typeof file.internalname == 'undefined'){
                octokit.rest.pulls.createReviewComment({
                    ...github.context.repo,
                    pull_number: github.context.payload.pull_request.number,
                    body: item + " Does not have mandetory field internalname",
                    path: './items/' + item,
                    line: 1
                })
                /*await octokit.rest.issues.createComment({
                    ...github.context.repo,
                    issue_number: github.context.payload.pull_request.number,
                    body: item + " Does not have mandetory field internalname"
                  });*/
                core.setFailed(item + " Does not have mandetory field internalname");
            } else if(typeof file.displayname == 'undefined'){
                core.setFailed(item + " Does not have mandetory field displayname");
            }
        }
    } catch (err) { 
        core.setFailed(err.message);
    }
}
  
run()
  