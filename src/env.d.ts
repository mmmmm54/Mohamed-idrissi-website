/// <reference types="astro/client" />

/*
  Minimal ambient types for the Node built-ins used at build time.
  Declared locally so the project keeps its three dependencies and does not
  need @types/node. Extend only if a new built-in is genuinely needed.
*/
declare module 'node:fs' {
  /* Only the byte readers used to find an image's width and height. */
  interface FileBytes extends Uint8Array {
    toString(encoding: 'ascii', start: number, end: number): string;
    readUInt16BE(offset: number): number;
    readUInt16LE(offset: number): number;
    readUInt32BE(offset: number): number;
    readUInt32LE(offset: number): number;
    readUIntLE(offset: number, byteLength: number): number;
  }
  export function existsSync(target: string): boolean;
  export function readdirSync(target: string): string[];
  export function readFileSync(target: string): FileBytes;
  const fs: {
    existsSync: typeof existsSync;
    readdirSync: typeof readdirSync;
    readFileSync: typeof readFileSync;
  };
  export default fs;
}

declare module 'node:path' {
  export function join(...parts: string[]): string;
  const path: {
    join: typeof join;
  };
  export default path;
}

declare const process: {
  cwd(): string;
};
