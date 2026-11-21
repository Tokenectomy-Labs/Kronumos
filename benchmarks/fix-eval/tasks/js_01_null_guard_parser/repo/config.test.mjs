import test from "node:test";
import assert from "node:assert/strict";
import { mergeConfig } from "./config.mjs";

test("handles null overrides cleanly", () => {
  const res = mergeConfig({ retries: 3, tls: { enabled: true } }, null);
  assert.deepEqual(res, { retries: 3, tls: { enabled: true } });
});

test("handles null nested section without throwing", () => {
  const res = mergeConfig({ tls: { enabled: true } }, { tls: null });
  assert.equal(res.tls, null);
});

test("deep merges valid nested objects", () => {
  const res = mergeConfig(
    { tls: { enabled: true, minVersion: "1.2" } },
    { tls: { minVersion: "1.3" } }
  );
  assert.deepEqual(res, { tls: { enabled: true, minVersion: "1.3" } });
});
