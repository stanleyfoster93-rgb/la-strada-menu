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

Dish photos are stored in `assets/images/` and mapped to menu item IDs in `ITEM_IMAGES` in `scripts/build-menu.py`. To add a photo, add an optimized image and its ID-to-path entry, then regenerate the menu. The generator reports missing files or unknown IDs rather than dropping a photo silently. Photos appear in dish details; items without photos keep the existing layout.

Dish and category names, ingredient descriptions, allergen labels, and interface labels are available in English, Romanian, and Russian. Romanian is the source language; spelling corrections and English and Russian translations are maintained in `scripts/build-menu.py`. Allergen labels are inferred from the listed ingredients, not verified against the restaurant's recipes; they may omit hidden ingredients and cross-contact risks. Confirm them with the restaurant before publication. Review translated names and ingredient terminology, especially regional dishes and brand names. The language selector saves the choice in local storage. Cards keep the compact name/description/portion/price layout; tapping a card opens details.
