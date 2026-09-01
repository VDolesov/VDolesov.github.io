/* Данные каталога «Мир сладостей».
   Собрано автоматически: build/data.py из build/catalog.json.
   Разделы и адреса повторяют структуру mirsladostey164.ru. */
(() => {
  "use strict";

  const SECTIONS = [
    { slug: "torty", title: "Торты", short: "Торты", description: "Праздничный торт собственного производства: мягкие коржи, крем и сбалансированная сладость." },
    { slug: "pirogi", title: "Пироги", short: "Пироги", description: "Домашний пирог с щедрой начинкой и румяным тестом — для семейного стола, офиса и праздника." },
    { slug: "vypechka", title: "Выпечка", short: "Выпечка", description: "Свежая выпечка из слоёного теста — хрустящая снаружи и сочная внутри." },
    { slug: "pirozhnye_i_deserty", title: "Пирожные и десерты", short: "Десерты", description: "Порционный десерт с выразительной текстурой и аккуратной подачей." },
    { slug: "pechene", title: "Печенье", short: "Печенье", description: "Печенье собственной выпечки — к чаю, кофе и в подарочный набор." },
    { slug: "salaty", title: "Салаты", short: "Салаты", description: "Готовый салат для домашнего обеда или праздничного стола. Небольшие партии." },
    { slug: "vtorye_blyuda", title: "Вторые блюда", short: "Горячее", description: "Горячее блюдо собственного производства. Остаётся разогреть и подать к столу." },
    { slug: "polufabrikaty", title: "Полуфабрикаты", short: "Полуфабрикаты", description: "Домашние полуфабрикаты для быстрого ужина — удобно хранить и легко приготовить." },
    { slug: "napitki", title: "Напитки", short: "Напитки", description: "Фруктово-ягодный напиток в удобном формате — к выпечке, обеду или празднику." },
  ];

  const PRODUCTS = [
    {
      id: "747", section: "torty",
      name: "Торт «Прага»",
      price: 1300, unit: "шт",
      article: "10007", badge: "Хит",
      weight: "1200 г",
      composition: "Мука пшеничная в/с, сахар-песок, яйцо куриное, масло сливочное, молоко цельное сгущенное, какао-порошок, глазурь кондитерская шоколадная, ванилин",
      energy: "391,55 ккал / 1369 кДж", nutrition: "Белков 6,0 г, жиров 20,77 г, углеводов 45,96 г",
      note: "",
      image: "/assets/products/747-v7.webp"
    },
    {
      id: "748", section: "torty",
      name: "Торт «Сластёна»",
      price: 920, unit: "шт",
      article: "10006", badge: "",
      weight: "1000 г",
      composition: "Мука пшеничная в/с, сахар-песок, яйцо куриное, масло сливочное, сливки растительные, молоко цельное сгущенное, орех грецкий, какао-порошок, ванилин, краситель пищевой",
      energy: "435,2 ккал / 1822 лДж", nutrition: "Белков 8,8 г, жиров 21,9 г, углеводов 54,8 г",
      note: "",
      image: "/assets/products/748-v7.webp"
    },
    {
      id: "749", section: "torty",
      name: "Торт «Шварцвальдский»",
      price: 880, unit: "шт",
      article: "10005", badge: "",
      weight: "1000 г",
      composition: "Мука пшеничная в/с, сахар-песок, яйцо куриное, сливки растительные, молоко цельное сгущенное, вишня свежая, какао-порошок, ароматизатор идентичный натуральному, краситель пищевой",
      energy: "259 ккал / 1084 кДж", nutrition: "Белков 4 г, жиров 12 г, углеводы 43 г",
      note: "",
      image: "/assets/products/749-v7.webp"
    },
    {
      id: "751", section: "torty",
      name: "Торт «Экзотика с ананасом»",
      price: 880, unit: "шт",
      article: "10003", badge: "Хит",
      weight: "1000 г",
      composition: "Мука пшеничная в/с, сахар-песок, яйцо куриное, масло сливочное, сливки растительные, молоко цельное сгущенное, ананас консервированный, киви, ванилин, краситель пищевой",
      energy: "253 ккал / 1059 кДж", nutrition: "Белков 7,1 г, жиров 11 г, углеводов 28 г",
      note: "",
      image: "/assets/products/751-v7.webp"
    },
    {
      id: "752", section: "torty",
      name: "Торт «Клубничный рай»",
      price: 880, unit: "шт",
      article: "10002", badge: "Хит",
      weight: "1000 г",
      composition: "Мука пшеничная в/с, сахар-песок, яйцо куриное, сливки растительные, молоко цельное сгущенное, клубника свежая, ванилин, краситель пищевой",
      energy: "276 ккал / 1155 кДж", nutrition: "Белков 5,1 г, жиров 10,5 г, углеводов 34 г",
      note: "",
      image: "/assets/products/752-v7.webp"
    },
    {
      id: "777", section: "torty",
      name: "Торт «Медово-ореховый»",
      price: 880, unit: "шт",
      article: "10001", badge: "",
      weight: "1000 г",
      composition: "Мука пшеничная в/с, сахар-песок, яйцо куриное, мёд, масло сливочное, сливки растительные, молоко цельное сгущенное, орех грецкий, ванилин, краситель пищевой",
      energy: "460 ккал / 1928 кДж", nutrition: "Белков 3,3 г, жиров 23,8 г, углеводов 58,7 г",
      note: "",
      image: "/assets/products/777-v7.webp"
    },
    {
      id: "736", section: "pirogi",
      name: "Пирог с мясом",
      price: 780, unit: "кг",
      article: "20002", badge: "",
      weight: "1000 г",
      composition: "Мука пшеничная в/с, сахар, маргарин, соль, масло растительное, дрожжи, говядина, свинина, лук",
      energy: "274,8 ккал / 1150 кДж", nutrition: "Белков 11,9 г, жиров 12,3 г, углеводов 33,9 г",
      note: "",
      image: "/assets/products/736-v7.webp"
    },
    {
      id: "737", section: "pirogi",
      name: "Пирог с вишней",
      price: 700, unit: "кг",
      article: "20001", badge: "",
      weight: "1000 г",
      composition: "Мука пшеничная в/с, сахар, яйцо, маргарин, соль, вода, дрожжи, вишня свежая",
      energy: "313,9 ккал / 1314 кДж", nutrition: "Белков 2,9 г, жиров 20,7 г, углеводов 31 г",
      note: "",
      image: "/assets/products/737-v7.webp"
    },
    {
      id: "738", section: "pirogi",
      name: "Пирог с капустой и рыбой",
      price: 570, unit: "кг",
      article: "20006", badge: "",
      weight: "1000 г",
      composition: "Мука пшеничная в/с, сахар, маргарин, соль, масло растительное, дрожжи, капуста, рыба консервированная",
      energy: "296,49 ккал / 1241 кДж", nutrition: "Белков 12,6 г, жиров 10,6 г, углеводов 37,4 г",
      note: "",
      image: "/assets/products/738-v7.webp"
    },
    {
      id: "739", section: "pirogi",
      name: "Пирог с капустой и грибами",
      price: 570, unit: "кг",
      article: "20003", badge: "",
      weight: "1000 г",
      composition: "Мука пшеничная в/с, сахар, маргарин, соль, масло подсолнечное, дрожжи, капуста, грибы шампиньоны",
      energy: "190,4 ккал / 797 кДж", nutrition: "Белков 4,5 г, жиров 6,6 г, углеводов 37,4 г",
      note: "",
      image: "/assets/products/739-v7.webp"
    },
    {
      id: "741", section: "pirogi",
      name: "Пирог с луком и яйцом",
      price: 570, unit: "кг",
      article: "20008", badge: "",
      weight: "1000 г",
      composition: "Мука пшеничная в/с, сахар, маргарин, соль, масло подсолнечное, дрожжи, лук зелёный",
      energy: "172 ккал / 719 кДж", nutrition: "Белков 8,9 г, жиров 6,4 г, углеводов 21,7 г",
      note: "",
      image: "/assets/products/741-v7.webp"
    },
    {
      id: "772", section: "pirogi",
      name: "Пирог с курагой и повидлом",
      price: 570, unit: "кг",
      article: "20007", badge: "",
      weight: "1000 г",
      composition: "Мука пшеничная в/с, сахар, яйцо, маргарин, соль, вода, дрожжи, курага, повидло яблочное",
      energy: "287 ккал / 1204 кДж", nutrition: "Белков 5,3 г, жиров 5,5 г, углеводов 48,2 г",
      note: "",
      image: "/assets/products/772-v7.webp"
    },
    {
      id: "773", section: "pirogi",
      name: "Пирог с белой рыбой",
      price: 700, unit: "кг",
      article: "20004", badge: "",
      weight: "1000 г",
      composition: "Мука пшеничная в/с, сахар, маргарин, соль, масло подсолнечное, дрожжи, белая рыба, морковь, лук репчатый",
      energy: "239,66 ккал / 1003 кДж", nutrition: "Белков 12,27 г, жиров 12,18 г, углеводов 25,87 г",
      note: "",
      image: "/assets/products/773-v7.webp"
    },
    {
      id: "774", section: "pirogi",
      name: "Пирог с капустой и яйцом",
      price: 570, unit: "кг",
      article: "20009", badge: "",
      weight: "1000 г",
      composition: "Мука пшеничная в/с, сахар, маргарин, соль, масло подсолнечное, дрожжи, капуста",
      energy: "181,02 ккал / 757 кДж", nutrition: "Белков 5,3 г, жиров 7,7 г, углеводов 23 г",
      note: "",
      image: "/assets/products/774-v7.webp"
    },
    {
      id: "775", section: "pirogi",
      name: "Кух бисквитный",
      price: 580, unit: "кг",
      article: "20005", badge: "",
      weight: "1000 г",
      composition: "Мука пшеничная в/с, сахар, яйцо, масло сливочное, маргарин, повидло яблочное",
      energy: "283 ккал / 1184 кДж", nutrition: "Белков 7,0 г, жиров 8,0 г, углеводов 45,0 г",
      note: "",
      image: "/assets/products/775-v7.webp"
    },
    {
      id: "776", section: "pirogi",
      name: "Каравай свадебный",
      price: 600, unit: "шт",
      article: "20010", badge: "",
      weight: "1200 г",
      composition: "Мука пшеничная в/с, сахар, яйцо, масло сливочное, маргарин, повидло яблочное",
      energy: "225,94 ккал / 945 кДж", nutrition: "Белков 7,8 г, жиров 1,4 г, углеводов 46,9 г",
      note: "",
      image: "/assets/products/776-v7.webp"
    },
    {
      id: "801", section: "pirogi",
      name: "Осетинский пирог с мясом",
      price: 890, unit: "шт",
      article: "10801", badge: "Новинка",
      weight: "1000 г",
      composition: "Мука пшеничная в/с, вода, дрожжи, соль, говядина, лук репчатый, специи",
      energy: "", nutrition: "",
      note: "Традиционный фыдджын: тонкое тесто и сочная начинка из рубленого мяса с луком.",
      image: "/assets/products/801-v7.webp"
    },
    {
      id: "802", section: "pirogi",
      name: "Осетинский пирог с картофелем и сыром",
      price: 690, unit: "шт",
      article: "10802", badge: "",
      weight: "1000 г",
      composition: "Мука пшеничная в/с, вода, дрожжи, соль, картофель, сыр, масло сливочное",
      energy: "", nutrition: "",
      note: "Картофджын с мягким картофелем и сыром — сливочный и сытный.",
      image: "/assets/products/802-v7.webp"
    },
    {
      id: "803", section: "pirogi",
      name: "Осетинский пирог с зеленью и сыром",
      price: 720, unit: "шт",
      article: "10803", badge: "Сезонный",
      weight: "1000 г",
      composition: "Мука пшеничная в/с, вода, дрожжи, соль, зелень, сыр",
      energy: "", nutrition: "",
      note: "Цахараджын со свежей зеленью и сыром — яркий аромат и тонкая румяная корочка.",
      image: "/assets/products/803-v7.webp"
    },
    {
      id: "742", section: "vypechka",
      name: "Слойка с ветчиной и сыром",
      price: 75, unit: "шт",
      article: "30001", badge: "",
      weight: "80 г",
      composition: "Мука пшеничная в/с, сахар, маргарин, дрожжи, соль, ветчина, сыр",
      energy: "372,6 ккал / 15559 кДж", nutrition: "Белков 11,22 г, жиров 24,62 г, углеводов 29,21 г",
      note: "",
      image: "/assets/products/742-v7.webp"
    },
    {
      id: "743", section: "vypechka",
      name: "Слойка с вишней",
      price: 75, unit: "шт",
      article: "30002", badge: "Хит",
      weight: "80 г",
      composition: "Мука пшеничная в/с, сахар, маргарин, дрожжи, соль, вишня свежая",
      energy: "352 ккал / 1473 кДж", nutrition: "Белков 7,21 г, жиров 15,49 г, углеводов 43,45 г",
      note: "",
      image: "/assets/products/743-v7.webp"
    },
    {
      id: "744", section: "vypechka",
      name: "Самса с курицей",
      price: 90, unit: "шт",
      article: "30006", badge: "",
      weight: "130 г",
      composition: "Мука пшеничная в/с, сахар, жир говяжий, дрожжи, соль, филе куриное, лук репчатый",
      energy: "309,57 ккал / 1295 кДж", nutrition: "Белков 11,40 г, жиров 21,18 г, углеводов 19,33 г",
      note: "",
      image: "/assets/products/744-v7.webp"
    },
    {
      id: "745", section: "vypechka",
      name: "Самса с сыром",
      price: 75, unit: "шт",
      article: "30003", badge: "",
      weight: "130 г",
      composition: "Мука пшеничная в/с, сахар, жир говяжий, дрожжи, соль, сыр, лук репчатый",
      energy: "309,57 ккал / 1295 кДж", nutrition: "Белков 11,40 г, жиров 21,18 г, углеводов 19,33 г",
      note: "",
      image: "/assets/products/745-v7.webp"
    },
    {
      id: "746", section: "vypechka",
      name: "Струдель с вишней",
      price: 550, unit: "кг",
      article: "30004", badge: "",
      weight: "",
      composition: "Мука пшеничная в/с, маргарин, сметана, молоко сухое, яйцо, сахар, джем вишневый, вишня свежая",
      energy: "238 кДж / 996 кДж", nutrition: "Белков 5,50 г, жиров 9,85 г, углеводов 34,29 г",
      note: "",
      image: "/assets/products/746-v7.webp"
    },
    {
      id: "780", section: "vypechka",
      name: "Струдель с лимоном",
      price: 550, unit: "кг",
      article: "30005", badge: "",
      weight: "",
      composition: "Мука пшеничная в/с, маргарин, сметана, молоко сухое, яйцо, сахар, лимон свежий",
      energy: "366,5 ккал / 1534 кДж", nutrition: "Белков 13,05 г, жиров 14,9 г, углеводов 48,5 г",
      note: "",
      image: "/assets/products/780-v7.webp"
    },
    {
      id: "756", section: "pirozhnye_i_deserty",
      name: "Зимняя вишня",
      price: 130, unit: "шт",
      article: "40001", badge: "",
      weight: "130 г",
      composition: "Мука в/с, сахар, яйцо, сыр творожный, сливки растительные, молоко сгущенное, вишня с/м, желатин, шоколад тёмный, шоколад белый",
      energy: "282 ккал / 1180 кДж", nutrition: "Белков 3,10 г, жиров 6,10 г, углеводов 55,5 г",
      note: "",
      image: "/assets/products/756-v7.webp"
    },
    {
      id: "757", section: "pirozhnye_i_deserty",
      name: "Соната",
      price: 130, unit: "шт",
      article: "40002", badge: "Хит",
      weight: "130 г",
      composition: "Мука в/с, сахар, яйцо, сыр творожный, сливки растительные, молоко сгущенное, малина с/м, желатин, шоколад белый, шоколад тёмный",
      energy: "316,6 ккал / 1325 кДж", nutrition: "Белков 5,43 г, жиров 14,57, углеводов 46,40 г",
      note: "",
      image: "/assets/products/757-v7.webp"
    },
    {
      id: "758", section: "pirozhnye_i_deserty",
      name: "Десерт «Графские развалины»",
      price: 130, unit: "шт",
      article: "40003", badge: "Хит",
      weight: "140 г",
      composition: "Мука в/с, сахар, яйцо, масло сливочное,молоко сгущенное вареное, чернослив",
      energy: "280,7 ккал / 1172,3 кДж", nutrition: "Белков 6,1 г, жиров 20,3 г, углеводов 20,,3 г",
      note: "",
      image: "/assets/products/758-v7.webp"
    },
    {
      id: "778", section: "pirozhnye_i_deserty",
      name: "Тирамису с малиной",
      price: 130, unit: "шт",
      article: "40005", badge: "",
      weight: "140 г",
      composition: "Мука в/с, сахар, яйцо, сливки, сироп сахарный, малина свежая, джем малиновый, кофе",
      energy: "312,6 ккал / 1308,79 кДж", nutrition: "Белков 4,7 г, жиров 15,4 г, углеводов 36,7 г",
      note: "",
      image: "/assets/products/778-v7.webp"
    },
    {
      id: "753", section: "pechene",
      name: "Печенье «Суворовское»",
      price: 340, unit: "кг",
      article: "50001", badge: "",
      weight: "",
      composition: "Мука в/с, сахар, яйцо, маргарин, ванилин, соль",
      energy: "510 ккал / 2135 кДж", nutrition: "Белков 6,1 г, жиров 30,3 г, углеводов 52,3 г",
      note: "",
      image: "/assets/products/753-v7.webp"
    },
    {
      id: "764", section: "salaty",
      name: "Салат «Сельдь под шубой»",
      price: 400, unit: "шт",
      article: "60002", badge: "",
      weight: "1000 г",
      composition: "Картофель,свёкла, яйцо, филе сельди с/с, морковь, майонез, лук репчатый",
      energy: "186,05 ккал / 778 кДж", nutrition: "Белков 6,0 г, жиров 15,14 г, углеводов 7,63 г",
      note: "",
      image: "/assets/products/764-v7.webp"
    },
    {
      id: "765", section: "salaty",
      name: "Салат «Русский»",
      price: 500, unit: "кг",
      article: "60003", badge: "",
      weight: "",
      composition: "Свекла, чернослив, чеснок, майонез",
      energy: "365,7 ккал / 1531,,1 кДж", nutrition: "Белков 18,7 г, жиров 25,3 г, углеводов 16,0 г",
      note: "",
      image: "/assets/products/765-v7.webp"
    },
    {
      id: "766", section: "salaty",
      name: "Салат «Винегрет»",
      price: 500, unit: "кг",
      article: "60004", badge: "",
      weight: "",
      composition: "Капуста квашеная, свёкла, картофель, огурцы соленые, морковь, зеленый горошек, масло подсолнечное, лук репчатый",
      energy: "133 ккал / 556,8 кДж", nutrition: "Белков 1,5 г, жиров 10,2 г, углеводов 9,0 г",
      note: "",
      image: "/assets/products/766-v7.webp"
    },
    {
      id: "768", section: "salaty",
      name: "Салат «Тбилиси»",
      price: 1000, unit: "кг",
      article: "60005", badge: "",
      weight: "",
      composition: "Говядина, лук репчатый, перец болгарский, фасоль консервированная, орех грецкий, кинза, масло растительное, чеснок",
      energy: "212 ккал / 887 кДж", nutrition: "Белков 11,6 г, жиров 15,7 г, углеводов 6,4 г",
      note: "",
      image: "/assets/products/768-v7.webp"
    },
    {
      id: "769", section: "salaty",
      name: "Салат «Аппетитный»",
      price: 950, unit: "кг",
      article: "60006", badge: "",
      weight: "",
      composition: "Филе куриное, орех грецкий, лук зеленый, майонез, виноград",
      energy: "149 ккал / 623 кДж", nutrition: "Белков 11,3 г, жиров 9,3 г, углеводов 5,2 г",
      note: "",
      image: "/assets/products/769-v7.webp"
    },
    {
      id: "770", section: "vtorye_blyuda",
      name: "Котлеты по-киевски",
      price: 130, unit: "шт",
      article: "70001", badge: "",
      weight: "120 г",
      composition: "Филе куриное, яйцо, масло подсолнечное, сухари панировочные, масло сливочное",
      energy: "290,7 ккал / 1217,1 кДж", nutrition: "Белков 17,9 г, жиров 23 г, углеводов 3,2 г",
      note: "",
      image: "/assets/products/770-v7.webp"
    },
    {
      id: "771", section: "vtorye_blyuda",
      name: "Люля рубленые",
      price: 1000, unit: "кг",
      article: "70002", badge: "",
      weight: "",
      composition: "Свинина, говядина, лук репчатый, специи, соль",
      energy: "245,55 ккал / 1027 кДж", nutrition: "Белков 14,22 г, жиров 19,32 г, углеводов 5,30 г",
      note: "",
      image: "/assets/products/771-v7.webp"
    },
    {
      id: "783", section: "vtorye_blyuda",
      name: "Пикша жареная",
      price: 1200, unit: "кг",
      article: "70003", badge: "",
      weight: "",
      composition: "Минтай, масло подсолнечное, соль",
      energy: "125,38 ккал / 524 кДж", nutrition: "Белков 15,38 г, жиров 6,58 г, углеводов 2,74 г",
      note: "",
      image: "/assets/products/783-v7.webp"
    },
    {
      id: "760", section: "polufabrikaty",
      name: "Пельмени",
      price: 390, unit: "шт",
      article: "80001", badge: "",
      weight: "600 г",
      composition: "Мука в/с, яйцо, говядина, свинина, лук репчатый, соль, перец черный",
      energy: "264,52 ккал / 1107 кДж", nutrition: "Белков 11,5 г, жиров 13,8 г, углеводов 25,8 г",
      note: "",
      image: "/assets/products/760-v7.webp"
    },
    {
      id: "761", section: "polufabrikaty",
      name: "Манты",
      price: 390, unit: "шт",
      article: "80002", badge: "",
      weight: "600 г",
      composition: "Мука в/с, яйцо, говядина, свинина, лук репчатый, соль, перец черный",
      energy: "265,52 ккал / 1107 кДж", nutrition: "Белков 11,5 г, жиров 13,8 г, углеводов 25,8 г",
      note: "",
      image: "/assets/products/761-v7.webp"
    },
    {
      id: "781", section: "polufabrikaty",
      name: "Вареники с картошкой",
      price: 130, unit: "шт",
      article: "80003", badge: "",
      weight: "600 г",
      composition: "Мука в/с, яйцо, картофель, лук репчатый, соль",
      energy: "177,51 ккал / 743 кДж", nutrition: "Белков 5,02 г, жиров 4,13 г, углеводов 30,78 г",
      note: "",
      image: "/assets/products/781-v7.webp"
    },
    {
      id: "782", section: "polufabrikaty",
      name: "Вареники с вишней",
      price: 210, unit: "шт",
      article: "80004", badge: "",
      weight: "600 г",
      composition: "Мука в/с, яйцо, вишня свежая, сахар",
      energy: "182,07 ккал / 762 кДж", nutrition: "Белков 4,47 г, жиров 2,80 г, углеводов 36,63 г",
      note: "",
      image: "/assets/products/782-v7.webp"
    },
    {
      id: "762", section: "napitki",
      name: "Компот фруктово-ягодный",
      price: 80, unit: "шт",
      article: "90002", badge: "",
      weight: "500 мл",
      composition: "Сухофрукты, сахар, вода питьевая",
      energy: "60 ккал / 261 кДж", nutrition: "Белков 0,8 г, жиров 0 г, углеводов 14,2 г",
      note: "",
      image: "/assets/products/762-v7.webp"
    },
    {
      id: "763", section: "napitki",
      name: "Морс клюквенный",
      price: 80, unit: "шт",
      article: "90001", badge: "",
      weight: "500 мл",
      composition: "Ягоды, сахар, вода питьевая",
      energy: "50 ккал / 251 кДж", nutrition: "Белков 0,8 г, жиров 0 г, углеводов 14,2 г",
      note: "",
      image: "/assets/products/763-v7.webp"
    },
  ];

  const SECTION_MAP = Object.fromEntries(SECTIONS.map(s => [s.slug, s]));
  PRODUCTS.forEach(p => {
    p.sectionTitle = SECTION_MAP[p.section].title;
    p.availability = ["torty", "pirogi"].includes(p.section)
      ? "Предзаказ от 24 часов" : "Наличие уточнит менеджер";
    p.description = p.note || SECTION_MAP[p.section].description;
    p.url = `/catalog/${p.section}/${p.id}/`;
  });

  window.MS_DATA = {
    SECTIONS, SECTION_MAP, PRODUCTS,
    FEATURED_IDS: ["801", "747", "749", "778", "746", "765"],
    MIN_ORDER: 800, FREE_DELIVERY: 3000, DELIVERY_FEE: 150
  };
})();
