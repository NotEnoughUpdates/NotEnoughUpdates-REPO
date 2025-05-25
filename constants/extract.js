const fs = require('fs');
const path = require('path');

// Open JSON file
const animatedSkullsJson = fs.readFileSync(path.join(__dirname, 'animatedSkulls.json'), 'utf8');

const REGEX = ".*(?<skin>PET_SKIN_BLACK_CAT_CATGIRL_[^\"]).*"

// Look for instance of the regex in the JSON file
const regex = new RegExp(REGEX, 'g');
const matches = animatedSkullsJson.match(regex);

if (matches) {
    // Loop through each match
    matches.forEach((match) => {
        // Extract the skin name from the match
        const skinName = match.match(/(?<skin>PET_SKIN_BLACK_CAT_CATGIRL_[^"]*)/).groups.skin;
        console.log(skinName);
    });
}