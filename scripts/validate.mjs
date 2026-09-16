import fs from 'node:fs';
import {validateDataset} from '../site/engine.js';
const data=validateDataset(JSON.parse(fs.readFileSync(new URL('../site/data/jobs.json',import.meta.url),'utf8')));
console.log(`Validated ${data.jobs.length} public jobs.`);
