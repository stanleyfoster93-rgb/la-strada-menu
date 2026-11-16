# La Strada Menu

Mobile-first restaurant menu. The static site is built from `index.html`, `style.css`, `script.js`, and `menu.json`.

## Run locally

Serve the repository root with any static HTTP server (the browser `fetch()` API does not work reliably from `file://`). For example:

```sh
python3 -m http.server 8000
```

Then open `http://localhost:8000`.

## Edit the menu

Edit `menu.json`:

- Categories live in `categories` and have `id`, an English `en` label, and an `items` array.
- Each item can be an object with `id`, English `name`, `portion`, numeric or string `price`, English `description`, English `allergens`, optional `image`, and optional `badge`.
- Legacy rows `[name, portion, price, description, allergens]` are also accepted; provide English text for all visitor-facing content.
- Currency is configured by the top-level `currency` property.

Cards show the name, description, portion, and price; tapping a card opens its details.
