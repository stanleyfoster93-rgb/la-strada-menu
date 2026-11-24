# Dish photos

Add a photo here using the exact menu item ID from `menu.json` as its filename:

```text
12-10-quattro-formaggi.webp
```

WebP is recommended to keep downloads fast. JPEG (`.jpg`, `.jpeg`) and PNG (`.png`) are also supported. After adding or replacing photos, regenerate `menu.json`:

```sh
python3 scripts/build-menu.py
```

To upload through GitHub, open this folder, choose **Add file → Upload files**, select the photos, and commit. The filename still needs to match the item's ID.

The generator connects each image to the menu item with the matching ID. Filenames that do not match an item ID, duplicate images for one dish, and unsupported file types are reported as errors.
