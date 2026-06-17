import crypto from 'crypto';
import fs from 'fs';
import { execSync } from 'child_process';
import os from 'os';
import path from 'path';

const repo = 'c:/Users/harshal.raut/OneDrive - Xoriant/Desktop/Sample Test';
const raw = execSync(`git -C "${repo}" notes --ref=provenance show HEAD`, { encoding: 'utf8' });
const m = JSON.parse(raw);
const payload = { ...m };
delete payload.signature;

function canonicalJson(value) {
  if (value === undefined) return 'null';
  if (value === null || typeof value !== 'object') return JSON.stringify(value);
  if (Array.isArray(value)) return '[' + value.map(canonicalJson).join(',') + ']';
  const keys = Object.keys(value).filter((k) => value[k] !== undefined).sort();
  return '{' + keys.map((k) => JSON.stringify(k) + ':' + canonicalJson(value[k])).join(',') + '}';
}

const c = canonicalJson(payload);
const priv = fs.readFileSync(path.join(os.homedir(), '.provenance', 'keys', 'private.pem'), 'utf8');
const recomputed = crypto.sign(null, Buffer.from(c), priv).toString('base64');
console.log('stored sig matches resign:', m.signature === recomputed);
const ok = crypto.verify(null, Buffer.from(c), m.publicKey, Buffer.from(m.signature, 'base64'));
console.log('verify with pub:', ok);
