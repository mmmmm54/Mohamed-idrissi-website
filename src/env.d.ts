/// <reference types="astro/client" />

/*
  Minimal ambient types for the Node built-ins used at build time.
  Declared locally so the project keeps its three dependencies and does not
  need @types/node. Extend only if a new built-in is genuinely needed.
*/
declare module 'node:fs' {
  export function existsSync(target: string): boolean;
  export function readdirSync(target: string): string[];
  const fs: {
    existsSync: typeof existsSync;
    readdirSync: typeof readdirSync;
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
