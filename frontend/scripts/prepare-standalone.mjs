import { cpSync, existsSync, mkdirSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const root = join(dirname(fileURLToPath(import.meta.url)), "..");
const copies = [
  [join(root, "public"), join(root, ".next", "standalone", "public")],
  [join(root, ".next", "static"), join(root, ".next", "standalone", ".next", "static")],
];

for (const [source, destination] of copies) {
  if (!existsSync(source)) continue;
  mkdirSync(dirname(destination), { recursive: true });
  cpSync(source, destination, { recursive: true, force: true });
}
