import re

EXTRA = [
    {"id": "801", "section": "pirogi", "name": "Осетинский пирог с мясом", "price": 890,
     "unit": "шт", "article": "10801", "badges": ["Новинка"],
     "weight": "1000 г", "composition": "Мука пшеничная в/с, вода, дрожжи, соль, говядина, лук репчатый, специи",
     "energy": "", "nutrition": "",
     "note": "Традиционный фыдджын: тонкое тесто и сочная начинка из рубленого мяса с луком."},
    {"id": "802", "section": "pirogi", "name": "Осетинский пирог с картофелем и сыром", "price": 690,
     "unit": "шт", "article": "10802", "badges": [],
     "weight": "1000 г", "composition": "Мука пшеничная в/с, вода, дрожжи, соль, картофель, сыр, масло сливочное",
     "energy": "", "nutrition": "",
     "note": "Картофджын с мягким картофелем и сыром — сливочный и сытный."},
    {"id": "803", "section": "pirogi", "name": "Осетинский пирог с зеленью и сыром", "price": 720,
     "unit": "шт", "article": "10803", "badges": ["Сезонный"],
     "weight": "1000 г", "composition": "Мука пшеничная в/с, вода, дрожжи, соль, зелень, сыр",
     "energy": "", "nutrition": "",
     "note": "Цахараджын со свежей зеленью и сыром — яркий аромат и тонкая румяная корочка."},
]

TYPE_BY_SECTION = {
    "torty": "Торт", "salaty": "Салат", "pechene": "Печенье",
}


def pretty(name, section):
    PREPOSITIONS = ("с ", "со ", "из ", "по ", "в ", "на ")
    name = name.strip().strip('"').strip()

    m = re.match(r'^(Торт|Салат|Десерт|Печенье|Пирог)\s+"?(.+?)"?$', name, re.I)
    prefix, core = (m.group(1), m.group(2)) if m else ("", name)

    if core.isupper():
        core = core.capitalize()
    if not prefix:
        prefix = TYPE_BY_SECTION.get(section, "")

    if not prefix:
        return core
    prefix = prefix.capitalize()

    if core.lower().startswith(PREPOSITIONS):
        return f"{prefix} {core[0].lower() + core[1:]}"
    if core.lower().startswith(prefix.lower()):
        return core
    return f"{prefix} «{core}»"
