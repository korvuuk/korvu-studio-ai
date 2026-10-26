// Mini runtime para VER os artboards .dc.html do Claude Design (sc-for, sc-if, {{ }}). Só para a designer olhar.
(function () {
  class DCLogic { constructor(p) { this.props = p || {}; this.state = {}; } setState(s) { Object.assign(this.state, s); render(); } }
  const src = document.querySelector('script[type="text/x-dc"]').textContent;
  const Comp = new Function('DCLogic', src + '\n;return Component;')(DCLogic);
  const comp = new Comp({});
  const host = document.querySelector('x-dc');
  const helmet = host.querySelector('helmet');
  if (helmet) { [...helmet.children].forEach((c) => document.head.appendChild(c)); helmet.remove(); }
  const tpl = host.innerHTML;
  function get(scope, path) {
    path = path.trim();
    let v = scope;
    for (const k of path.split('.')) { if (v == null) return undefined; v = v[k]; }
    return v;
  }
  function interp(s, scope) {
    const m = s.match(/^\s*\{\{([^}]+)\}\}\s*$/);
    if (m) return get(scope, m[1]);
    return s.replace(/\{\{([^}]+)\}\}/g, (_, p) => { const v = get(scope, p); return v == null ? '' : String(v); });
  }
  function proc(node, scope) {
    if (node.nodeType === 3) { if (node.nodeValue.includes('{{')) node.nodeValue = interp(node.nodeValue, scope) ?? ''; return; }
    if (node.nodeType !== 1) return;
    const tag = node.tagName;
    if (tag === 'SC-FOR') {
      const list = interp(node.getAttribute('list'), scope) || [];
      const as = node.getAttribute('as');
      const frag = document.createDocumentFragment();
      list.forEach((it) => {
        const wrap = document.createElement('div'); wrap.innerHTML = node.innerHTML;
        const sc = Object.assign(Object.create(scope), { [as]: it });
        [...wrap.childNodes].forEach((c) => { proc(c, sc); });
        [...wrap.childNodes].forEach((c) => frag.appendChild(c));
      });
      node.replaceWith(frag); return;
    }
    if (tag === 'SC-IF') {
      const v = interp(node.getAttribute('value'), scope);
      if (!v) { node.remove(); return; }
      const kids = [...node.childNodes]; kids.forEach((c) => proc(c, scope));
      node.replaceWith(...[...node.childNodes]); return;
    }
    for (const a of [...node.attributes]) {
      if (!a.value.includes('{{')) continue;
      const v = interp(a.value, scope);
      if (/^on/i.test(a.name)) { node.removeAttribute(a.name); if (typeof v === 'function') node.addEventListener(a.name.slice(2).toLowerCase(), v); }
      else if (v === false || v == null) node.removeAttribute(a.name);
      else if (v === true) node.setAttribute(a.name, a.name === 'disabled' ? '' : 'true');
      else node.setAttribute(a.name, String(v));
    }
    [...node.childNodes].forEach((c) => proc(c, scope));
  }
  function render() {
    const vals = comp.renderVals();
    host.innerHTML = tpl;
    [...host.childNodes].forEach((c) => proc(c, vals));
  }
  render();
})();
