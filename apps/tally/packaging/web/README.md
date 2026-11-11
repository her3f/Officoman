# Hosting Tally for the web


`tally-web-<version>.zip` (from the GitHub release, or `packaging/web/package.sh`) holds a
static site in `tally-web-<version>/`:

| File | What it is |
|---|---|
| `index.html` | The page. It loads everything through relative URLs. |
| `tally-web-<hash>.js` | wasm-bindgen glue (generated, ES module) |
| `tally-web-<hash>_bg.wasm` | The app (compresses to roughly a third with gzip/Brotli) |
| `_headers`, `.htaccess` | Sample header rules for Netlify/Cloudflare Pages and Apache |

There is no server-side code. Upload the folder's contents anywhere that serves static files.

## Any path works

All URLs in `index.html` are relative (`public_url = "./"` in `apps/tally-web/Trunk.toml`),
so the site works at a domain root (`https://example.com/`), under a prefix
(`https://example.com/tools/tally/`) and from a CDN bucket. The asset names carry a content
hash, so they can be cached forever. Only `index.html` needs revalidation.

## Required server settings

- **MIME type:** serve `.wasm` as `application/wasm`. Browsers refuse to stream-compile it under
  any other type, and the app then loads slowly or not at all. Serve `.js` as `text/javascript`.
  Most hosts already do both. For nginx, check that `mime.types` has `application/wasm wasm;`.
- **Compression:** turn on gzip or Brotli for `.wasm`, `.js` and `.html`. That cuts the
  download to roughly a third. You can also precompress (`brotli -k *.wasm`) and let
  the server send `Content-Encoding: br`.
- **Caching:** `Cache-Control: public, max-age=31536000, immutable` on the hashed `.wasm` and
  `.js` files, and `no-cache` on `index.html`.
- **HTTPS:** WebGPU (and the clipboard) only work in a secure context, which means `https://`
  or `http://localhost`. Over plain HTTP elsewhere, the app falls back to WebGL2.
- **No special isolation headers:** Tally doesn't use `SharedArrayBuffer`, so it doesn't
  need `Cross-Origin-Opener-Policy` or `Cross-Origin-Embedder-Policy`. If your site already sends
  COEP `require-corp`, also send `Cross-Origin-Resource-Policy: same-origin` (or `cross-origin`
  when the files live on a CDN) on the app's files.

nginx example:

```nginx
location /tally/ {
    types { application/wasm wasm; text/javascript js; text/html html; }
    gzip on;
    gzip_types application/wasm text/javascript text/html;
    location ~* \.(wasm|js)$ { add_header Cache-Control "public, max-age=31536000, immutable"; }
    location ~* index\.html$ { add_header Cache-Control "no-cache"; }
}
```

Local test: `python3 -m http.server 8765` inside the folder, then open http://localhost:8765/.

## Embedding in a page (iframe)

```html
<iframe
  src="https://example.com/tally/"
  title="Tally spreadsheet"
  style="width: 100%; height: 720px; border: 0;"
  allow="fullscreen; clipboard-read; clipboard-write"
  allowfullscreen>
</iframe>
```

- The app fills the iframe and follows its size, so size the iframe and not the app.
- Keyboard shortcuts go to the iframe after the user clicks into it, as with any embedded app.
- **Cross-origin embeds** work. Preferences are kept in the iframe's `localStorage`. Browsers
  that partition or block third-party storage may forget them between visits, and the app
  then starts with defaults.
- **Sandboxed iframes** need at least
  `sandbox="allow-scripts allow-same-origin allow-downloads allow-popups"`. Without
  `allow-same-origin` there's no storage. Without `allow-downloads`, Save and Export (browser
  downloads) are blocked.
- Don't send `X-Frame-Options: DENY` or a `frame-ancestors` CSP that excludes the embedding page.
- **Window chrome:** `?chrome=none` on the iframe `src` leaves out the title bar and the File tab
  (whose Backstage view then never opens); `?chrome=notitlebar` or `?chrome=nofiletab` leave out just
  one. Use them when the host window already shows the file name and owns the files, so the sheet's
  own Open or Save As cannot replace what the host thinks is open. Everything stays on by default.

### The parent bridge (`?host=parent`)

A page framing Tally in a **same-origin** iframe can add `?host=parent` to the iframe's URL
(`https://example.com/tally/?host=parent`) and have Tally hand its files over instead of
downloading them. The two sides talk `postMessage` with plain window messages that carry a
`type`:

| Message | Direction | Fields |
|---|---|---|
| `tally:ready` | app → page | `version`, `appVersion`: the app is listening; send a file now |
| `tally:open` | page → app | `name`, `bytes` (an `ArrayBuffer` or `Uint8Array`): open like File › Open |
| `tally:save` | app → page | `name`, `bytes` (a transferred `ArrayBuffer`): every file the app would otherwise download (Save, Save As, Export as PDF). The page stores it and reports failures itself. |
| `tally:dirty` | app → page | `dirty`: unsaved changes appeared or went away |
| `tally:failed` | app → page | `error`: the app couldn't start |

In host mode the app starts with an empty workbook instead of a sample, so the framing page
should guard leaving the page while changes are unsaved. `&author=` names the user for the
notes and comments the app creates. Opening `?host=parent` outside an iframe gives the normal
app with downloads.

### Embedding without an iframe (page host mode)

A page that loads the Tally module into its own document — its own `<canvas
id="tally_canvas">` inside a component, sized to a box beside the page's own header and
controls — opts in with `data-host="page"` on that canvas. The behaviour is the same as the
parent bridge, except the transport is DOM `CustomEvent`s on the canvas instead of
`postMessage`: the app dispatches `tally:ready`, `tally:save`, `tally:dirty` and
`tally:failed` on the canvas with the message fields above as the event's `detail`, and the
page dispatches `tally:open` on the canvas with `detail: { name, bytes }` to open a
workbook. Events don't bubble, so two editors on one page can't hear each other; listen on the
canvas itself.

```html
<canvas id="tally_canvas" data-host="page" style="width: 100%; height: 600px; border: 0;"></canvas>
```

```js
import init from "./tally-web-<hash>.js"; // the wasm-bindgen glue shipped with the app

// Listen first: the app announces itself while `init` runs.
const canvas = document.getElementById("tally_canvas");

canvas.addEventListener("tally:ready", async () => {
  // Open a workbook of the page's own, as with File › Open.
  const bytes = await workbookBytes(); // an ArrayBuffer or Uint8Array
  canvas.dispatchEvent(new CustomEvent("tally:open", {
    detail: { name: "Budget.xlsx", bytes },
  }));
});

// Every file Tally would otherwise download (Save, Save As, Export as PDF) arrives here.
canvas.addEventListener("tally:save", (event) => {
  const { name, bytes } = event.detail; // bytes is an ArrayBuffer
  storeFile(name, bytes);
});

canvas.addEventListener("tally:dirty", (event) => {
  warnBeforeLeaving(event.detail.dirty);
});
canvas.addEventListener("tally:failed", (event) => {
  showError(event.detail.error);
});

await init({ module_or_path: "./tally-web-<hash>_bg.wasm" });
```

As with the parent bridge, the app starts with an empty workbook instead of a sample, and
`?author=` on the page's URL names the user for new notes and comments. The `data-host` value
must be exactly `page`; anything else is ignored, and the app runs as a standalone page with
downloads.

The messages and both transports are the shared contract of [`craft-web-host`](https://github.com/storytold/craft-libs/tree/main/crates/web-host) (storytold/craft-libs#420), the same for every Craft app: its README lists every message, including `saved`, with the compatibility notes. In `tally:ready`, `version` is the contract's (`"1"`) and `appVersion` is this app's release. Tally reads bytes, so a host sends `bytes`, not a `File`.

### Trust and limits

- **Who is trusted.** In page host mode the page and Tally share one document, so any script on the page can drive the app: open files in it and receive what it saves. Use this mode only for a page you control. The iframe mode (`?host=parent`) answers only the parent window, on the page's own origin.
- **Files from the host are untrusted input.** An opened file goes through the same reading as one picked with File ▸ Open or dropped on the window, with the same format limits; before it is copied into the app's memory, its size is checked against the host open limit (512 MiB) and a larger file is refused, and a name is cut to 255 characters.
- **The event and message names are the interface.** `tally:ready`, `tally:open`, `tally:save`, `tally:dirty` and `tally:failed`, and the fields they carry (the same as the `?host=parent` messages), stay stable; changing one is a breaking change.

### Driving it from the page (`window.tally`)

Every Tally web build puts `window.tally` on the page, from [`craft-web-api`](https://github.com/storytold/craft-libs/tree/main/crates/web-api) (storytold/craft-libs#413), the same shape in every Craft app. `tally.request(method, params)` calls any method of the control channel the desktop app serves (`docs/control-protocol.md`), and `execute(command, params)`, `commands()`, `docInspect(params)`, `uiInspect(params)` and `screenshot(params)` are shortcuts for the common ones. Each returns a Promise that resolves with the method's result and rejects with an `Error`; a call the app does not answer within 30 seconds rejects, and the app skips it if it has not started it; a call the app has already taken still finishes, so a retry after a timeout can apply a command twice.

```js
const book = await tally.docInspect();               // sheets, used ranges, tables, charts, names, selection
await tally.execute("cell.set", { cell: "A1", input: "Total" });
const { data } = await tally.screenshot();          // the canvas as PNG (base64)
```

The API is there in every mode, with or without a host. Opening a workbook, handing a saved or exported file to the page, the file name and the unsaved flag stay with the host messages above.

## Renderer selection

Tally's web build is the same egui app as the desktop one, compiled to wasm
(`apps/tally-web`). It renders with the backend `apps/tally-web` selects (WebGPU
where available, otherwise WebGL2). If the web app adds URL flags to force a backend (as the
sibling Craft apps do with `?webgl` / `?cpu`), document them here; they also work on the
iframe `src`.

A browser with neither WebGPU nor WebGL2 gets a message in place of the app.
