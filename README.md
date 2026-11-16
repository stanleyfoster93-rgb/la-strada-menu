# Cafenea La Strada — Menu

Mobile-first tourist menu for Cafenea La Strada. Menu items are loaded from `menu.json`; the interface displays the English text for visitors.

## Run locally

Because the page uses `fetch()` to load `menu.json`, serve the repository over HTTP instead of opening `index.html` directly with a `file://` URL. For example, with Python installed:

```bash
python3 -m http.server 8000
```

Then open <http://localhost:8000> in your browser.

## Files

- `index.html` — page structure and accessible dish-details dialog.
- `style.css` — responsive mobile-first styling.
- `script.js` — menu loading, validation, rendering, and dialog behavior.
- `menu.json` — categories and menu data.
