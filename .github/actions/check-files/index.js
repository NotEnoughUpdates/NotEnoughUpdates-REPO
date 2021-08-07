const core = require("@actions/core");
const github = require("@actions/github");
const resolve = require('path').resolve;
const fs = require('fs')

let problems = '';

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
            if(file.filename.endsWith('.json') && file.status != 'deleted'){
                let string = fs.readFileSync(resolve(file.filename))
                string = string.toString();
                console.log(string.split('\n'))
                try{
                    JSON.parse(string)
                    if(file.filename.startsWith('items')){
                        items.push(file.filename)
                    }
                }catch(err){
                    const num = parseInt(err.message.split(' ')[err.message.split(' ').length - 1]);
                    let line = 1;
                    if(typeof num == 'number'){

                    }
                    await comment(github, octokit, "Failed to parse json for " + file.filename + ". error: " + err.message, line, file.filename)
                }
            }
        }
        for(const i in items){
            const item = items[i];
            const file = require(resolve(item))
            if(typeof file.internalname == 'undefined'){
                await comment(github, octokit, item + ' does not have mandetory field internalname', 1, item)
            } 
            if(typeof file.displayname == 'undefined'){
                await comment(github, octokit, item + ' does not have mandetory field displayname', 1, item)
            }
            /*let nbt = file.nbttag
            console.log(nbt)
            nbt = JSON.parse(nbt)
            console.log(nbt)*/
        }
        if(problems != ''){
            core.setFailed(problems)
        }
    } catch (err) { 
        core.setFailed(err.message);
    }
}

async function comment(github, octokit, body, line, item){
    await octokit.rest.pulls.createReviewComment({
        ...github.context.repo,
        pull_number: github.context.payload.pull_request.number,
        body: body,
        line: line,
        side: 'LEFT',
        commit_id: github.context.payload.pull_request.head.sha,
        path: item
    })
    problems += body + ', '
}
  
run()