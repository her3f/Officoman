const { test } = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const source = fs.readFileSync(path.join(__dirname, 'site/site.js'), 'utf8');

function element(attrs = {}) {
  return {
    attrs, events: {}, hidden: false,
    addEventListener(event, callback) { this.events[event] = callback; },
    setAttribute(key, value) { this.attrs[key] = value; },
    getAttribute(key) { return this.attrs[key]; },
    focus() { this.focused = true; },
    classList: { toggle() {} },
  };
}

function setup(lang) {
  const tabs = ['nib', 'tally', 'podium', 'sheaf'].map(id => element({ 'aria-controls': id }));
  const panels = Object.fromEntries(['nib', 'tally', 'podium', 'sheaf'].map(id => [id, element()]));
  const buttons = ['all', 'windows', 'macos', 'linux'].map(os => Object.assign(element(), { dataset: { os } }));
  const cells = ['windows', 'macos', 'linux'].map(platform => Object.assign(element(), { dataset: { platform } }));
  const filters = Object.assign(element(), { querySelectorAll: () => buttons });
  const status = element();
  const document = {
    documentElement: { lang, dir: lang === 'ar' ? 'rtl' : 'ltr' },
    querySelector: selector => ({ '.platform-filter': filters, '.downloads': element() }[selector] || null),
    querySelectorAll: selector => selector === '[role="tab"]' ? tabs : cells,
    getElementById: id => id === 'download-status' ? status : panels[id],
  };
  vm.runInNewContext(source, { document });
  return { tabs, panels, buttons, cells, status };
}

for (const lang of ['ar', 'en']) {
  test(`${lang}: download filter keeps its language and hides other platforms`, () => {
    const ui = setup(lang);
    ui.buttons[1].events.click();
    assert.deepEqual(ui.cells.map(cell => cell.hidden), [false, true, true]);
    assert.equal(ui.buttons[1].attrs['aria-pressed'], 'true');
    assert.match(ui.status.textContent, lang === 'ar' ? /^عرض التنزيلات:/ : /^Showing downloads for/);
    ui.buttons[0].events.click();
    assert.ok(ui.cells.every(cell => !cell.hidden));
    assert.ok(ui.status.textContent.includes(lang === 'ar' ? 'جميع الأنظمة' : 'All platforms'));
  });
  test(`${lang}: arrow keys follow the reading direction and select the matching panel`, () => {
    const ui = setup(lang);
    let prevented = false;
    ui.tabs[0].events.keydown({ key: lang === 'ar' ? 'ArrowLeft' : 'ArrowRight', preventDefault() { prevented = true; } });
    assert.equal(prevented, true);
    assert.equal(ui.tabs[1].attrs['aria-selected'], 'true');
    assert.equal(ui.tabs[1].focused, true);
    assert.equal(ui.panels.tally.hidden, false);
    assert.equal(ui.panels.nib.hidden, true);
  });
}
