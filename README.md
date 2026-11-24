# La Strada Menu

Mobile-first restaurant menu. The static site is built from `index.html`, `style.css`, `script.js`, and `menu.json`.

## Run locally

Serve the repository root with any static HTTP server (the browser `fetch()` API does not work reliably from `file://`). For example:

```sh
python3 -m http.server 8000
```

Then open `http://localhost:8000`.

The locally hosted Cormorant Garamond font used for the restaurant name is licensed under the SIL Open Font License; see `assets/fonts/OFL-Cormorant-Garamond.txt`.

## Edit the menu

The full menu is generated from `menu-analysis.txt`:

```sh
python3 scripts/build-menu.py
```

This imports the transcribed items, portions, prices, and ingredient descriptions into `menu.json`, grouped into 12 mobile-friendly categories. The analysis file notes a few source details that still need verification; these appear as badges in the menu.

Dish photos are stored in `assets/images/`. To add one, use the dish's exact ID from `menu.json` as the filename (for example, `12-10-quattro-formaggi.webp`) and upload the image to that folder. WebP is recommended; JPEG and PNG are also supported. Regenerate `menu.json` with `python3 scripts/build-menu.py` to attach all matching photos automatically. The generator rejects unsupported files and image names that do not match a menu item. Photos for dishes not yet listed in the menu can be kept in `assets/images/pending/`; they are not displayed until matched to a menu item. Items without photos keep the existing layout.

Dish and category names, ingredient descriptions, allergen labels, and interface labels are available in English, Romanian, and Russian. Romanian is the source language; spelling corrections and English and Russian translations are maintained in `scripts/build-menu.py`. Allergen labels are inferred from the listed ingredients, not verified against the restaurant's recipes; they may omit hidden ingredients and cross-contact risks. Confirm them with the restaurant before publication. Review translated names and ingredient terminology, especially regional dishes and brand names. The language selector saves the choice in local storage. Cards keep the compact name/description/portion/price layout; tapping a card opens details.
