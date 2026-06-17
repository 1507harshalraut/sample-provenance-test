import crypto from 'crypto';
import { execSync } from 'child_process';
import fs from 'fs';

const repo = 'c:/Users/harshal.raut/OneDrive - Xoriant/Desktop/Sample Test';
const raw = execSync(`git -C "${repo}" notes --ref=provenance show HEAD`, { encoding: 'utf8' });
const m = JSON.parse(raw);
const p = { ...m };
delete p.signature;

function canonicalJson(value) {
  if (value === undefined) return 'null';
  if (value === null || typeof value !== 'object') return JSON.stringify(value);
  if (Array.isArray(value)) return '[' + value.map(canonicalJson).join(',') + ']';
  const keys = Object.keys(value).filter((k) => value[k] !== undefined).sort();
  return '{' + keys.map((k) => JSON.stringify(k) + ':' + canonicalJson(value[k])).join(',') + '}';
}

const c = canonicalJson(p);
fs.writeFileSync('canonical-js.txt', c, 'utf8');
console.log('js len', c.length);
console.log('js hash', crypto.createHash('sha256').update(c).digest('hex').slice(0, 16));
