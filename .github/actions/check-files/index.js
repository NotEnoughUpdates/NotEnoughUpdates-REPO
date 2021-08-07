const core = require("@actions/core");
const github = require("@actions/github");
const resolve = require('path').resolve;
const fs = require('fs')

let errors = 0;
let warnings = 0;

async function run() {
    try {
        const token = core.getInput("repo-token");
        const octokit = github.getOctokit(token);

        const check = await octokit.rest.checks.create({
            ...github.context.repo,
            head_sha: github.context.payload.pull_request.head.sha,
            status: 'in_progress',
            started_at: new Date().toISOString(),
            name: 'Parsing JSON'
        })
        let annotations1 = [];
        
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
                    let line = undefined;
                    annotations1.push({
                        title: 'Parsing JSON failed for ' + file.filename,
                        summary: err,
                        annotation_level: 'failure'
                    })
                    if(typeof num == 'number'){
                        line = getlineNumberofChar(string, num)
                    }
                    core.error("Failed to parse json for " + file.filename + "Error occured at line: " + line + ". error: " + err.message)
                    errors++;
                }
            }
        }

        octokit.rest.checks.update({
            ...github.context.repo,
            check_run_id: check.data.id,
            commit_id: github.context.payload.pull_request.head.sha,
            conclusion: (errors > 0 ? 'failure' : (warnings > 0 ? 'neutral' : 'success')),
            status: 'completed',
            output: {
                title: "Parsing JSON results",
                summary: "The reseults after parsing all of the changed JSON files.",
                annotations: annotations1
            }
        })

        for(const i in items){
            const item = items[i];
            const file = require(resolve(item))
            if(typeof file.internalname == 'undefined'){
                core.error(item + ' does not have mandetory field internalname.')
                errors++;
            } 
            if(typeof file.displayname == 'undefined'){
                core.error(item + ' does not have mandetory field displayname.')
                errors++;
            }
            if(typeof file.itemid == 'undefined'){
                core.error(item + ' does not have mandetory field itemid.')
                errors++;
            }
            const display = file.nbttag.split('display:{Lore:[')[1].split('],')[0]
            let lines = display.split(/",[0-9]+:"/g)
            lines[0] = lines[0].substring(3)
            lines[lines.length -1] = lines[lines.length -1].substring(0, lines[lines.length -1].length-1)
            same = true;
            for(const l in lines){
                if(lines[l] != file.lore[l]){
                    same = false;
                }
            }
            if(!same){
                core.warning('The lore does not match the lore in the nbt tag for file ' + item + ".")
                warnings++;
            }
            if(file.nbttag.includes("uuid:\"")){
                core.warning('The nbt tag for item ' + item + ' contains a uuid, this is not allowed.',)
                warnings++;
            }
            if(file.nbttag.includes("timestamp:\"")){
                core.warning('The nbt tag for item ' + item + ' contains a timestamp, this is not allowed.')
                warnings++;
            }
        }
        if(errors == 0 && warnings == 0){
            octokit.rest.pulls.createReview({
                ...github.context.repo,
                pull_number: github.context.payload.pull_request.number,
                commit_id: github.context.payload.pull_request.head.sha,
                event: 'APPROVE'
            })
        }else{
            octokit.rest.pulls.createReview({
                ...github.context.repo,
                pull_number: github.context.payload.pull_request.number,
                commit_id: github.context.payload.pull_request.head.sha,
                event: 'REQUEST_CHANGES',
                body: `I've detected ${errors} big problem(s) that need to be fixed and ${warnings} small problem(s) that you might want to take a look at.`
            })
        }

        console.log(check)
    } catch (err) { 
        core.setFailed(err.message);
    }
}

function getlineNumberofChar(data, index) {
    const perLine = data.split('\n');
    const total_length = 0;
    for (let i in perLine) {
        total_length += perLine[i].length;
        if (total_length >= index)
            return i + 1;
    }
}
  
run()