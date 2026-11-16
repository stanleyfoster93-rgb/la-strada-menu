import json
import runpy
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
        self.assertEqual(cheese_pie["name"]["ru"], "Плацинда с творогом и зеленью")
        self.assertIn("cottage cheese", cheese_pie["description"]["en"].casefold())
        self.assertIn("творог", cheese_pie["description"]["ru"].casefold())


if __name__ == "__main__":
    unittest.main()
