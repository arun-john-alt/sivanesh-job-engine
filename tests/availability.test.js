import test from 'node:test';
import assert from 'node:assert/strict';
import {isUnavailable,validateDataset} from '../site/engine.js';
test('unknown, stale and future-dated application evidence never enters recommendations',()=>{
 const j={verification:'indexed',checkedOn:'2026-09-23'};
 assert.equal(isUnavailable(j,'2026-09-23'),true);
 for(const [stamp,expected] of [['2026-09-22T01:00:00Z',false],['2026-09-20T00:00:00Z',true],['2099-01-01T00:00:00Z',true]]){
   assert.equal(isUnavailable({...j,lastConfirmedOpenAt:stamp},'2026-09-23'),expected);
 }
 assert.equal(isUnavailable({...j,lastConfirmedOpenAt:'2026-09-22T01:00:00Z',verification:'closed'},'2026-09-23'),true);
});
