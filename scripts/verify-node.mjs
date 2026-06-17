import crypto from 'crypto';
import { execSync } from 'child_process';

const repo = 'c:/Users/harshal.raut/OneDrive - Xoriant/Desktop/Sample Test';
const raw = execSync(`git -C "${repo}" notes --ref=provenance show HEAD`, { encoding: 'utf8' });
const m = JSON.parse(raw);
const payload = { ...m };
delete payload.signature;

function canonicalJson(value) {
  if (value === null || typeof value !== 'object') return JSON.stringify(value);
  if (Array.isArray(value)) return '[' + value.map(canonicalJson).join(',') + ']';
  const keys = Object.keys(value).sort();
  return '{' + keys.map((k) => JSON.stringify(k) + ':' + canonicalJson(value[k])).join(',') + '}';
}

for (const [name, c] of [
  ['canonical', canonicalJson(payload)],
  ['stringify', JSON.stringify(payload)],
]) {
  const ok = crypto.verify(null, Buffer.from(c), m.publicKey, Buffer.from(m.signature, 'base64'));
  console.log(name, ok);
}
