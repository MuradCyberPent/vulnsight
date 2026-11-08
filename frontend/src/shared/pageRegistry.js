// Finds every page in src/modules/*/pages/*.jsx.
// A page file exports:  route = { path, public?, admin?, priority? }   and optionally   nav = { label, order, end?, adminOnly? }
// If two pages use the same path, the one with the higher priority wins (a later module can replace an earlier page).
const files = import.meta.glob("../modules/*/pages/*.jsx", { eager: true });

const byPath = new Map();
for (const mod of Object.values(files)) {
  if (!mod.route || !mod.default) continue;
  const page = { ...mod.route, nav: mod.nav, Component: mod.default };
  const current = byPath.get(page.path);
  if (!current || (page.priority ?? 0) > (current.priority ?? 0)) byPath.set(page.path, page);
}

export const pages = [...byPath.values()];

export const navItems = pages
  .filter((p) => p.nav)
  .map((p) => ({ to: p.path, ...p.nav }))
  .sort((a, b) => a.order - b.order);
