import json
import runpy
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MENU = runpy.run_path(str(ROOT / "scripts" / "build-menu.py"))


class MenuTranslationTests(unittest.TestCase):
    def test_phrase_translation_preserves_meaning_and_grammar(self):
        source = "Ceapă roșie, sfeclă roșie, vișină înghețată, unt de cacao."
        self.assertEqual(
            MENU["translate_description"](source, "ru"),
            "Красный лук, свёкла, замороженная вишня, масло какао.",
        )
        self.assertEqual(
            MENU["translate_description"](source, "en"),
            "Red onion, beetroot, frozen sour cherries, cocoa butter.",
        )

    def test_names_and_brand_words(self):
        translate = MENU["translate_name"]
        self.assertEqual(translate("Caesar cu pui", "ru"), "«Цезарь» с курицей")
        self.assertEqual(translate("Beermaster Brewery — Golden Lager", "en"), "Beermaster Brewery — Golden Lager")
        self.assertEqual(translate("Captain Morgan Spiced Gold", "ru"), "Captain Morgan Spiced Gold")
        self.assertEqual(translate("Gold", "ru"), "Золотая текила")

    def test_frozen_fruit_and_cocoa_butter_are_not_milk(self):
        infer = MENU["infer_allergens"]
        self.assertEqual(infer("Vișină înghețată, unt de cacao."), MENU["ALLERGEN_STATUS"]["none"])
        self.assertEqual(infer("Unt de cacao, grăsime lactată.")["ru"], ["Молоко"])

    def test_dish_photos_are_present_in_generated_menu(self):
        data = json.loads((ROOT / "menu.json").read_text(encoding="utf-8"))
        items = {item["id"]: item for category in data["categories"] for item in category["items"]}
        for item_id, image in {
            "3-7-soleanca": "assets/images/3-7-soleanca.webp",
            "9-1-tocana-de-porc-cu-mamaliga": "assets/images/9-1-tocana-de-porc-cu-mamaliga.webp",
            "12-10-quattro-formaggi": "assets/images/12-10-quattro-formaggi.webp",
            "4-11-cu-pui-in-sos-de-frisca": "assets/images/4-11-cu-pui-in-sos-de-frisca.webp",
            "14-6-desert-cusma-lui-guguta": "assets/images/14-6-desert-cusma-lui-guguta.webp",
            "1-1-gustare-haiduc": "assets/images/1-1-gustare-haiduc.webp",
            "10-1-piure-de-cartofi": "assets/images/10-1-piure-de-cartofi.webp",
            "4-7-vita-si-porc": "assets/images/4-7-vita-si-porc.webp",
        }.items():
            with self.subTest(item_id=item_id):
                self.assertEqual(items[item_id]["image"], image)
                self.assertTrue((ROOT / image).is_file())
        self.assertNotIn("image", items["3-1-zeama"])
        self.assertTrue((ROOT / "assets/images/pending/koryushka.webp").is_file())

    def test_image_discovery_uses_item_id_as_filename(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            directory = Path(temporary_directory) / "assets" / "images"
            directory.mkdir(parents=True)
            (directory / "3-7-soleanca.jpg").touch()
            items = [{"id": "3-7-soleanca"}]

            MENU["attach_images"](items, directory, Path(temporary_directory))

            self.assertEqual(items[0]["image"], "assets/images/3-7-soleanca.jpg")

    def test_image_discovery_rejects_unknown_item_ids(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            directory = Path(temporary_directory)
            (directory / "not-a-menu-item.webp").touch()

            with self.assertRaisesRegex(ValueError, "must match a menu item ID"):
                MENU["attach_images"]([{"id": "3-7-soleanca"}], directory, Path(temporary_directory))

    def test_image_discovery_rejects_duplicate_images(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            directory = Path(temporary_directory)
            (directory / "3-7-soleanca.webp").touch()
            (directory / "3-7-soleanca.png").touch()

            with self.assertRaisesRegex(ValueError, "Multiple images"):
                MENU["attach_images"]([{"id": "3-7-soleanca"}], directory, Path(temporary_directory))

    def test_image_discovery_ignores_pending_subdirectory(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            directory = Path(temporary_directory) / "assets" / "images"
            pending = directory / "pending"
            pending.mkdir(parents=True)
            (pending / "koryushka.webp").touch()
            items = [{"id": "3-7-soleanca"}]

            MENU["attach_images"](items, directory, Path(temporary_directory))

            self.assertNotIn("image", items[0])

    def test_tocana_names_in_generated_menu(self):
        data = json.loads((ROOT / "menu.json").read_text(encoding="utf-8"))
        items = {item["id"]: item for category in data["categories"] for item in category["items"]}
        for item_id, name in {
            "7-5-tocana-de-pui-cu-mamaliga": "Токана из курицы с мамалыгой",
            "8-2-tocana-de-vita-cu-mamaliga": "Токана из говядины с мамалыгой",
            "9-1-tocana-de-porc-cu-mamaliga": "Токана из свинины с мамалыгой",
        }.items():
            with self.subTest(item_id=item_id):
                self.assertEqual(items[item_id]["name"]["ru"], name)
        self.assertEqual(items["3-13-scrob-cu-branza"]["name"]["ru"], "Скроб с брынзой")
        self.assertEqual(items["9-3-costita-la-grill-cu-mujdei"]["name"]["ru"], "Костица с соусом «Муждей»")
        self.assertEqual(items["10-4-mamaliga-cu-branza"]["name"]["ru"], "Мамалыга с брынзой")

    def test_pie_names_in_russian_menu(self):
        data = json.loads((ROOT / "menu.json").read_text(encoding="utf-8"))
        items = {item["id"]: item for category in data["categories"] for item in category["items"]}
        expected_names = {
            "4-1-placinta-cu-branza-de-vaci-si-verdeata": "С брынзой и зеленью",
            "4-2-cascaval": "С сыром",
            "4-3-cartofi": "С картофелем",
            "4-4-varza": "С капустой",
            "4-5-visina": "С вишней",
            "4-6-mar-bostan": "С яблоком / тыквой",
        }
        for item_id, name in expected_names.items():
            with self.subTest(item_id=item_id):
                self.assertEqual(items[item_id]["name"]["ru"], name)

    def test_generated_data_includes_corrected_text(self):
        data = json.loads((ROOT / "menu.json").read_text(encoding="utf-8"))
        items = {item["id"]: item for category in data["categories"] for item in category["items"]}
        self.assertEqual(len(items), 247)
        salad = items["2-3-din-legume"]
        self.assertIn("красный лук", salad["description"]["ru"])
        self.assertEqual(salad["name"]["ru"], "Овощной салат")
        pie = items["4-5-visina"]
        self.assertEqual(pie["allergens"], MENU["ALLERGEN_STATUS"]["none"])
        self.assertIn("păstăi", items["10-7-cartof-cu-ciuperci-pastari"]["name"]["ro"])
        cheese_pie = items["4-1-placinta-cu-branza-de-vaci-si-verdeata"]
        self.assertEqual(cheese_pie["name"]["ro"], "Plăcintă cu brânză de vaci și verdeață")
        self.assertEqual(cheese_pie["name"]["en"], "Pie with cottage cheese and herbs")
        self.assertEqual(cheese_pie["name"]["ru"], "С брынзой и зеленью")
        self.assertIn("cottage cheese", cheese_pie["description"]["en"].casefold())
        self.assertIn("творог", cheese_pie["description"]["ru"].casefold())


if __name__ == "__main__":
    unittest.main()
