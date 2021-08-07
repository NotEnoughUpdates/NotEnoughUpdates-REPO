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
        const items = []
        for(const i in changed.data){
            const file = changed.data[i];
            if(file.filename.startsWith('items') && file.status != 'deleted'){
                items.push(file.filename)
            }
        }
        //console.log(github.context.payload.pull_request)
        for(const i in items){
            const item = items[i];
            const file = require(resolve(item))
            if(typeof file.internalname == 'undefined'){
                console.log(github.context.payload.pull_request.head.sha)// 7419cf5b2b4e44bfc368bc755f6d7575346aff91
                console.log(github.context.payload.pull_request.base.sha)// b1f7c45cd1b0584e52ec3c6454cf0e82ceff156e
                await octokit.rest.pulls.createReviewComment({
                    ...github.context.repo,
                    pull_number: github.context.payload.pull_request.number,
                    body: item + " Does not have mandetory field internalname",
                    line: 2,
                    side: 'LEFT',
                    commit_id: github.context.payload.pull_request.head.sha,
                    path: item
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
  