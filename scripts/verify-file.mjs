import crypto from 'crypto';
import fs from 'fs';

function canonicalJson(value) {
  if (value === null || typeof value !== 'object') return JSON.stringify(value);
  if (Array.isArray(value)) return '[' + value.map(canonicalJson).join(',') + ']';
  const keys = Object.keys(value).sort();
  return '{' + keys.map((k) => JSON.stringify(k) + ':' + canonicalJson(value[k])).join(',') + '}';
}

const m = JSON.parse(fs.readFileSync(process.argv[2], 'utf8'));
const payload = { ...m };
delete payload.signature;
const c = canonicalJson(payload);
const ok = crypto.verify(
  null,
  Buffer.from(c),
  m.publicKey,
  Buffer.from(m.signature, 'base64'),
);
console.log('file verify', ok);
