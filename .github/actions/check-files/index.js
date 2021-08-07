const core = require("@actions/core");
const github = require("@actions/github");
const resolve = require('path').resolve;
const fs = require('fs')

let failed = false;
let erroredCheck2 = false;

async function run() {
    try {
        const token = core.getInput("repo-token");
        const octokit = github.getOctokit(token);

        const check1 = await octokit.rest.checks.create({
            ...github.context.repo,
            head_sha: github.context.payload.pull_request.head.sha,
            status: 'in_progress',
            started_at: new Date().toISOString(),
            name: 'Parsing JSON'
        })
        const check2 = await octokit.rest.checks.create({
            ...github.context.repo,
            head_sha: github.context.payload.pull_request.head.sha,
            status: 'queued',
            started_at: new Date().toISOString(),
            name: 'File checks'
        })
        const annotations1 = [];
        const annotations2 = [];
        
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
                    if(typeof num == 'number'){
                        line = getlineNumberofChar(string, num)
                    }
                    failed = true;
                    annotations1.push({
                        title: 'Parsing JSON failed for ' + file.filename,
                        message: err.message,
                        annotation_level: 'failure',
                        path: file.filename,
                        start_line: line,
                        end_line: line
                    })
                }
            }
        }

        octokit.rest.checks.update({
            ...github.context.repo, 
            check_run_id: check1.data.id,
            commit_id: github.context.payload.pull_request.head.sha,
            conclusion: (annotations1.length > 0 ? 'failure' : 'success'),
            status: 'completed',
            output: {
                title: "Parsing JSON results",
                summary: "The results after parsing all of the changed JSON files.",
                annotations: annotations1
            }
        })
        octokit.rest.checks.update({
            ...github.context.repo, 
            check_run_id: check2.data.id,
            commit_id: github.context.payload.pull_request.head.sha,
            status: 'in_progress',
        })

        for(const i in items){
            const item = items[i];
            const file = require(resolve(item))
            if(typeof file.internalname == 'undefined'){
                core.error(item + ' does not have mandatory  field internalname.')
                annotations2.push({
                    title: item + ' does not have mandatory field internalname.',
                    message: 'The field internalname is required and this file doesn\'t have it.',
                    annotation_level: 'failure',
                    path: item,
                    start_line: 1,
                    end_line: 1
                })
                erroredCheck2 = true;
            } 
            if(typeof file.displayname == 'undefined'){
                annotations2.push({
                    title: item + ' does not have mandatory field displayname.',
                    message: 'The field displayname is required and this file doesn\'t have it.',
                    annotation_level: 'failure',
                    path: item,
                    start_line: 1,
                    end_line: 1
                })
                erroredCheck2 = true;
            }
            if(typeof file.itemid == 'undefined'){
                annotations2.push({
                    title: item + ' does not have mandatory field itemid.',
                    message: 'The field itemid is required and this file doesn\'t have it.',
                    annotation_level: 'failure',
                    path: item,
                    start_line: 1,
                    end_line: 1
                })
                erroredCheck2 = true;
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
                annotations2.push({
                    title: 'The lore in the nbt tag and lore of ' + item + ' is not the same.',
                    message: 'The lore of the nbt tag and the lore in the array is not the same, please fix this.',
                    annotation_level: 'warning',
                    path: item,
                    start_line: getWordLine(fs.readFileSync(item).toString(), '"nbttag"'),
                    end_line:  getWordLine(fs.readFileSync(item).toString(), '"nbttag"')
                })
            }
            if(file.nbttag.includes("uuid:\"")){
                annotations2.push({
                    title: 'The nbt tag for item ' + item + ' contains a uuid.',
                    message: 'The nbt tag for item ' + item + ' contains a uuid, this is not allowed.',
                    annotation_level: 'warning',
                    path: item,
                    start_line: getWordLine(fs.readFileSync(item).toString(), '"nbttag"'),
                    end_line:  getWordLine(fs.readFileSync(item).toString(), '"nbttag"')
                })
            }
            if(file.nbttag.includes("timestamp:\"")){
                core.warning('The nbt tag for item ' + item + ' contains a timestamp, this is not allowed.')
                annotations2.push({
                    title: 'The nbt tag for item ' + item + ' contains a timestamp',
                    message: 'The nbt tag for item ' + item + ' contains a timestamp, this is not allowed.',
                    annotation_level: 'warning',
                    path: item,
                    start_line: getWordLine(fs.readFileSync(item).toString(), '"nbttag"'),
                    end_line:  getWordLine(fs.readFileSync(item).toString(), '"nbttag"')
                })
            }
        }

        octokit.rest.checks.update({
            ...github.context.repo, 
            check_run_id: check2.data.id,
            commit_id: github.context.payload.pull_request.head.sha,
            conclusion: (erroredCheck2 ? 'failure' : (annotations2 > 0 ? 'neutral' : 'success')),
            status: 'completed',
            output: {
                title: "File checks conclusions",
                summary: "The results after checking all files for mistakes.",
                annotations: annotations2
            }
        })
        if(annotations1.length > 0 || annotations2.length > 0) {
            octokit.rest.issues.createComment({
                ...github.context.repo,
                issue_number: github.context.payload.pull_request.number,
                body: `I've detected some problems you might want to take a look at, you can see them as annotations in the files tab.`
            })
        }

        if(failed){
            core.setFailed('This action has failed, I have left some annotations in the files tab of the pull request.')
        }
    } catch (err) { 
        core.setFailed(err.message);
    }
}

function getlineNumberofChar(data, index) {
    const line = data.split('\n');
    let total_length = 0;
    for (const i in line) {
        total_length += line[i].length + 1;
        if (total_length >= index)
            return parseInt(i) + 1;
    }
}

function getWordLine(input, word){
    const line = input.split('\n');
    for (let i in line) {
        if(line[i].includes(word))
            return parseInt(i) + 1;
    }
    return 1;
}
  
run()