# Cafenea La Strada — Menu

Mobile-first tourist menu for Cafenea La Strada with English, Romanian, and Russian language support. The selected language is saved in the browser and restored on the next visit.

## Run locally

Because the page uses `fetch()` to load `menu.json`, serve the repository over HTTP instead of opening `index.html` directly with a `file://` URL. For example, with Python installed:

```bash
python3 -m http.server 8000
```

Then open <http://localhost:8000> in your browser.

## Files

- `index.html` — page structure, language picker, and accessible dish-details dialog.
- `style.css` — responsive, iPhone-friendly mobile-first styling with safe-area support.
- `script.js` — menu loading, validation, language switching, and dialog behavior.
- `menu.json` — categories and menu data translated into EN, RO, and RU.
