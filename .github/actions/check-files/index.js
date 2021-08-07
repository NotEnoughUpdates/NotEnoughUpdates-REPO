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
                try{
                    JSON.parse(string)
                    if(file.filename.startsWith('items')){
                        items.push(file.filename)
                    }
                }catch(err){
                    const num = parseInt(err.message.split(' ')[err.message.split(' ').length - 1]);
                    let line = 1;
                    if(typeof num == 'number'){
                        line = getlineNumberofChar(string, num)
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
            const nbt = file.nbttag;
            const display = nbt.split('display:{Lore:[')[1].split('],')[0]
            console.log(display)
            const lines = display.split(/(",)?[0-9]+:"/g)
            console.log(lines)
            lines[lines.length -1] = lines[lines.length -1].substring(0, lines[lines.length -1].length-1)
            console.log(lines)
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

function getlineNumberofChar(data, index) {
    var perLine = data.split('\n');
    var total_length = 0;
    for (i = 0; i < perLine.length; i++) {
        total_length += perLine[i].length;
        if (total_length >= index)
            return i + 1;
    }
}
  
run()