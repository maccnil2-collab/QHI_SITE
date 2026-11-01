import { FlatCompat } from "@eslint/eslintrc";
import js from "@eslint/js";
import { dirname } from "node:path";
import { fileURLToPath } from "node:url";

const compat = new FlatCompat({
  baseDirectory: dirname(fileURLToPath(import.meta.url)),
  recommendedConfig: js.configs.recommended,
});

const config = [
  ...compat.config({ extends: ["next/core-web-vitals", "next/typescript"] }),
  {
    ignores: [".next/**", ".next-*/**", "node_modules/**", "playwright-report/**", "test-results/**", "next-env.d.ts"],
  },
];
export default config;
