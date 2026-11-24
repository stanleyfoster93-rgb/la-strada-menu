#!/usr/bin/env python3
import json
import re
import unicodedata
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "menu-analysis.txt"
OUTPUT = ROOT / "menu.json"
IMAGE_DIRECTORY = ROOT / "assets" / "images"
IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}
PLACINTA_NAMES_RU = {
    1: "С творогом и зеленью",
    2: "С сыром",
    3: "С картофелем",
    4: "С капустой",
    5: "С вишней",
    6: "С яблоком / тыквой",
}

SOURCE_SECTION_NAMES = {
    1: {"en": "Cold starters", "ro": "Gustări reci", "ru": "Холодные закуски"},
    2: {"en": "Salads", "ro": "Salate", "ru": "Салаты"},
    3: {"en": "Soups & egg dishes", "ro": "Supe și bucate din ouă", "ru": "Супы и блюда из яиц"},
    4: {"en": "Pies, khachapuri & pancakes", "ro": "Plăcinte, khachapuri și clătite", "ru": "Плацинды, хачапури и блины"},
    5: {"en": "Fish dishes", "ro": "Preparate din pește", "ru": "Рыбные блюда"},
    6: {"en": "Skillet dishes", "ro": "Preparate la tigaie", "ru": "Блюда на сковороде"},
    7: {"en": "Chicken dishes", "ro": "Preparate din pui", "ru": "Блюда из курицы"},
    8: {"en": "Beef dishes", "ro": "Preparate din vită", "ru": "Блюда из говядины"},
    9: {"en": "Pork dishes", "ro": "Preparate din porc", "ru": "Блюда из свинины"},
    10: {"en": "Side dishes", "ro": "Garnituri", "ru": "Гарниры"},
    11: {"en": "Pasta", "ro": "Paste", "ru": "Паста"},
    12: {"en": "Pizza", "ro": "Pizza", "ru": "Пицца"},
    13: {"en": "Burgers", "ro": "Burgeri", "ru": "Бургеры"},
    14: {"en": "Desserts", "ro": "Deserturi", "ru": "Десерты"},
    15: {"en": "Sauces & extras", "ro": "Sosuri și adaosuri", "ru": "Соусы и добавки"},
    16: {"en": "Soft drinks", "ro": "Băuturi răcoritoare", "ru": "Прохладительные напитки"},
    17: {"en": "Non-alcoholic cocktails", "ro": "Cocktailuri nealcoolice", "ru": "Безалкогольные коктейли"},
    18: {"en": "Hot drinks", "ro": "Băuturi fierbinți", "ru": "Горячие напитки"},
    19: {"en": "Alcoholic cocktails", "ro": "Cocktailuri alcoolice", "ru": "Алкогольные коктейли"},
    20: {"en": "Beer", "ro": "Bere", "ru": "Пиво"},
    21: {"en": "Wine & sparkling wine", "ro": "Vin și vin spumant", "ru": "Вино и игристое вино"},
    22: {"en": "Spirits", "ro": "Băuturi spirtoase", "ru": "Крепкий алкоголь"},
}

CATEGORIES = {
    "starters-salads": {
        "sections": (1, 2),
        "name": {"en": "Starters & salads", "ro": "Gustări și salate", "ru": "Закуски и салаты"},
    },
    "soups-eggs": {
        "sections": (3,),
        "name": {"en": "Soups & eggs", "ro": "Supe și bucate din ouă", "ru": "Супы и блюда из яиц"},
    },
    "pies-pastries": {
        "sections": (4,),
        "name": {"en": "Pies & pastries", "ro": "Plăcinte, khachapuri și clătite", "ru": "Плацинды, хачапури и блины"},
    },
    "mains": {
        "sections": (5, 6, 7, 8, 9),
        "name": {"en": "Main courses", "ro": "Preparate principale", "ru": "Основные блюда"},
    },
    "sides-extras": {
        "sections": (10, 15),
        "name": {"en": "Sides & extras", "ro": "Garnituri și adaosuri", "ru": "Гарниры и добавки"},
    },
    "pasta-pizza-burgers": {
        "sections": (11, 12, 13),
        "name": {"en": "Pasta, pizza & burgers", "ro": "Paste, pizza și burgeri", "ru": "Паста, пицца и бургеры"},
    },
    "desserts": {
        "sections": (14,),
        "name": {"en": "Desserts", "ro": "Deserturi", "ru": "Десерты"},
    },
    "drinks": {
        "sections": (16, 18),
        "name": {"en": "Soft & hot drinks", "ro": "Băuturi răcoritoare și calde", "ru": "Безалкогольные и горячие напитки"},
    },
    "cocktails": {
        "sections": (17, 19),
        "name": {"en": "Cocktails", "ro": "Cocktailuri", "ru": "Коктейли"},
    },
    "beer": {
        "sections": (20,),
        "name": {"en": "Beer & snacks", "ro": "Bere și gustări", "ru": "Пиво и закуски"},
    },
    "wine": {
        "sections": (21,),
        "name": {"en": "Wine & sparkling wine", "ro": "Vin și vin spumant", "ru": "Вино и игристое"},
    },
    "spirits": {
        "sections": (22,),
        "name": {"en": "Spirits", "ro": "Băuturi spirtoase", "ru": "Крепкий алкоголь"},
    },
}

NAME_PHRASES = {
    "en": {
        "gustare „haiduc”": "Haiduc appetizer",
        "gustare haiduc": "Haiduc appetizer",
        "gustare boierească la rachiu": "Traditional brandy snack platter",
        "platou cu cașcaval": "Cheese platter",
        "pateu de ficat": "Liver pâté",
        "gustare de vânătă": "Eggplant appetizer",
        "bruschetta cu avocado și roșii": "Avocado and tomato bruschetta",
        "bruschetta cu somon și brânză": "Salmon and cheese bruschetta",
        "piept de pui": "chicken breast",
        "carne de vită": "beef",
        "carne de porc": "pork",
        "carne de pui": "chicken",
        "cartofi pai": "French fries",
        "cartofi ca acasă": "Home-style potatoes",
        "mămăligă": "polenta",
        "supă cremă": "Cream soup",
        "supă cu": "Soup with",
        "supă de": "Soup with",
        "borș cu": "Borscht with",
        "borș de": "Borscht with",
        "la grill": "grilled",
        "la grătar": "grilled",
        "cu mămăligă": "with polenta",
        "cu cartof în ulcică": "with potatoes in a clay pot",
        "la tigaie": "skillet",
        "la friteuză": "deep-fried",
        "în sortiment": "assorted",
        "înghețată prăjită": "Fried ice cream",
        "platou cu fructe": "Fruit platter",
        "piure de cartofi": "Mashed potatoes",
        "orez cu legume": "Rice with vegetables",
        "spaghetti cu sos bolognese": "Spaghetti Bolognese",
        "cu carne de pui": "with chicken",
        "cu carne de vită": "with beef",
        "cu carne de porc": "with pork",
        "vin și vin spumant": "Wine & sparkling wine",
        "soleancă": "Solyanka",
        "kebab mix plate": "Kebab platter",
        "spaghetti carbonara": "Spaghetti Carbonara",
        "quattro formaggi": "Four-cheese pizza",
        "focaccia": "Focaccia",
        "margherita": "Margherita pizza",
        "„four seasons”": "Four Seasons pizza",
        "ciocolată fierbinte": "Hot chocolate",
        "fruit limonadă": "Fruit lemonade",
        "glintwein": "Mulled wine",
        "retroping pane": "Breaded Retroping",
        "arahide": "Peanuts",
        "pesmeți": "Croutons",
        "caldă „la strada”": "Warm La Strada salad",
        "funcioasă": "Funchoza",
        "„la strada”": "„La Strada”",
        "plăcinte": "Pies",
        "clătite": "Pancakes",
        "gustări la bere": "Beer snacks",
        "la sticlă": "Bottled",
        "seria": "series",
    },
    "ru": {
        "gustare „haiduc”": "Закуска «Хайдук»",
        "gustare haiduc": "Закуска «Хайдук»",
        "gustare boierească la rachiu": "Закуска по-боярски к ракии",
        "platou cu cașcaval": "Сырная тарелка",
        "pateu de ficat": "Печёночный паштет",
        "gustare de vânătă": "Закуска из баклажанов",
        "bruschetta cu avocado și roșii": "Брускетта с авокадо и помидорами",
        "bruschetta cu somon și brânză": "Брускетта с лососем и сыром",
        "piept de pui": "куриная грудка",
        "carne de vită": "говядина",
        "carne de porc": "свинина",
        "carne de pui": "курица",
        "cartofi pai": "картофель фри",
        "cartofi ca acasă": "картофель по-домашнему",
        "mămăligă": "мамалыга",
        "supă cremă": "Крем-суп",
        "supă cu": "Суп с",
        "supă de": "Суп с",
        "borș cu": "Борщ с",
        "borș de": "Борщ с",
        "la grill": "на гриле",
        "la grătar": "на гриле",
        "cu mămăligă": "с мамалыгой",
        "cu cartof în ulcică": "с картофелем в горшочке",
        "la tigaie": "на сковороде",
        "la friteuză": "во фритюре",
        "în sortiment": "ассорти",
        "înghețată prăjită": "Жареное мороженое",
        "platou cu fructe": "Фруктовая тарелка",
        "piure de cartofi": "Картофельное пюре",
        "orez cu legume": "Рис с овощами",
        "spaghetti cu sos bolognese": "Спагетти болоньезе",
        "cu carne de pui": "с курицей",
        "cu carne de vită": "с говядиной",
        "cu carne de porc": "со свининой",
        "vin și vin spumant": "Вино и игристое вино",
        "soleancă": "Солянка",
        "kebab mix plate": "Ассорти кебаб",
        "spaghetti carbonara": "Спагетти карбонара",
        "quattro formaggi": "Пицца «Четыре сыра»",
        "focaccia": "Фокачча",
        "margherita": "Пицца «Маргарита»",
        "„four seasons”": "Пицца «Четыре сезона»",
        "ciocolată fierbinte": "Горячий шоколад",
        "fruit limonadă": "Фруктовый лимонад",
        "glintwein": "Глинтвейн",
        "retroping pane": "Ретропинг в панировке",
        "arahide": "Арахис",
        "pesmeți": "Сухарики",
        "caldă „la strada”": "Тёплый салат «Ла Страда»",
        "funcioasă": "Фунчоза",
        "„la strada”": "«Ла Страда»",
        "plăcinte": "Плацинды",
        "clătite": "Блины",
        "gustări la bere": "Закуски к пиву",
        "la sticlă": "Бутылочное",
        "seria": "серия",
    },
}

NAME_WORDS = {
    "en": {
        "gustare": "appetizer", "salată": "salad", "caldă": "warm", "ficat": "liver",
        "bacon": "bacon", "legume": "vegetables", "vitamin": "Vitamin", "grecească": "Greek",
        "rustică": "rustic", "carne": "meat", "pui": "chicken", "vită": "beef", "porc": "pork",
        "ouă": "eggs", "ou": "egg", "supă": "soup", "zeamă": "chicken soup", "cartofi": "potatoes",
        "cartof": "potato", "brânză": "cheese", "cașcaval": "cheese", "plăcintă": "pie",
        "plăcinte": "pies", "khachapuri": "khachapuri", "clătite": "pancakes", "creveți": "shrimp",
        "somon": "salmon", "crap": "carp", "dorada": "sea bream", "garnituri": "sides",
        "sosuri": "sauces", "adaosuri": "extras", "paste": "pasta", "pizza": "pizza",
        "burgeri": "burgers", "deserturi": "desserts", "înghețată": "ice cream",
        "fructe": "fruit", "băuturi": "drinks", "răcoritoare": "soft", "calde": "hot",
        "cocktailuri": "cocktails", "bere": "beer", "vin": "wine", "spumant": "sparkling",
        "spirtoase": "spirits", "fript": "fried", "prăjit": "fried", "grătar": "grill",
        "cu": "with", "și": "and", "de": "of", "din": "from", "la": "with", "în": "in",
        "platou": "platter", "bruschetta": "bruschetta",
        "ciuperci": "mushrooms", "roșii": "tomatoes", "măr": "apple", "mere": "apples",
        "cafea": "coffee", "ceai": "tea", "espresso": "espresso", "cappuccino": "cappuccino",
        "latte": "latte", "aperol": "Aperol", "cocktail": "cocktail", "hrișcă": "buckwheat",
        "pâine": "bread", "usturoi": "garlic", "morcov": "carrot", "varză": "cabbage",
        "fasole": "beans", "mazăre": "peas", "ardei": "pepper", "măsline": "olives",
        "lămâie": "lemon", "portocală": "orange", "șuncă": "ham",
        "cascaval": "cheese", "mozzarella": "mozzarella", "vegetariană": "Vegetarian",
        "vegetarian": "Vegetarian", "clasic": "Classic", "classic": "Classic",
        "cușma": "hat", "guguță": "Guguta", "gogoase": "doughnuts",
        "vișină": "sour cherry", "maioneză": "mayonnaise", "sos tartar": "tartar sauce",
        "muștar": "mustard", "adjică": "adjika", "miere": "honey", "dulceață": "jam",
        "porumb conservat": "canned corn", "olive": "olives", "castraveți murați": "pickles",
        "salam": "salami", "parmezan": "parmesan", "smântână": "sour cream",
        "ketchup": "ketchup",
    },
    "ru": {
        "gustare": "закуска", "salată": "салат", "caldă": "тёплый", "ficat": "печень",
        "bacon": "бекон", "legume": "овощи", "vitamin": "Витаминный", "grecească": "греческий",
        "rustică": "деревенский", "carne": "мясо", "pui": "курица", "vită": "говядина", "porc": "свинина",
        "ouă": "яйца", "ou": "яйцо", "supă": "суп", "zeamă": "зама", "cartofi": "картофель",
        "cartof": "картофель", "brânză": "сыр", "cașcaval": "сыр", "plăcintă": "плацинда",
        "plăcinte": "плацинды", "khachapuri": "хачапури", "clătite": "блины", "creveți": "креветки",
        "somon": "лосось", "crap": "карп", "dorada": "дорада", "garnituri": "гарниры",
        "sosuri": "соусы", "adaosuri": "добавки", "paste": "паста", "pizza": "пицца",
        "burgeri": "бургеры", "deserturi": "десерты", "înghețată": "мороженое",
        "fructe": "фрукты", "băuturi": "напитки", "răcoritoare": "прохладительные", "calde": "горячие",
        "cocktailuri": "коктейли", "bere": "пиво", "vin": "вино", "spumant": "игристое",
        "spirtoase": "крепкий алкоголь", "fript": "жареный", "prăjit": "жареный", "grătar": "гриль",
        "cu": "с", "și": "и", "de": "", "din": "из", "la": "с", "în": "в",
        "platou": "ассорти", "bruschetta": "брускетта",
        "ciuperci": "грибы", "roșii": "помидоры", "măr": "яблоко", "mere": "яблоки",
        "cafea": "кофе", "ceai": "чай", "espresso": "эспрессо", "cappuccino": "капучино",
        "latte": "латте", "aperol": "Апероль", "cocktail": "коктейль",
        "pâine": "хлеб", "usturoi": "чеснок", "morcov": "морковь", "varză": "капуста",
        "fasole": "фасоль", "mazăre": "горох", "ardei": "перец", "măsline": "оливки",
        "lămâie": "лимон", "portocală": "апельсин", "șuncă": "ветчина", "mozzarella": "моцарелла",
        "vegetariană": "Вегетарианская", "vegetarian": "Вегетарианский", "clasic": "Классический",
        "classic": "Классический", "cușma": "шапка", "guguță": "Гугуцэ", "gogoase": "пончики",
        "vișină": "вишня", "maioneză": "майонез", "sos tartar": "соус тартар",
        "muștar": "горчица", "adjică": "аджика", "miere": "мёд", "dulceață": "варенье",
        "porumb conservat": "консервированная кукуруза", "olive": "оливки", "castraveți murați": "солёные огурцы",
        "salam": "салями", "parmezan": "пармезан", "smântână": "сметана",
        "ketchup": "кетчуп",
    },
}

DESCRIPTION_PHRASES = {
    "ceapă roșie": ("red onion", "красный лук"),
    "sfeclă roșie": ("beetroot", "свёкла"),
    "roșii cherry": ("cherry tomatoes", "помидоры черри"),
    "iaurt grecesc": ("Greek yogurt", "греческий йогурт"),
    "mix salat": ("mixed salad leaves", "смесь салатных листьев"),
    "borș acru": ("sour fermented bran broth", "кислый отвар из отрубей"),
    "asorti de salamuri afumate": ("assorted smoked sausages", "ассорти копчёных колбас"),
    "varză proaspătă": ("fresh cabbage", "свежая капуста"),
    "vișină înghețată": ("frozen sour cherries", "замороженная вишня"),
    "sos picant": ("spicy sauce", "острый соус"),
    "sos pesto": ("pesto sauce", "соус песто"),
    "piept pui": ("chicken breast", "куриная грудка"),
    "ceapă marinată": ("marinated onion", "маринованный лук"),
    "ceafă de porc": ("pork neck", "свиная шея"),
    "costiță de porc": ("pork ribs", "свиные рёбрышки"),
    "ciolan de porc": ("pork knuckle", "свиная рулька"),
    "varză murată": ("pickled cabbage", "квашеная капуста"),
    "porumb conservat": ("canned corn", "консервированная кукуруза"),
    "steak pui": ("chicken steak", "куриный стейк"),
    "înghețată albă/cu ciocolată": ("plain or chocolate ice cream", "белое или шоколадное мороженое"),
    "înghețată albă": ("plain ice cream", "белое мороженое"),
    "dulceață de fructe": ("fruit jam", "фруктовое варенье"),
    "dulceață de vișină": ("sour cherry jam", "вишнёвое варенье"),
    "unt de cacao": ("cocoa butter", "масло какао"),
    "grăsime lactată": ("milk fat", "молочный жир"),
    "în sortiment": ("assorted", "в ассортименте"),
    "sirop mojito": ("Mojito syrup", "сироп «Мохито»"),
    "sirop cocos": ("coconut syrup", "кокосовый сироп"),
    "vin spumant": ("sparkling wine", "игристое вино"),
    "vin roșu": ("red wine", "красное вино"),
    "suc de lime": ("lime juice", "сок лайма"),
    "suc lime": ("lime juice", "сок лайма"),
    "suc ananas": ("pineapple juice", "ананасовый сок"),
    "suc lămâie": ("lemon juice", "лимонный сок"),
    "salam crud de vită": ("raw beef salami", "сырая салями из говядины"),
    "degețele de pui pane": ("breaded chicken fingers", "куриные палочки в панировке"),
    "inele de ceapă": ("onion rings", "луковые кольца"),
    "cartofi bile": ("potato balls", "картофельные шарики"),
    "pesmeți măcinați": ("ground breadcrumbs", "молотые панировочные сухари"),
    "sos tar-tar": ("tartar sauce", "соус тартар"),
    "urechi de porc": ("pork ears", "свиные уши"),
    "sos oyster": ("oyster sauce", "устричный соус"),
    "morcov coreean": ("Korean-style carrot", "морковь по-корейски"),
    "alb, roșu": ("white, red", "белое, красное"),
    "piept de pui": ("chicken breast", "куриная грудка"),
    "carne de vită": ("beef", "говядина"),
    "carne de porc": ("pork", "свинина"),
    "carne de pui": ("chicken", "курица"),
    "ficat de pui": ("chicken liver", "куриная печень"),
    "rădăcină de țelină": ("celery root", "корень сельдерея"),
    "ulei de măsline": ("olive oil", "оливковое масло"),
    "frunză de salată": ("lettuce leaf", "лист салата"),
    "ardei dulce": ("sweet pepper", "сладкий перец"),
    "ardei iute": ("hot pepper", "острый перец"),
    "sos dulce de muștar": ("sweet mustard sauce", "сладкий горчичный соус"),
    "sos de soia": ("soy sauce", "соевый соус"),
    "sos tartar": ("tartar sauce", "соус тартар"),
    "sos caesar": ("Caesar dressing", "соус «Цезарь»"),
    "pastă de tomate": ("tomato paste", "томатная паста"),
    "făină de grâu": ("wheat flour", "пшеничная мука"),
    "făină de porumb": ("cornmeal", "кукурузная мука"),
    "pâine toast": ("toast", "тостовый хлеб"),
    "brânză de vaci": ("cottage cheese", "творог"),
    "brânză de oi": ("sheep's cheese", "овечий сыр"),
    "brânză feta": ("feta cheese", "сыр фета"),
    "brânză cu verdeață": ("herbed cheese", "сыр с зеленью"),
    "cașcaval dorblu": ("Dorblu cheese", "сыр дорблю"),
    "cașcaval camembert": ("Camembert cheese", "сыр камамбер"),
    "cașcaval afumat": ("smoked cheese", "копчёный сыр"),
    "zahăr pudră": ("powdered sugar", "сахарная пудра"),
    "apă gazată": ("sparkling water", "газированная вода"),
    "suc de ananas": ("pineapple juice", "ананасовый сок"),
    "fructe de pădure": ("berries", "лесные ягоды"),
    "cartofi pai": ("French fries", "картофель фри"),
    "cartofi fierți": ("boiled potatoes", "отварной картофель"),
    "ou fiert": ("boiled egg", "варёное яйцо"),
    "miez de nucă": ("walnut kernels", "ядра грецкого ореха"),
    "carne tocată": ("minced meat", "мясной фарш"),
    "roșii proaspete": ("fresh tomatoes", "свежие помидоры"),
    "castraveți murați": ("pickles", "маринованные огурцы"),
    "brânză cu": ("cheese with", "сыр с"),
    "lapte condensat": ("condensed milk", "сгущённое молоко"),
    "cartofi fri": ("French fries", "картофель фри"),
    "fide de orez": ("rice noodles", "рисовая лапша"),
    "carne de vită, porc, pui": ("beef, pork, and chicken", "говядина, свинина и курица"),
    "blue curacao": ("Blue Curaçao", "Блю кюрасао"),
    "cream cheese": ("cream cheese", "сливочный сыр"),
    "elder flower": ("elderflower", "цветки бузины"),
    "oyster sauce": ("oyster sauce", "устричный соус"),
    "peach liqueur": ("peach liqueur", "персиковый ликёр"),
    "pisang ambon": ("Pisang Ambon", "Пизанг Амбон"),
    "sare de mare": ("sea salt", "морская соль"),
    "salam crud afumat": ("dry-cured smoked salami", "сырокопчёная салями"),
    "salamuri afumate": ("smoked sausages", "копчёные колбасы"),
    "triple sec": ("triple sec", "трипл-сек"),
}

NAME_EXACT = {
    "silver": ("Silver tequila", "Серебряная текила"),
    "gold": ("Gold tequila", "Золотая текила"),
    "platou cu carne": ("Meat platter", "Мясное ассорти"),
    "plăcintă cu brânză de vaci și verdeață": (
        "Pie with cottage cheese and herbs",
        "Плацинда с творогом и зеленью",
    ),
    "cu ficat și bacon": ("With liver and bacon", "С печенью и беконом"),
    "din legume": ("Vegetable salad", "Овощной салат"),
    "caesar cu pui": ("Caesar with chicken", "«Цезарь» с курицей"),
    "caesar cu bacon": ("Caesar with bacon", "«Цезарь» с беконом"),
    "caesar cu creveți": ("Caesar with shrimp", "«Цезарь» с креветками"),
    "„grecească”": ("Greek salad", "Греческий салат"),
    "salată rustică cu couscous": ("Rustic salad with couscous", "Деревенский салат с кускусом"),
    "mix cu mozzarella și avocado": ("Mixed salad with mozzarella and avocado", "Салатный микс с моцареллой и авокадо"),
    "supă cremă de pui cu ciuperci": ("Creamy chicken and mushroom soup", "Крем-суп с курицей и грибами"),
    "supă cremă cu cartof și ciuperci": ("Creamy potato and mushroom soup", "Крем-суп с картофелем и грибами"),
    "supă cu perișoare": ("Meatball soup", "Суп с фрикадельками"),
    "borș cu carne de porc": ("Borscht with pork", "Борщ со свининой"),
    "borș cu fasole": ("Borscht with beans", "Борщ с фасолью"),
    "supă de mazăre cu bacon": ("Pea soup with bacon", "Гороховый суп с беконом"),
    "supă de mazăre": ("Pea soup", "Гороховый суп"),
    "shakshouka": ("Shakshouka", "Шакшука"),
    "omletă cu șuncă, cașcaval și roșii": ("Omelette with ham, cheese and tomatoes", "Омлет с ветчиной, сыром и помидорами"),
    "omletă cu cașcaval": ("Cheese omelette", "Омлет с сыром"),
    "scrob cu brânză": ("Scrambled eggs with cheese", "Скроб с брынзой"),
    "brânză și verdeață": ("Cheese and herbs", "Сыр и зелень"),
    "măr / bostan": ("Apple / pumpkin", "Яблоко / тыква"),
    "cu cartofi și ciuperci": ("With potatoes and mushrooms", "С картофелем и грибами"),
    "cu pui în sos de frișcă": ("With chicken in cream sauce", "С курицей в сливочном соусе"),
    "crap prăjit cu legume": ("Fried carp with vegetables", "Жареный карп с овощами"),
    "somon la grill": ("Grilled salmon", "Лосось на гриле"),
    "dorada cu legume": ("Sea bream with vegetables", "Дорада с овощами"),
    "risotto cu creveți": ("Shrimp risotto", "Ризотто с креветками"),
    "piept de pui cu legume în sos picant": ("Chicken breast with vegetables in spicy sauce", "Куриная грудка с овощами в остром соусе"),
    "pui a la italia cu ciuperci": ("Italian-style chicken with mushrooms", "Курица по-итальянски с грибами"),
    "asorti grill la tigaie": ("Mixed grill skillet", "Мясное ассорти на сковороде"),
    "tigaie cu cartofi, carne și ou": ("Skillet with potatoes, meat and egg", "Картофель с мясом и яйцом на сковороде"),
    "carne de vită cu legume în sos picant": ("Beef with vegetables in spicy sauce", "Говядина с овощами в остром соусе"),
    "steak de pui la grătar": ("Grilled chicken steak", "Куриный стейк на гриле"),
    "frigărui de pui": ("Chicken skewers", "Куриный шашлык"),
    "tocană de pui cu mămăligă": ("Chicken stew with polenta", "Токана из курицы с мамалыгой"),
    "steak de vită": ("Beef steak", "Стейк из говядины"),
    "tocană de vită cu mămăligă": ("Beef stew with polenta", "Токана из говядины с мамалыгой"),
    "tocană de porc cu mămăligă": ("Pork stew with polenta", "Токана из свинины с мамалыгой"),
    "steak din ceafă de porc": ("Pork neck steak", "Стейк из свиной шеи"),
    "costiță la grill cu mujdei": ("Grilled ribs with garlic sauce", "Костица с соусом «Муждей»"),
    "picior (ciolan) de porc cu varză murată": ("Pork knuckle with pickled cabbage", "Свиная рулька с квашеной капустой"),
    "mămăligă cu brânză": ("Polenta with cheese", "Мамалыга с брынзой"),
    "cartofi umpluți cu legume": ("Potatoes stuffed with vegetables", "Картофель, фаршированный овощами"),
    "cartof cu ciuperci / păstări": ("Potato with mushrooms / green beans", "Картофель с грибами / стручковой фасолью"),
    "legume la grătar": ("Grilled vegetables", "Овощи на гриле"),
    "tagliatelle cu ciuperci": ("Tagliatelle with mushrooms", "Тальятелле с грибами"),
    "cu creveți, ceapă roșie și rucola": ("With shrimp, red onion and arugula", "С креветками, красным луком и рукколой"),
    "cu șuncă și roșii": ("With ham and tomatoes", "С ветчиной и помидорами"),
    "cu salami": ("With salami", "С салями"),
    "cu șuncă și măsline": ("With ham and olives", "С ветчиной и оливками"),
    "cu șuncă și vinete": ("With ham and eggplant", "С ветчиной и баклажанами"),
    "cu șuncă și ananas": ("With ham and pineapple", "С ветчиной и ананасом"),
    "cu carne de pui și ciuperci": ("With chicken and mushrooms", "С курицей и грибами"),
    "cu carne de pui și porumb": ("With chicken and corn", "С курицей и кукурузой"),
    "salami, porumb și ardei iute": ("Salami, corn and hot pepper", "Салями, кукуруза и острый перец"),
    "cheese burger cu carne de pui": ("Chicken cheeseburger", "Чизбургер с курицей"),
    "cheese burger cu carne de vită": ("Beef cheeseburger", "Чизбургер с говядиной"),
    "cheesecake": ("Cheesecake", "Чизкейк"),
    "tiramisu": ("Tiramisu", "Тирамису"),
    "prăjitură de casă cu fructe de pădure și înghețată": ("Homemade cake with berries and ice cream", "Домашний пирог с ягодами и мороженым"),
    "desert „cușma lui guguță”": ("Guguță's Hat dessert", "Десерт «Шапка Гугуцэ»"),
    "gogoase cu vișină": ("Doughnuts with sour cherries", "Пончики с вишней"),
    "clătite cu brânză și stafide": ("Pancakes with cheese and raisins", "Блины с сыром и изюмом"),
    "măr copt cu miez de nucă": ("Baked apple with walnuts", "Печёное яблоко с грецкими орехами"),
    "salată de fructe": ("Fruit salad", "Фруктовый салат"),
    "înghețată cu fructe": ("Ice cream with fruit", "Мороженое с фруктами"),
    "înghețată în sortiment cu adaosuri": ("Assorted ice cream with toppings", "Мороженое в ассортименте с добавками"),
    "tabletă de ciocolată în sortiment": ("Assorted chocolate bars", "Шоколад в ассортименте"),
    "topping și sirop în sortiment": ("Assorted toppings and syrups", "Топпинги и сиропы в ассортименте"),
    "ardei dulce": ("Sweet pepper", "Сладкий перец"),
    "ardei iute": ("Hot pepper", "Острый перец"),
    "suc fresh": ("Fresh juice", "Свежевыжатый сок"),
    "suc „orhei vit”": ("Orhei Vit juice", "Сок «Orhei Vit»"),
    "cafea espresso": ("Espresso", "Эспрессо"),
    "cafea cappuccino": ("Cappuccino", "Капучино"),
    "cafea latte": ("Latte", "Латте"),
    "ceai infuzie": ("Infused tea", "Заварной чай"),
    "ceai de fructe": ("Fruit tea", "Фруктовый чай"),
    "aperol spritz": ("Aperol Spritz", "Апероль шприц"),
    "platou la bere la friteuză": ("Deep-fried beer snack platter", "Ассорти закусок к пиву во фритюре"),
    "degețele de pui pane": ("Breaded chicken fingers", "Куриные палочки в панировке"),
    "urechi de porc la friteuză": ("Deep-fried pork ears", "Свиные уши во фритюре"),
    "urechi de porc picante": ("Spicy pork ears", "Острые свиные уши"),
    "creveți pane": ("Breaded shrimp", "Креветки в панировке"),
    "platou la bere": ("Beer snack platter", "Ассорти закусок к пиву"),
    "la pahar": ("By the glass", "Бокал"),
    "sosuri / toppinguri": ("Sauces / toppings", "Соусы / топпинги"),
    "chateau vartely — categoria „individo”": ("Chateau Vartely — Individo range", "Chateau Vartely — серия «Individo»"),
    "vin de marcă": ("Vintage wine", "Марочное вино"),
    "vin spumant „maestro”": ("Maestro sparkling wine", "Игристое вино «Maestro»"),
    "draft": ("Draft", "Разливное"),
    "lichior": ("Liqueur", "Ликёр"),
    "ice tea": ("Iced tea", "Холодный чай"),
    "fruit shake": ("Fruit shake", "Фруктовый коктейль"),
    "coffee frappe": ("Coffee frappé", "Кофе фраппе"),
}

DESCRIPTION_WORDS = {
    "de": ("of", "из"),
    "cu": ("with", "с"),
    "și": ("and", "и"),
    "în": ("in", "в"),
    "acru": ("sour", "кислый"),
    "afumat": ("smoked", "копчёный"),
    "afumate": ("smoked", "копчёные"),
    "alb": ("white", "белый"),
    "albă": ("white", "белая"),
    "alune": ("hazelnuts", "лесные орехи"),
    "ananas": ("pineapple", "ананас"),
    "apă": ("water", "вода"),
    "arahide": ("peanuts", "арахис"),
    "ardei": ("pepper", "перец"),
    "banană": ("banana", "банан"),
    "bile": ("balls", "шарики"),
    "biscuiți": ("biscuits", "печенье"),
    "bostan": ("pumpkin", "тыква"),
    "bostănel": ("zucchini", "кабачок"),
    "brânză": ("cheese", "сыр"),
    "cacao": ("cocoa", "какао"),
    "caramelă": ("caramel", "карамель"),
    "cartof": ("potato", "картофель"),
    "cartofi": ("potatoes", "картофель"),
    "castraveți": ("cucumbers", "огурцы"),
    "ceafă": ("pork neck", "свиная шея"),
    "ceapă": ("onion", "лук"),
    "cereale": ("cereal", "хлопья"),
    "ciolan": ("pork knuckle", "свиная рулька"),
    "ciocolată": ("chocolate", "шоколад"),
    "ciuperci": ("mushrooms", "грибы"),
    "conopidă": ("cauliflower", "цветная капуста"),
    "conservat": ("canned", "консервированный"),
    "conservată": ("canned", "консервированная"),
    "condiment": ("seasoning", "приправа"),
    "condimente": ("spices", "специи"),
    "coreean": ("Korean-style", "по-корейски"),
    "costiță": ("ribs", "рёбрышки"),
    "crap": ("carp", "карп"),
    "crud": ("raw", "сырой"),
    "creveți": ("shrimp", "креветки"),
    "cătină": ("sea buckthorn", "облепиха"),
    "dulce": ("sweet", "сладкий"),
    "dulceață": ("jam", "варенье"),
    "energizant": ("energy drink", "энергетический напиток"),
    "făină": ("flour", "мука"),
    "fasole": ("beans", "фасоль"),
    "feta": ("feta", "фета"),
    "fiert": ("boiled", "отварной"),
    "fierți": ("boiled", "отварные"),
    "ficat": ("liver", "печень"),
    "fri": ("fries", "фри"),
    "frunză": ("leaf", "лист"),
    "fructe": ("fruit", "фрукты"),
    "grâu": ("wheat", "пшеница"),
    "grecesc": ("Greek", "греческий"),
    "grăsime": ("fat", "жир"),
    "ghimbir": ("ginger", "имбирь"),
    "iaurt": ("yogurt", "йогурт"),
    "inele": ("rings", "кольца"),
    "iute": ("hot", "острый"),
    "lapte": ("milk", "молоко"),
    "lămâie": ("lemon", "лимон"),
    "mămăligă": ("polenta", "мамалыга"),
    "mărar": ("dill", "укроп"),
    "măsline": ("olives", "оливки"),
    "măcinați": ("ground", "молотые"),
    "mazăre": ("peas", "горох"),
    "mentă": ("mint", "мята"),
    "miere": ("honey", "мёд"),
    "mix": ("mix", "смесь"),
    "morcov": ("carrot", "морковь"),
    "murați": ("pickled", "маринованные"),
    "murată": ("pickled", "маринованная"),
    "murături": ("pickles", "соленья"),
    "mujdei": ("garlic sauce", "чесночный соус"),
    "măr": ("apple", "яблоко"),
    "miez": ("kernel", "ядро"),
    "nucă": ("walnut", "грецкий орех"),
    "nuci": ("nuts", "орехи"),
    "oțet": ("vinegar", "уксус"),
    "ou": ("egg", "яйцо"),
    "ouă": ("eggs", "яйца"),
    "pâine": ("bread", "хлеб"),
    "pane": ("breaded", "в панировке"),
    "pârjoală": ("patty", "котлета"),
    "păstări": ("green beans", "стручковая фасоль"),
    "păstăi": ("green beans", "стручковая фасоль"),
    "pateu": ("pâté", "паштет"),
    "perișoare": ("meatballs", "фрикадельки"),
    "parmezan": ("Parmesan", "пармезан"),
    "pastă": ("paste", "паста"),
    "pesmeți": ("breadcrumbs", "панировочные сухари"),
    "pește": ("fish", "рыба"),
    "piept": ("breast", "грудка"),
    "picant": ("spicy", "острый"),
    "picantă": ("spicy", "острая"),
    "portocală": ("orange", "апельсин"),
    "portocale": ("oranges", "апельсины"),
    "porc": ("pork", "свинина"),
    "porumb": ("corn", "кукуруза"),
    "proaspete": ("fresh", "свежие"),
    "proaspătă": ("fresh", "свежая"),
    "pudră": ("powdered", "пудра"),
    "pui": ("chicken", "курица"),
    "rădăcină": ("root", "корень"),
    "roșie": ("tomato", "помидор"),
    "roșii": ("tomatoes", "помидоры"),
    "rum": ("rum", "ром"),
    "salată": ("lettuce", "салат"),
    "salat": ("salad", "салат"),
    "salami": ("salami", "салями"),
    "salam": ("salami", "салями"),
    "salamuri": ("sausages", "колбасы"),
    "sare": ("salt", "соль"),
    "scrob": ("scrambled eggs", "яичница"),
    "sfeclă": ("beetroot", "свёкла"),
    "slănină": ("bacon", "сало"),
    "smântână": ("sour cream", "сметана"),
    "somon": ("salmon", "лосось"),
    "soia": ("soy", "соя"),
    "sos": ("sauce", "соус"),
    "spanac": ("spinach", "шпинат"),
    "scrumbie": ("herring", "сельдь"),
    "strugure": ("grape", "виноград"),
    "struguri": ("grapes", "виноград"),
    "suc": ("juice", "сок"),
    "șuncă": ("ham", "ветчина"),
    "șop": ("dill", "укроп"),
    "șpănac": ("spinach", "шпинат"),
    "șalotă": ("shallot", "шалот"),
    "șofran": ("saffron", "шафран"),
    "tartă": ("tart", "тарт"),
    "tăiței": ("noodles", "лапша"),
    "topping": ("topping", "топпинг"),
    "tocat": ("minced", "рубленый"),
    "tocată": ("minced", "рубленое"),
    "tonic": ("tonic", "тоник"),
    "țelină": ("celery", "сельдерей"),
    "ulei": ("oil", "масло"),
    "unt": ("butter", "сливочное масло"),
    "usturoi": ("garlic", "чеснок"),
    "varză": ("cabbage", "капуста"),
    "verdețuri": ("herbs", "зелень"),
    "verdețea": ("herbs", "зелень"),
    "verdeată": ("herbs", "зелень"),
    "vânătă": ("eggplant", "баклажан"),
    "vinete": ("eggplant", "баклажаны"),
    "vită": ("beef", "говядина"),
    "vișină": ("sour cherry", "вишня"),
    "vodka": ("vodka", "водка"),
    "zahăr": ("sugar", "сахар"),
    "absinth": ("absinthe", "абсент"),
    "asorti": ("assorted", "ассорти"),
    "mare": ("sea", "морская"),
    "aluat": ("dough", "тесто"),
    "aperol": ("Aperol", "Апероль"),
    "avocado": ("avocado", "авокадо"),
    "bacon": ("bacon", "бекон"),
    "baileys": ("Baileys", "Бейлис"),
    "basturma": ("basturma", "бастурма"),
    "blue": ("blue", "блю"),
    "borș": ("borscht", "борщ"),
    "broccoli": ("broccoli", "брокколи"),
    "bruschetta": ("bruschetta", "брускетта"),
    "cafea": ("coffee", "кофе"),
    "camembert": ("Camembert", "камамбер"),
    "cașcaval": ("cheese", "сыр"),
    "chiflă": ("bun", "булочка"),
    "cherry": ("cherry", "вишня"),
    "clătite": ("pancakes", "блины"),
    "cocos": ("coconut", "кокос"),
    "cola": ("cola", "кола"),
    "couscous": ("couscous", "кускус"),
    "cream": ("cream", "сливки"),
    "curacao": ("curaçao", "кюрасао"),
    "degețele": ("chicken fingers", "куриные палочки"),
    "dorada": ("sea bream", "дорада"),
    "dorblu": ("Dorblu", "дорблю"),
    "elder": ("elder", "бузина"),
    "exotic": ("exotic", "экзотический"),
    "flower": ("flower", "цветок"),
    "frișcă": ("cream", "сливки"),
    "gin": ("gin", "джин"),
    "grapefruit": ("grapefruit", "грейпфрут"),
    "înghețată": ("ice cream", "мороженое"),
    "kahlua": ("Kahlúa", "Калуа"),
    "ketchup": ("ketchup", "кетчуп"),
    "kiwi": ("kiwi", "киви"),
    "lactată": ("dairy", "молочный"),
    "lime": ("lime", "лайм"),
    "liqueur": ("liqueur", "ликёр"),
    "malibu": ("Malibu", "Малибу"),
    "marinată": ("marinated", "маринованная"),
    "martini": ("Martini", "Мартини"),
    "mascarpone": ("mascarpone", "маскарпоне"),
    "mojito": ("Mojito", "Мохито"),
    "mozzarella": ("mozzarella", "моцарелла"),
    "muștar": ("mustard", "горчица"),
    "oregano": ("oregano", "орегано"),
    "orez": ("rice", "рис"),
    "oyster": ("oyster", "устричный"),
    "peach": ("peach", "персик"),
    "pesto": ("pesto", "песто"),
    "pisang": ("Pisang", "Пизанг"),
    "pișcot": ("ladyfinger biscuit", "печенье савоярди"),
    "prosciutto": ("prosciutto", "прошутто"),
    "roșu": ("red", "красное"),
    "rucola": ("arugula", "руккола"),
    "salati": ("salads", "салаты"),
    "sec": ("dry", "сухое"),
    "sirop": ("syrup", "сироп"),
    "snacksuri": ("snacks", "закуски"),
    "snackuri": ("snacks", "закуски"),
    "sortiment": ("assorted", "ассорти"),
    "spaghetti": ("spaghetti", "спагетти"),
    "sprite": ("Sprite", "Спрайт"),
    "spumant": ("sparkling wine", "игристое вино"),
    "stafide": ("raisins", "изюм"),
    "steak": ("steak", "стейк"),
    "sudjuk": ("sujuk", "суджук"),
    "susan": ("sesame", "кунжут"),
    "tagliatelle": ("tagliatelle", "тальятелле"),
    "tar": ("tartar", "тартар"),
    "tartar": ("tartar", "тартар"),
    "tequila": ("tequila", "текила"),
    "toast": ("toast", "тост"),
    "triple": ("triple", "трипл"),
    "urechi": ("ears", "уши"),
    "verdeață": ("herbs", "зелень"),
    "vin": ("wine", "вино"),
    "whisky": ("whisky", "виски"),
    "wraps": ("wraps", "лепёшки"),
    "cascaval": ("cheese", "сыр"),
    "carne": ("meat", "мясо"),
    "caesar": ("Caesar", "«Цезарь»"),
}

ALLERGEN_LABELS = {
    "gluten": {"en": "Gluten", "ro": "Gluten", "ru": "Глютен"},
    "dairy": {"en": "Milk", "ro": "Lapte", "ru": "Молоко"},
    "eggs": {"en": "Eggs", "ro": "Ouă", "ru": "Яйца"},
    "peanuts": {"en": "Peanuts", "ro": "Arahide", "ru": "Арахис"},
    "tree_nuts": {"en": "Tree nuts", "ro": "Fructe cu coajă lemnoasă", "ru": "Орехи"},
    "fish": {"en": "Fish", "ro": "Pește", "ru": "Рыба"},
    "crustaceans": {"en": "Crustaceans", "ro": "Crustacee", "ru": "Ракообразные"},
    "molluscs": {"en": "Molluscs", "ro": "Moluște", "ru": "Моллюски"},
    "soy": {"en": "Soy", "ro": "Soia", "ru": "Соя"},
    "sesame": {"en": "Sesame", "ro": "Susan", "ru": "Кунжут"},
    "mustard": {"en": "Mustard", "ro": "Muștar", "ru": "Горчица"},
    "celery": {"en": "Celery", "ro": "Țelină", "ru": "Сельдерей"},
}

ALLERGEN_PATTERNS = {
    "gluten": r"\b(?:făină(?!\s+de\s+porumb)|pâine|toast|aluat|pesmeți|pesmet|couscous|spaghetti|tagliatelle|paste|tăiței|biscuiți|chiflă|wraps|cereale|bread|flour|breadcrumbs|noodles|bun|wheat)\b",
    "dairy": r"\b(?:brânză|cașcaval|frișcă|smântână|unt|lapte|iaurt|înghețată|grăsime lactată|parmezan|mozzarella|camembert|dorblu|feta|mascarpone|cheese|cream|butter|milk|yogurt|dairy)\b",
    "eggs": r"\b(?:ou(?:ă)?|ou fiert|maioneză|sos\s+(?:tar[- ]?tar|caesar)|eggs?|mayonnaise)\b",
    "peanuts": r"\b(?:arahide|peanuts?)\b",
    "tree_nuts": r"\b(?:nuci|nucă|alune|miez de nucă|nuts?|hazelnuts?)\b",
    "fish": r"\b(?:pește|scrumbie|somon|crap|dorada|fish|salmon|herring|carp)\b",
    "crustaceans": r"\b(?:creveți|shrimp|prawns?|crab|crabs|lobster)\b",
    "molluscs": r"\b(?:oyster|stridii|midii|scoici|calamar|squid|mussels?)\b",
    "soy": r"\b(?:soia|soy)\b",
    "sesame": r"\b(?:susan|sesame)\b",
    "mustard": r"\b(?:muștar|mustard)\b",
    "celery": r"\b(?:țelină|celery)\b",
}

ALLERGEN_STATUS = {
    "none": {
        "en": "No common allergens identified in the listed ingredients.",
        "ro": "Nu au fost identificați alergeni comuni în ingredientele indicate.",
        "ru": "В указанных ингредиентах распространённые аллергены не выявлены.",
    },
    "missing": {
        "en": "Ingredients are not listed in the source menu.",
        "ro": "Ingredientele nu sunt indicate în meniul-sursă.",
        "ru": "Состав не указан в исходном меню.",
    },
}

PORTION = re.compile(r"^(?:\d+(?:[.,]\d+)?(?:/\d+(?:[.,]\d+)?)?\s*(?:gr|g|kg|ml|l|buc)|\d+\s*buc)$", re.I)
PRICE = re.compile(r"^(\d+(?:[.,]\d+)?(?:/\d+(?:[.,]\d+)?)?)\s+lei\b", re.I)


def translate_name(value, language):
    exact = NAME_EXACT.get(value.casefold())
    if exact:
        return exact[0 if language == "en" else 1]
    result = value
    phrases = NAME_PHRASES[language]
    phrase_replacements = {}
    for source in sorted(phrases, key=len, reverse=True):
        placeholder = f"ZZPHRASE{len(phrase_replacements)}ZZ"
        result, count = re.subn(
            rf"(?<!\w){re.escape(source)}(?!\w)", placeholder, result, flags=re.IGNORECASE
        )
        if count:
            phrase_replacements[placeholder] = phrases[source]

    words = NAME_WORDS[language]
    for source in sorted(words, key=len, reverse=True):
        result = re.sub(
            rf"(?<![\w]){re.escape(source)}(?![\w])",
            words[source],
            result,
            flags=re.IGNORECASE,
        )
    result = re.sub(r"\s+", " ", result).strip(" ,.-")
    for placeholder, translation in phrase_replacements.items():
        result = result.replace(placeholder, translation)
    if language == "en":
        result = re.sub(r"\b(\d+) ani\b", r"\1 years", result, flags=re.I)
    elif language == "ru":
        result = re.sub(r"\b(\d+) ani\b", r"\1 лет", result, flags=re.I)
    if language == "en":
        result = result.replace("„", "“")
    elif language == "ru":
        result = result.replace("„", "«").replace("”", "»")
    result = re.sub(r"\s+", " ", result).strip(" ,.-")
    return result[:1].upper() + result[1:]


def translate_description(value, language):
    language_index = 0 if language == "en" else 1
    result = value
    replacements = {}
    for source in sorted(DESCRIPTION_PHRASES, key=len, reverse=True):
        placeholder = f"ZZINGREDIENT{len(replacements)}ZZ"
        result, count = re.subn(
            rf"(?<!\w){re.escape(source)}(?!\w)", placeholder, result, flags=re.IGNORECASE
        )
        if count:
            replacements[placeholder] = DESCRIPTION_PHRASES[source][language_index]

    for source in sorted(DESCRIPTION_WORDS, key=len, reverse=True):
        result = re.sub(
            rf"(?<![\w]){re.escape(source)}(?![\w])",
            DESCRIPTION_WORDS[source][language_index],
            result,
            flags=re.IGNORECASE,
        )
    result = re.sub(r"\s+", " ", result).strip()
    for placeholder, translation in replacements.items():
        result = result.replace(placeholder, translation)
    result = re.sub(r"\s+", " ", result).strip()
    return result[:1].upper() + result[1:]


def infer_allergens(description):
    if not description:
        return ALLERGEN_STATUS["missing"]

    description = re.sub(r"\b(?:vișină înghețată|unt de cacao)\b", "", description, flags=re.I)
    found = [
        allergen_id
        for allergen_id, pattern in ALLERGEN_PATTERNS.items()
        if re.search(pattern, description, flags=re.IGNORECASE)
    ]
    if not found:
        return ALLERGEN_STATUS["none"]
    return {
        language: [ALLERGEN_LABELS[allergen_id][language] for allergen_id in found]
        for language in ("en", "ro", "ru")
    }


def category_for(section_number):
    for category_id, category in CATEGORIES.items():
        if section_number in category["sections"]:
            return category_id, category
    raise ValueError(f"No category configured for source section {section_number}")


def slug(value):
    normalized = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode("ascii")
    return re.sub(r"[^a-z0-9]+", "-", normalized.lower()).strip("-") or "item"


def parse_item(line, section_number, subgroup, index):
    raw = line[2:].replace("Miere ���", "Miere").replace("�", "")
    parts = [part.strip() for part in raw.split(" — ")]
    portion_index = None
    portion = None
    name_prefix = None
    uncertain = "de verificat" in raw.lower()
    for i in range(1, len(parts) - 1):
        match = re.search(
            r"(\d+(?:[.,]\d+)?(?:/\d+(?:[.,]\d+)?)?\s*(?:gr|g|kg|ml|l|buc))(?:\s*\(de verificat\))?$",
            parts[i],
            re.I,
        )
        if match:
            portion_index = i
            portion = match.group(1)
            if "captura sugerează" in parts[i].lower():
                name_prefix = " — ".join(parts[:i]).strip()
            break
    if portion_index is None and parts:
        match = re.match(
            r"^(.*?)(\d+(?:[.,]\d+)?(?:/\d+(?:[.,]\d+)?)?\s*(?:gr|g|kg|ml|l|buc))(?:\s*\(de verificat\))?$",
            parts[0],
            re.I,
        )
        if match and len(parts) > 1:
            name_prefix = match.group(1).strip()
            parts.insert(1, match.group(2).strip())
            portion_index = 1
            portion = match.group(2).strip()
    if portion_index is None:
        return None

    price_match = PRICE.match(parts[portion_index + 1])
    if not price_match:
        return None

    name = name_prefix or " — ".join(parts[:portion_index]).strip()
    portion = portion or parts[portion_index]
    price = price_match.group(1)
    remainder = parts[portion_index + 1][price_match.end():].strip()
    description = " — ".join(([remainder] if remainder else []) + parts[portion_index + 2:]).strip()
    description = re.sub(r"^(?:\.\s*|\s*\.\s*)", "", description).strip()
    description = re.sub(r"\s*\([^)]*de verificat[^)]*\)\.?", "", description, flags=re.I)

    translations = {
        "ro": re.sub(r"\bpăstări\b", "păstăi", name, flags=re.I),
        "en": translate_name(name, "en"),
        "ru": translate_name(name, "ru"),
    }
    if section_number == 4 and subgroup.casefold() == "plăcinte":
        translations["ru"] = PLACINTA_NAMES_RU[index]
    item = {
        "id": f"{section_number}-{index}-{slug(name)}",
        "name": translations,
        "portion": portion,
        "price": price,
    }
    if description:
        romanian_description = re.sub(r"\bpăstări\b", "păstăi", description, flags=re.I)
        romanian_description = re.sub(r"\bfide de orez\b", "fidea de orez", romanian_description, flags=re.I)
        item["description"] = {
            "en": translate_description(description, "en"),
            "ro": romanian_description,
            "ru": translate_description(description, "ru"),
        }
    item["allergens"] = infer_allergens(description)
    if subgroup:
        item["section"] = {
            "en": translate_name(subgroup, "en"),
            "ro": subgroup,
            "ru": translate_name(subgroup, "ru"),
        }
    else:
        item["section"] = SOURCE_SECTION_NAMES[section_number]
    if "Retroping pane" in name:
        item["badge"] = {"en": "Name to verify", "ro": "Denumire de verificat", "ru": "Название уточняется"}
    if uncertain:
        item["badge"] = {
            "en": "Details to verify",
            "ro": "Detalii de verificat",
            "ru": "Данные требуют проверки",
        }
    return item


def attach_images(items, image_directory=IMAGE_DIRECTORY, root=ROOT):
    items_by_id = {item["id"]: item for item in items}
    seen = set()

    for path in image_directory.iterdir():
        if path.name.startswith(".") or path.name == "README.md":
            continue
        if path.is_dir():
            continue
        if not path.is_file() or path.suffix.casefold() not in IMAGE_EXTENSIONS:
            raise ValueError(f"Unsupported file in dish image directory: {path.name}")
        if path.stem not in items_by_id:
            raise ValueError(f"Image filename must match a menu item ID: {path.name}")
        if path.stem in seen:
            raise ValueError(f"Multiple images found for menu item: {path.stem}")
        seen.add(path.stem)
        items_by_id[path.stem]["image"] = path.relative_to(root).as_posix()


def main():
    categories = {
        category_id: {"id": category_id, "name": category["name"], "items": []}
        for category_id, category in CATEGORIES.items()
    }
    section_number = None
    subgroup = ""
    section_item_index = 0
    for line in SOURCE.read_text(encoding="utf-8").splitlines():
        heading = re.match(r"^(\d+)\. (.+)$", line)
        if heading:
            number = int(heading.group(1))
            section_number = number if number in range(1, 23) else None
            subgroup = ""
            section_item_index = 0
            continue
        if not section_number:
            continue
        if line.startswith("- "):
            item = parse_item(line, section_number, subgroup, section_item_index + 1)
            if item:
                category_id, _ = category_for(section_number)
                categories[category_id]["items"].append(item)
                section_item_index += 1
            continue
        text = line.strip()
        if text and not text.startswith(("Sursa:", "Monedă:", "Scop:", "STRUCTURĂ", "LISTA", "OBSERVAȚII")):
            subgroup = text.rstrip(":")

    items = [item for category in categories.values() for item in category["items"]]
    attach_images(items)

    output = {"currency": "MDL", "categories": list(categories.values())}
    OUTPUT.write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {sum(len(category['items']) for category in output['categories'])} menu items across {len(output['categories'])} categories.")


if __name__ == "__main__":
    main()
