export function mergeConfig(defaults, overrides) {
  const result = { ...defaults };
  for (const key of Object.keys(overrides)) {
    const val = overrides[key];
    if (typeof val === "object" && typeof result[key] === "object") {
      result[key] = mergeConfig(result[key], val);
    } else {
      result[key] = val;
    }
  }
  return result;
}
