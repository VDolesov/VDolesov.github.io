import io
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
V1 = os.path.join(os.path.dirname(HERE), "v1")
CONTACT = ("Елена Михайловна Сидорова", "info@mirsladostey64.ru", "+7 (8452) 47-35-69", "+78452473569")

COMMON_REQUIREMENTS = [
    "знание и соблюдение санитарных норм",
    "добросовестное выполнение должностных обязанностей",
    "медицинская книжка или готовность оформить её в первый месяц работы",
]
COMMON_TERMS = [
    "стабильная выплата зарплаты два раза в месяц",
    "официальное трудоустройство по ТК РФ",
    "бесплатное питание для сотрудников",
    "дружный коллектив",
]

VACANCIES = [
    {
        "title": "Наборщик готовой продукции",
        "meta": "Ночная смена · график 5/2 с 20:00 до 6:00",
        "salary": "от 25 000 ₽",
        "intro": "На склад готовой продукции требуется наборщик.",
        "duties": ["набор готовой продукции по накладным и отправка её в торговую сеть",
                   "контроль качества готовой продукции и упаковки",
                   "соблюдение технологических инструкций"],
        "requirements": ["опыт работы не важен"] + COMMON_REQUIREMENTS,
        "terms": ["график работы 5/2 с 20:00 до 6:00"] + COMMON_TERMS,
    },
    {
        "title": "Кондитер в слоечный цех",
        "meta": "Ночная смена · график 5/2 с 18:00 до 5:00",
        "salary": "35 000 ₽",
        "intro": "Приглашаем на работу кондитера слоечного цеха.",
        "duties": ["изготовление слоёных изделий по технологическим картам на современном оборудовании",
                   "контроль качества сырья, полуфабрикатов и готовой продукции",
                   "соблюдение технологических инструкций"],
        "requirements": ["опыт работы не менее одного года"] + COMMON_REQUIREMENTS,
        "terms": ["график работы 5/2 с 18:00 до 5:00"] + COMMON_TERMS,
    },
    {
        "title": "Повар-универсал",
        "meta": "Ночная смена · график 5/2 с 18:00 до 5:00",
        "salary": "37 000 ₽",
        "intro": "Приглашаем на работу повара в ночную смену.",
        "duties": ["изготовление горячих блюд по технологическим картам",
                   "контроль качества сырья, полуфабрикатов и готовой продукции",
                   "соблюдение технологических инструкций"],
        "requirements": ["опыт работы не менее одного года"] + COMMON_REQUIREMENTS,
        "terms": ["график работы 5/2 с 18:00 до 5:00"] + COMMON_TERMS,
    },
]


def items(values):
    return "".join(f"<li>{v}</li>" for v in values)


def vacancy(i, v):
    subject = f"Резюме: {v['title']}"
    return f'''        <article class="vacancy reveal">
          <div class="vacancy__head">
            <span class="vacancy__index">{i:02d}</span>
            <div>
              <h3>{v["title"]}</h3>
              <p>{v["meta"]}</p>
            </div>
            <strong>{v["salary"]}</strong>
          </div>
          <details class="vacancy__details">
            <summary>Обязанности, требования, условия<span aria-hidden="true"></span></summary>
            <div class="vacancy__body">
              <p>{v["intro"]}</p>
              <h4>Обязанности</h4><ul>{items(v["duties"])}</ul>
              <h4>Требования</h4><ul>{items(v["requirements"])}</ul>
              <h4>Условия</h4><ul>{items(v["terms"])}</ul>
            </div>
          </details>
          <a class="button button--outline vacancy__apply" href="mailto:{CONTACT[1]}?subject={subject}">Отправить резюме</a>
        </article>'''


MAIN = f'''<main id="main">
    <section class="page-hero" id="top">
      <div class="page-hero__media" aria-hidden="true"></div>
      <div class="page-hero__shade" aria-hidden="true"></div>
      <div class="shell">
        <nav class="breadcrumbs" aria-label="Хлебные крошки"><a href="/v1/">Главная</a><span aria-hidden="true">/</span><span>Вакансии</span></nav>
        <p class="eyebrow page-hero__eyebrow">Работа у нас</p>
        <h1>Наша<br><em>команда</em></h1>
        <p class="page-hero__lead">Мы рады видеть в команде инициативных и вовлечённых сотрудников. Официальное трудоустройство, стабильная зарплата два раза в месяц, бесплатное питание.</p>
      </div>
    </section>

    <section class="vacancies" aria-labelledby="vacanciesTitle">
      <div class="shell">
        <div class="vacancies__head reveal">
          <div>
            <p class="eyebrow">Открытые вакансии</p>
            <h2 id="vacanciesTitle">Три<br><em>позиции</em></h2>
          </div>
          <p class="vacancies__contact">Контактное лицо — {CONTACT[0]}.<br>Резюме принимаем на <a href="mailto:{CONTACT[1]}">{CONTACT[1]}</a>, вопросы — по телефону <a href="tel:{CONTACT[3]}">{CONTACT[2]}</a>.</p>
        </div>
        <div class="vacancy-list">
{chr(10).join(vacancy(i + 1, v) for i, v in enumerate(VACANCIES))}
        </div>
      </div>
    </section>
  </main>'''

DESCRIPTION = "Открытые вакансии кондитерской «Мир сладостей» в Саратове: наборщик готовой продукции, кондитер, повар. Официальное трудоустройство, бесплатное питание."


def main():
    template = io.open(os.path.join(V1, "contacts", "index.html"), encoding="utf-8").read()
    html = re.sub(r"<main id=\"main\">.*?</main>", lambda m: MAIN, template, count=1, flags=re.S)
    html = re.sub(r'<meta name="description" content="[^"]*">', f'<meta name="description" content="{DESCRIPTION}">', html)
    html = re.sub(r'<meta property="og:description" content="[^"]*">', f'<meta property="og:description" content="{DESCRIPTION}">', html)
    html = html.replace('<meta property="og:title" content="Контакты — Мир сладостей">', '<meta property="og:title" content="Вакансии — Мир сладостей">')
    html = html.replace("<title>Контакты — Мир сладостей</title>", "<title>Вакансии — Мир сладостей</title>")
    html = html.replace('<a href="/v1/contacts/" class="is-active">Контакты</a>', '<a href="/v1/contacts/">Контакты</a>')
    html = html.replace('<link rel="canonical" href="https://mirsladostey164.ru/contacts/">', '<link rel="canonical" href="https://mirsladostey164.ru/company/vacancy/">')
    folder = os.path.join(V1, "vacancies")
    os.makedirs(folder, exist_ok=True)
    io.open(os.path.join(folder, "index.html"), "w", encoding="utf-8", newline="\n").write(html)
    print("v1/vacancies/index.html written")


if __name__ == "__main__":
    main()
