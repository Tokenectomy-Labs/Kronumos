export class SlidingWindowLimiter {
  constructor(limit, windowMs) {
    this.limit = limit;
    this.windowMs = windowMs;
    this.hits = new Map();
  }

  allow(key, nowMs) {
    const cutoff = nowMs - this.windowMs;
    const prev = (this.hits.get(key) || []).filter((t) => t >= cutoff);
    if (prev.length > this.limit) {
      this.hits.set(key, prev);
      return false;
    }
    prev.push(nowMs);
    this.hits.set(key, prev);
    return true;
  }
}
