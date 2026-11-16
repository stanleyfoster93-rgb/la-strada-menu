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

- Categories live in `categories` and have `id`, localized labels (`en`, `ro`, `ru`), and an `items` array.
- Each item can be an object with `id`, localized `name`, `portion`, numeric `price`, localized `description`, localized `allergens`, optional `image`, and optional `badge`.
- Legacy rows `[name, portion, price, description]` are still accepted for gradual migration. These rows only contain Romanian text, so that text remains Romanian after changing the interface language until translations are added.
- Currency is configured by the top-level `currency` property.

To add a language, add its text to category/item localization objects and to the `TEXT` dictionary in `script.js`.

The language selector supports English, Romanian, and Russian. Language choice is saved in local storage. Cards keep the compact name/description/portion/price layout; tapping a card opens details.
