import test from "node:test";
import assert from "node:assert/strict";
import { SlidingWindowLimiter } from "./limiter.mjs";

test("enforces exact request limit within window", () => {
  const lim = new SlidingWindowLimiter(2, 1000);
  assert.equal(lim.allow("u1", 100), true);
  assert.equal(lim.allow("u1", 200), true);
  assert.equal(lim.allow("u1", 300), false);
});

test("expires requests strictly outside the window", () => {
  const lim = new SlidingWindowLimiter(1, 1000);
  assert.equal(lim.allow("u1", 1000), true);
  assert.equal(lim.allow("u1", 1999), false);
  assert.equal(lim.allow("u1", 2000), true);
});
