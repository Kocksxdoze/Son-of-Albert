import sqlite3
import os

class PsychoKnowledge:
    def __init__(self, db_path: str = "storage/empasis.db"):
        # Создаем папку, если нет
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self.db_path = db_path
        self._init_db()

    def _get_connection(self) -> sqlite3.Connection:
        return sqlite3.connect(self.db_path)

    def _init_db(self):
        """Создает таблицу и наполняет её стартовыми знаниями."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # Таблица понятий
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS terms (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    keyword TEXT UNIQUE,
                    lang TEXT,
                    title TEXT,
                    explanation TEXT,
                    advice TEXT
                )
            """)

            # Всегда актуализируем проверенные карточки знаний
            self._seed_default_data(cursor)
            conn.commit()

    def _seed_default_data(self, cursor: sqlite3.Cursor):
        """База проверенных терминов и клинических методик детской психологии (RU, UZ, EN)."""
        terms = [
            # 1. Грызение ручек, предметов и ногтей (Оральный сенсорный стимминг / Онихофагия)
            (
                "грызет ручк", "ru",
                "Оральный стимминг и сенсорная саморегуляция (грызение ручек/карандашей/предметов)",
                "В детской нейропсихологии это не «каприз» и не «плохое воспитание». Это бессознательный способ сенсорной саморегуляции нервной системы:\n\n"
                "👶 1. Дошкольники и начальные классы (1-4 класс): Жевательные мышцы челюсти — мощнейший проприоцептивный рецептор. Когда ребенок концентрируется на письме или счете, его лобные доли быстро истощаются. Сжимая зубы и надкусывая ручку, мозг рефлекторно «догружает» кору импульсами для удержания фокуса. Это физиологическая потребность в мышечном тонусе.\n\n"
                "🧑 2. Подростки (5-11 класс): Чаще всего выступает соматическим клапаном сброса фоновой тревоги, перфекционизма (страх помарки в тетради) или скрытого раздражения.",
                "Практические методики помощи (без вреда для психики):\n\n"
                "✅ 1. Сенсорное замещение (дать безопасную альтернативу рту):\n"
                "• Насадки-грызунки на ручки из пищевого силикона (chewelry) — дают челюстям нужное мышечное сопротивление, но безопасны для эмали зубов и ЖКТ.\n"
                "• Бутылочка с водой с плотной тугой трубочкой или спортивным клапаном на парте. Питье воды мелкими глотками через усилие сосания мгновенно активирует парасимпатическую нервную систему и снимает спазм.\n"
                "• Твердые хрустящие перекусы (кусочки яблока, моркови) перед началом выполнения домашних заданий.\n\n"
                "✅ 2. Тактильная разгрузка для рук:\n"
                "• Пружинное массажное кольцо или шарик Су-Джок, тактильный эспандер, мялка-антистресс, чтобы пальцы совершали мышечную работу.\n\n"
                "✅ 3. Дифференциация по возрасту в общении:\n"
                "• С учениками младших классов бессмысленно вести логические беседы «зачем ты это делаешь» или требовать «взять себя в руки» — у них ещё не созрели зоны самоконтроля лобных долей. Помогает только спокойная сенсорная подмена (дать силиконовую насадку, дать попить через трубочку).\n"
                "• С подростком — спокойно понаблюдать за триггерами: перед какими именно уроками ручка идет в рот (страх двойки, конфликт, перегрузка).\n\n"
                "⛔ ЧЕГО ДЕЛАТЬ КАТЕГОРИЧЕСКИ НЕЛЬЗЯ:\n"
                "• Кричать, бить по рукам, выдергивать предмет изо рта.\n"
                "• Стыдить перед классом или семьей («ты уже взрослый, а ведешь себя как маленький!»).\n"
                "• Мазать ручки или пальцы горькими лаками/горчицей (это усиливает невротизацию и переводит тревогу в тики, энурез или навязчивое обкусывание ногтей до крови)."
            ),
            (
                "грызет карандаш", "ru",
                "Оральный стимминг и сенсорная саморегуляция (грызение ручек/карандашей/предметов)",
                "В детской нейропсихологии это не «каприз» и не «плохое воспитание». Это бессознательный способ сенсорной саморегуляции нервной системы:\n\n"
                "👶 1. Дошкольники и начальные классы (1-4 класс): Жевательные мышцы челюсти — мощнейший проприоцептивный рецептор. Когда ребенок концентрируется на письме или счете, его лобные доли быстро истощаются. Сжимая зубы и надкусывая ручку, мозг рефлекторно «догружает» кору импульсами для удержания фокуса.\n\n"
                "🧑 2. Подростки (5-11 класс): Соматический сброс фоновой тревоги и страха ошибки.",
                "Практические методики помощи:\n\n"
                "✅ 1. Сенсорное замещение: силиконовые насадки-грызунки (chewelry), питье воды через узкую тугую трубочку, твердые яблоки/морковь перед уроком.\n"
                "✅ 2. Тактильная разгрузка: кольцо или шарик Су-Джок, тактильный эспандер.\n"
                "✅ 3. Возрастной подход: с младшими — только мягкая сенсорная подмена без чтения нотаций; с подростками — поиск триггеров напряжения.\n"
                "⛔ КАТЕГОРИЧЕСКИ ЗАПРЕЩЕНО: стыдить, бить по рукам, мазать горьким."
            ),
            (
                "грызет ногт", "ru",
                "Онихофагия (навязчивое обкусывание ногтей и кутикулы)",
                "Онихофагия у детей и подростков — невротическая реакция на хронический стресс, завышенные ожидания окружающих, эмоциональное перенапряжение или внутренний запрет на проявление агрессии/протеста.",
                "Практические шаги помощи:\n\n"
                "✅ 1. Исключить наказания: ребенок делает это в моменты бессознательного транса. Окрики лишь усиливают стыд и тревогу.\n"
                "✅ 2. Тактильное переключение: дайте в руки массажное кольцо Су-Джок, тактильный брелок-антистресс или кусочек пластилина/жвачки для рук.\n"
                "✅ 3. Снижение учебного давления: обсудите с учителем и семьей, нет ли перегрузки кружками и завышенных требований к оценкам.\n"
                "✅ 4. Уход за руками: аккуратно подпиливать ногти, использовать заживляющие масла с приятным запахом (чтобы убрать заусенцы, провоцирующие обкусывание)."
            ),
            (
                "кусает ручк", "ru",
                "Оральный стимминг (привычка грызть и надкусывать предметы)",
                "Физиологический стимминг для стимуляции внимания коры головного мозга через жевательные рецепторы при умственной нагрузке.",
                "Рекомендации: используйте пищевые силиконовые насадки на ручки, воду через трубочку, массажеры Су-Джок для кистей. Ни в коем случае не стыдите ребенка."
            ),
            (
                "грызет предм", "ru",
                "Оральный стимминг (привычка тянуть и грызть предметы на уроках)",
                "Физиологический стимминг для стимуляции внимания коры головного мозга через жевательные рецепторы при умственной нагрузке.",
                "Рекомендации: используйте пищевые силиконовые насадки на ручки, воду через трубочку, массажеры Су-Джок для кистей. Ни в коем случае не стыдите ребенка."
            ),
            # 2. Страх ответа у доски
            (
                "боится доски", "ru",
                "Школьная тревожность и страх ответа у доски",
                "Один из самых распространенных детских страхов. У ребенка блокируется оперативная память из-за резкого выброса адреналина и кортизола: дома он знал материал на 5, но у доски перед классом наступает ступор («белый лист»).",
                "Рекомендации учителям и родителям:\n\n"
                "✅ 1. Первые разы опрашивать с места или в паре с одноклассником, пока ребенок не почувствует безопасность.\n"
                "✅ 2. Никогда не вызывать к доске в карательных целях («Ага, отвлекаешься — иди к доске!»).\n"
                "✅ 3. Хвалить за логику и попытку рассуждать, даже если итоговый ответ неточен.\n"
                "✅ 4. Дома: отрепетировать ответ в игровой форме перед зеркалом или мягкими игрушками."
            ),
            (
                "боится отвечать", "ru",
                "Школьная тревожность и страх ошибки при ответе",
                "Страх социального осуждения, насмешек сверстников или разочарования взрослых, блокирующий речевой аппарат.",
                "Рекомендации: поддерживающая безоценочная реакция на первых порах, разрешение отвечать письменно или с места, формирование права на ошибку."
            ),
            # 3. Двигательное беспокойство (не сидит на месте)
            (
                "не сидит на месте", "ru",
                "Двигательное беспокойство и сенсорная разгрузка на уроке",
                "У детей до 10-12 лет тормозные механизмы коры ещё созревают. Неподвижное сидение 45 минут подряд вызывает у многих мышечный зажим и торможение мыслительных процессов. Движение для такого ребенка — единственный способ не «выключиться» из урока.",
                "Рекомендации педагогам и родителям:\n\n"
                "✅ 1. Легитимное движение: поручите ребенку стереть с доски, раздать тетради, открыть форточку или полить цветок.\n"
                "✅ 2. Сенсорная балансировочная подушка на стул: позволяет телу совершать микродвижения таза и удерживать баланс без шума и срыва урока.\n"
                "✅ 3. Короткие 1-минутные кинезиологические разминки («кулак-ребро-ладонь») между блоками заданий."
            ),
            (
                "крутится", "ru",
                "Двигательное беспокойство и сенсорная разгрузка на уроке",
                "Физиологическая потребность нервной системы в двигательной разгрузке для поддержания тонуса коры мозга.",
                "Рекомендации: дать полезную двигательную задачу (раздать тетради, стереть с доски), использовать кинезиологические упражнения."
            ),
            # 4. СДВГ (Русский)
            (
                "сдвг", "ru",
                "СДВГ (Синдром дефицита внимания и гиперактивности)",
                "Это не лень и не плохое воспитание. Это особенность работы нервной системы, из-за которой ребенку трудно удерживать фокус на одном деле, сидеть неподвижно и контролировать импульсы.",
                "Совет родителям и учителям: разбивайте задачи на короткие шаги по 10-15 минут, хвалите за усилия и обязательно обратитесь к школьному психологу или неврологу для подбора комфортного режима учебы."
            ),
            # 5. Буллинг / Травля (Русский)
            (
                "буллинг", "ru",
                "Буллинг (Школьная травля)",
                "Это повторяющаяся агрессия одних детей против другого, где есть явное неравенство сил. Ребенок не виноват в том, что стал жертвой травли.",
                "Совет родителям: не говорите «разберись сам» или «не обращай внимания». Вмешайтесь немедленно, свяжитесь с классным руководителем и школьным психологом. Безопасность ребенка — на первом месте."
            ),
            # 6. Паническая атака (Русский)
            (
                "паническая атака", "ru",
                "Паническая атака",
                "Внезапный приступ сильной тревоги, сопровождающийся нехваткой воздуха, учащенным сердцебиением и страхом. Это неопасно для жизни, но очень пугает ребенка.",
                "Первая помощь: дышите медленно (вдох на 4 счета, выдох на 4 счета), опустите руки в теплую или прохладную воду, назовите 5 предметов вокруг себя."
            ),
            # 7. Узбекские термины
            (
                "ruchka tishlash", "uz",
                "Ruchka va buyumlarni tishlash odati (Oral stimming va onixofagiya)",
                "Bolalar neyropsixologiyasida bu injiqlik yoki yomon tarbiya emas. Bu asab tizimining o'z-o'zini tinchlantirish va quvvatlantirish mexanizmidir:\n\n"
                "👶 Boshlang'ich sinf va maktabgacha yoshdagi bolalar: Bola diqqatini darsga jamlashga (yozish, hisoblash) uringanda, miya tez toliqadi. Jag' mushaklarini qisish va ruchkani tishlash orqali miya po'stlog'i qo'shimcha impuls oladi va diqqatni ushlab turadi.\n\n"
                "🧑 O'smirlar: Bu ko'pincha darsdagi kuchli xavotir, xato qilishdan qo'rqish yoki yashirin stress natijasida yuzaga keladi.",
                "Amaliy yordam usullari:\n\n"
                "✅ 1. Sensor almashtirish (og'iz uchun xavfsiz alternativa): ruchka ustiga kiyiladigan xavfsiz silikon qopqoqlar («chewelry»), qattiqroq naychali (trubochkali) suv idishi.\n"
                "✅ 2. Qo'llar uchun taktil mashg'ulot: Su-Jok massaj halqachasi yoki antistress to'pchalari.\n"
                "✅ 3. Yoshga mos yondashuv: kichik yoshdagi bolalarga pand-nasihat foyda bermaydi — faqat xavfsiz narsaga almashtirish kerak.\n"
                "⛔ QAT'IYAN TAQIQLANADI: Bolani sinf oldida uyaltirish, qo'liga urish yoki achchiq narsalar surtish."
            ),
            (
                "ruchkani tishlaydi", "uz",
                "Ruchka va buyumlarni tishlash odati (Oral stimming)",
                "Asab tizimining diqqatni jamlash uchun o'z-o'zini sensor quvvatlantirishi.",
                "Maslahat: xavfsiz silikon qopqoqlar bering, naychali suv ichiring, bolani aslo kamsitmang va uyaltirmang."
            ),
            (
                "tirnoq tishlash", "uz",
                "Onixofagiya (tirnoq va barmoq terisini tishlash)",
                "Surunkali xavotir va ruhiy zo'riqishga nisbatan asab tizimining himoya reaksiyasi.",
                "Maslahat: qattiq jazolamang, qo'liga Su-Jok massajeri bering, darslar va to'garaklar yuklamasini me'yorlashtiring."
            ),
            (
                "doskadan qo'rqish", "uz",
                "Doskaga chiqish va xato qilishdan qo'rqish",
                "Tengdoshlar kulgisidan yoki kattalar tanqididan qo'rqish natijasida xotira va nutqning bloklanishi.",
                "Maslahat: dastlab joyidan yoki do'sti bilan birga javob berishga ruxsat bering, harakatini maqtang."
            ),
            (
                "tinch o'tirmaydi", "uz",
                "Darsda tinch o'tirmaslik va harakatlanish ehtiyoji",
                "Kichik yoshdagi bolalarda tormozlanish markazlarining to'liq shakllanmaganligi sababli yuzaga keladi. Harakat miyani uyg'oq tutishga yordam beradi.",
                "Maslahat: doskani artish, daftarlarni tarqatish kabi foydali jismoniy vazifalar bering."
            ),
            (
                "diqqat yetishmasligi", "uz",
                "DYGS (Diqqat yetishmasligi va giperaktivlik sindromi)",
                "Bu erkalik yoki yomon tarbiya emas. Bu asab tizimining o'ziga xos xususiyati bo'lib, bolaga diqqatni jamlash, bir joyda tinch o'tirish va his-tuyg'ularni boshqarish qiyin bo'ladi.",
                "Ota-onalar va o'qituvchilarga maslahat: vazifalarni 10-15 daqiqalik qismlarga bo'ling, maktab psixologi bilan birgalikda bolaga qulay o'quv rejimini tuzing."
            ),
            (
                "bulling", "uz",
                "Bulling (Maktabdagi tazyiq va haqorat)",
                "Bu bir guruh yoki bitta o'quvchining boshqa bolaga nisbatan doimiy ravishda kamsitishi va ruhiy/jismoniy bosim o'tkazishi. Bola bu holatda mutlaqo aybdor emas.",
                "Ota-onalarga maslahat: bolani yolg'iz qoldirmang, «o'zing hal qil» demang. Zudlik bilan sinf rahbari va maktab psixologiga xabar bering."
            )
        ]

        cursor.executemany("""
            INSERT OR REPLACE INTO terms (keyword, lang, title, explanation, advice)
            VALUES (?, ?, ?, ?, ?)
        """, terms)

    def find_term(self, text: str) -> dict | None:
        """Ищет в тексте упоминание психологического термина."""
        clean_text = text.lower()
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT keyword, title, explanation, advice FROM terms")
            rows = cursor.fetchall()
            
            for keyword, title, explanation, advice in rows:
                if keyword in clean_text:
                    return {
                        "title": title,
                        "explanation": explanation,
                        "advice": advice
                    }
        return None

if __name__ == "__main__":
    kb = PsychoKnowledge()
    print("База знаний инициализирована!")

    # Тест: родитель спрашивает про СДВГ
    result = kb.find_term("Здравствуйте, учитель сказал что у сына подозрение на сдвг, что это?")
    if result:
        print("\nНАЙДЕНО ПОНЯТИЕ:")
        print("📌", result["title"])
        print("📖 Объяснение:", result["explanation"])
        print("💡 Совет:", result["advice"])

    # Тест: вопрос на узбекском про буллинг
    res_uz = kb.find_term("Maktabda bolamga nisbatan bulling bo'lyapti")
    if res_uz:
        print("\nO'ZBEKCHA NATIJA:")
        print("📌", res_uz["title"])
        print("📖 Tushuntirish:", res_uz["explanation"])