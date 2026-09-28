import json
import urllib.request
import urllib.error

class EmpasisBrain:
    def __init__(self, model_name: str = "qwen2.5:1.5b"):
        self.model_name = model_name
        # Используем современный эндпоинт чата Ollama с поддержкой контекста
        self.ollama_chat_url = "http://localhost:11434/api/chat"
        # История сообщений диалога
        self.history: list[dict] = []

        # Профессиональные системные установки с фокусом на эмпатию, активное слушание и клинико-педагогическую точность
        self.system_prompts = {
            "ru": (
                "Ты — Empasis, чуткий, внимательный, мудрый цифровой ассистент и школьный ИИ-помощник. "
                "\nТВОЯ ГЛАВНАЯ ЦЕЛЬ — быть безопасным другом, интеллектуальным помощником и квалифицированным консультантом в школьной жизни как для учеников, так и для родителей и педагогов."
                "\n\nФУНДАМЕНТАЛЬНЫЕ ПРАВИЛА И РЕЖИМЫ ДИАЛОГА:"
                "\n1. РАЗЛИЧЕНИЕ СУБЪЕКТА (1-е ЛИЦО vs 3-е ЛИЦО):"
                "\n   • РЕЖИМ ЛИЧНЫХ ЧУВСТВ (собеседник говорит о СЕБЕ: 'мне грустно', 'я боюсь', 'меня обижают', 'мне тяжело'):"
                "\n     - Прояви эмпатию и валидацию чувств ('Мне очень жаль, что тебе сейчас так тоскливо. Грустить — это нормально...')."
                "\n     - Не сыпь банальными советами ('улыбнись', 'выпей чаю'). Прояви интерес, задай 1-2 открытых вопроса, дай выговориться."
                "\n     - Заканчивай бережным вопросом."
                "\n   • РЕЖИМ КЕЙС-КОНСУЛЬТАЦИИ (собеседник спрашивает про ДРУГОГО ЧЕЛОВЕКА / РЕБЕНКА / УЧЕНИКА: 'ученик грызет...', 'ребенок боится...', 'сын не делает уроки', 'дочь плачет', 'дети в классе шумят'):"
                "\n     - СТРОЖАЙШИЙ ЗАПРЕТ: НИ В КОЕМ СЛУЧАЕ не говори собеседнику 'мне жаль, что ты так делаешь', 'почему ты грызешь ручки' или 'сделай вдох'! Собеседник — НЕ ребенок с этой проблемой, а РОДИТЕЛЬ, УЧИТЕЛЬ или ПСИХОЛОГ!"
                "\n     - СТРУКТУРА ЭКСПЕРТНОГО ОТВЕТА В РЕЖИМЕ КЕЙСА:"
                "\n       1) Возрастная специфика: четко разделяй дошколят/младших школьников (1-4 класс) и подростков. У младших детей волевой самоконтроль лобных долей ещё не созрел, им бессмысленно читать нотации или спрашивать 'зачем ты это делаешь' — помогает только сенсорная подмена и смена деятельности. У подростков — важно искать психоэмоциональный триггер."
                "\n       2) Физиологический и психологический смысл: объясни, что поведение — это не каприз и не лень, а реакция нервной системы (сенсорный стимминг / догрузка коры мозга жевательными мышцами для удержания фокуса / сброс напряжения)."
                "\n       3) Практические методы помощи: сенсорное замещение (грызунки-насадки, вода через тугую трубочку, твердые перекусы), тактильные предметы для рук (кольца Су-Джок, эспандеры), физкультминутки."
                "\n       4) Чего делать НЕЛЬЗЯ: строго предостереги от стыжения перед классом/семьей, криков, физического выдергивания предметов изо рта или мазания горьким."
                "\n2. ПРИВЕТСТВИЕ И САМОПРЕДСТАВЛЕНИЕ: Отвечай естественно и тепло. Представляйся как Empasis — цифровой школьный ассистент."
                "\n3. ОСТРАЯ ПАНИКА У СОБЕСЕДНИКА: Только если сам собеседник испытывает удушье и панический приступ — предложи короткую технику дыхания (физиологический вздох)."
            ),
            "uz": (
                "Siz — Empasis, samimiy, dono, e'tiborli va ishonchli maktab raqamli yordamchisisiz. "
                "\nASOSIY MAQSADINGIZ — o'quvchilar, ota-onalar va o'qituvchilarga ruhiy va pedagogik maslahat berish, ularni dildan tinglash va qo'llab-quvvatlash."
                "\n\nMULOQOTNING ASOSIY QOIDALARI:"
                "\n1. SHAXSNI AJRATISH (1-SHAXS vs 3-SHAXS):"
                "\n   • SHAXSIY HIS-TUYG'ULAR (suhbatdosh O'ZI haqida gapirganda: 'menga og'ir', 'qo'rqyapman', 'ko'nglim cho'kdi'):"
                "\n     - Daldani his qildiring, his-tuyg'ularini tushuning ('Senga hozir qiyin va xafa ekaningdan afsusdaman...')."
                "\n     - Shoshilinch maslahat bermang, dardi bilan qiziqing va dilini bo'shatishga imkon bering."
                "\n   • BOLALAR VA O'QUVCHILAR HAQIDA SO'RALGANDA (3-shaxs: 'o'quvchi ruchka tishlaydi', 'bolam dars qilmayapti', 'o'g'lim qo'rqadi'):"
                "\n     - QAT'IYAN TAQIQLANADI: Suhbatdoshga 'sen nega ruchka tishlayapsan' yoki 'bunday qilishingdan afsusdaman' deb aytmang! Suhbatdosh muammoli bola emas, balki OTA-ONA, O'QITUVCHI yoki PSIXOLOGDIR!"
                "\n     - MASLAHAT TUZILISHI:"
                "\n       1) Yosh xususiyati: boshlang'ich sinf va o'smirlarni ajrating. Kichik bolalarga tanbeh berish foydasiz, ularga sensor almashtirish kerak."
                "\n       2) Sababi: bu erkalik emas, asab tizimining diqqatni jamlash yoki zo'riqishni yengish mexanizmi ekanini tushuntiring."
                "\n       3) Amaliy usullar: sensor almashtirish (silikon qopqoqlar, naychali suv), taktil vositalar (Su-Jok halqachasi)."
                "\n       4) Nimalar taqiqlanadi: sinf oldida uyaltirish, urish, achchiq narsalar surtish qat'iyan man etiladi."
                "\n2. SALOMLASHISH: Samimiy salomlashing va Empasis deb tanishtiring."
            ),
            "en": (
                "You are Empasis, an empathetic, knowledgeable, and reliable digital school assistant. "
                "\nCORE MISSION: To provide empathetic listening for students and professional, pedagogical and neuropsychological guidance for teachers and parents."
                "\n\nKEY CONVERSATIONAL RULES:"
                "\n1. SUBJECT DIFFERENTIATION (1st PERSON vs 3rd PERSON):"
                "\n   • PERSONAL EMOTIONS (User talks about THEMSELVES: 'I feel sad', 'I am afraid', 'I feel overwhelmed'):"
                "\n     - Empathize and validate their feelings first. Offer a safe space to vent before giving any advice."
                "\n   • CASE CONSULTATION (User asks about a THIRD PERSON / CHILD / STUDENT: 'a student bites pens', 'my child refuses homework', 'son is anxious'):"
                "\n     - STRICT RULE: NEVER address the user as if they are the one biting pens or acting out! The user is a TEACHER, PARENT, or PSYCHOLOGIST."
                "\n     - CONSULTATION STRUCTURE:"
                "\n       1) Age differentiation (elementary/early childhood lacks conscious frontal lobe inhibition—lecturing does not work; adolescents need emotional trigger analysis)."
                "\n       2) Neuropsychological reason (sensory stimming, proprioceptive oral feedback to maintain focus, stress release)."
                "\n       3) Actionable methodologies: sensory substitution (silicone chew toppers, water through narrow straw), fidget tools (tactile rings), movement breaks."
                "\n       4) What NOT to do: strictly warn against shaming, punishment, or applying bitter substances."
            )
        }

    def _is_ollama_available(self) -> bool:
        try:
            req = urllib.request.Request("http://localhost:11434/api/tags", method="GET")
            with urllib.request.urlopen(req, timeout=3.0) as resp:
                return resp.status == 200
        except Exception:
            return False

    def _build_system_prompt(self, lang: str, user_profile: dict | None) -> str:
        base = self.system_prompts.get(lang, self.system_prompts["ru"])
        if not user_profile:
            return base

        name = user_profile.get("username", "Собеседник")
        age = user_profile.get("age", 14)
        role = user_profile.get("role", "student")

        if lang == "uz":
            profile_context = (
                f"\n\nSUHBATDOSH HAQIDA MA'LUMOT:"
                f"\nIsmi: {name}, Yoshi: {age} yoshda, Maktabdagi roli: {role}."
            )
            if role in ["psychologist", "teacher"]:
                profile_context += (
                    f"\n- Suhbatdosh — maktab { 'psixologi' if role == 'psychologist' else 'o‘qituvchisi' }. "
                    f"U bilan tengdosh mutaxassis sifatida gaplashing. Uni 'maktab psixologiga murojaat qiling' deb yubormang!"
                )
            elif role == "parent":
                profile_context += (
                    f"\n- Suhbatdosh — ota-ona. Mehribon va dalda beruvchi ohangda, uyda qo'llash oson bo'lgan usullarni bering."
                )
            else:
                profile_context += (
                    f"\n- Suhbatdosh — o'quvchi. Do'stona, tushunarli tilda gapiring."
                )
        elif lang == "en":
            profile_context = (
                f"\n\nUSER PROFILE:"
                f"\nName: {name}, Age: {age} y.o., Role: {role}."
            )
            if role in ["psychologist", "teacher"]:
                profile_context += (
                    f"\n- User is a school { 'psychologist' if role == 'psychologist' else 'teacher' }. "
                    f"Treat them as an esteemed colleague and supervisor. Never tell them to 'visit a school psychologist'!"
                )
            elif role == "parent":
                profile_context += (
                    f"\n- User is a parent. Provide supportive, blame-free, home-actionable advice."
                )
            else:
                profile_context += (
                    f"\n- User is a student. Use clear, supportive, age-appropriate language."
                )
        else:
            profile_context = (
                f"\n\nПРОФИЛЬ ТЕКУЩЕГО СОБЕСЕДНИКА:"
                f"\nЛогин: {name}, Возраст: {age} лет, Роль в школе: {role}."
                f"\nПРАВИЛА ОБЩЕНИЯ С ЭТОЙ РОЛЬЮ:"
            )
            if role in ["psychologist", "teacher"]:
                profile_context += (
                    f"\n- Собеседник — { 'Школьный психолог' if role == 'psychologist' else 'Учитель' }. "
                    f"Общайся с ним уважительно, на равных, как опытный коллега-методист и супервизор. "
                    f"Используй корректную терминологию (сенсорная интеграция, оральный стимминг, онихофагия, проприоцепция, догрузка коры). "
                    f"НИ В КОЕМ СЛУЧАЕ не рекомендуй собеседнику 'обратиться к школьному психологу' — он сам специалист школы!"
                )
            elif role == "parent":
                profile_context += (
                    f"\n- Собеседник — родитель. Поддержи его, сними чувство тревоги и вины ('вы замечательный родитель, что обратили внимание на это'). "
                    f"Давай простые, применимые дома и понятные рекомендации без академического занудства."
                )
            else:
                profile_context += (
                    f"\n- Собеседник — школьник/подросток. Говори просто, тепло и по-человечески, как надёжный старший наставник."
                )

        return base + profile_context

    def generate_response(
        self, 
        user_text: str, 
        lang: str = "ru", 
        kb_info: dict | None = None,
        user_profile: dict | None = None,
        chat_history: list[dict] | None = None
    ) -> str:
        # Сценарий базы знаний (проверенная карточка диагноза)
        if kb_info:
            return self._format_knowledge_response(kb_info, lang, user_profile)

        # Сценарий живого общения
        if self._is_ollama_available():
            return self._generate_via_ollama_chat(user_text, lang, user_profile, chat_history)
        else:
            return self._generate_fallback(user_text, lang, user_profile)

    def generate_stream(
        self,
        user_text: str,
        lang: str = "ru",
        kb_info: dict | None = None,
        user_profile: dict | None = None,
        chat_history: list[dict] | None = None
    ):
        """Потоковый генератор токенов ответа (yield) для Server-Sent Events."""
        if kb_info:
            card = self._format_knowledge_response(kb_info, lang, user_profile)
            yield {"token": card, "done": False, "is_term": True}
            yield {"token": "", "done": True, "is_term": True}
            return

        if not self._is_ollama_available():
            fallback_text = self._generate_fallback(user_text, lang, user_profile)
            yield {"token": fallback_text, "done": False, "is_fallback": True}
            yield {"token": "", "done": True, "is_fallback": True}
            return

        system_content = self._build_system_prompt(lang, user_profile)
        messages = [{"role": "system", "content": system_content}]

        if chat_history:
            for m in chat_history[-6:]:
                role = "assistant" if m.get("sender") == "bot" else "user"
                messages.append({"role": role, "content": m.get("text", "")})

        messages.append({"role": "user", "content": user_text})

        payload = json.dumps({
            "model": self.model_name,
            "messages": messages,
            "stream": True,
            "options": {
                "temperature": 0.7,
                "num_predict": 1024,
                "top_p": 0.9,
                "repeat_penalty": 1.15
            }
        }).encode("utf-8")

        try:
            req = urllib.request.Request(
                self.ollama_chat_url,
                data=payload,
                headers={"Content-Type": "application/json"}
            )
            with urllib.request.urlopen(req, timeout=120.0) as resp:
                for line in resp:
                    if not line:
                        continue
                    try:
                        chunk = json.loads(line.decode("utf-8"))
                        token = chunk.get("message", {}).get("content", "")
                        done = chunk.get("done", False)
                        if token:
                            yield {"token": token, "done": False}
                        if done:
                            yield {"token": "", "done": True}
                            break
                    except json.JSONDecodeError:
                        continue
        except Exception:
            fallback_text = self._generate_fallback(user_text, lang, user_profile)
            yield {"token": fallback_text, "done": False, "is_fallback": True}
            yield {"token": "", "done": True, "is_fallback": True}

    def _format_knowledge_response(self, kb_info: dict, lang: str, user_profile: dict | None = None) -> str:
        role = user_profile.get("role", "student") if user_profile else "student"
        is_staff = role in ["psychologist", "teacher", "admin"]

        if lang == "uz":
            footer = (
                "🏫 *Material maktab psixologik xizmati va pedagogik jamoasi uchun metodik qo'llanma sifatida tayyorlandi.*"
                if is_staff else
                "🏫 *Batafsil ma'lumot va individual yordam uchun maktabimiz psixologi qabuliga yozilishingiz mumkin.*"
            )
            return (
                f"📌 **{kb_info['title']}**\n\n"
                f"🔹 **Bu nima:** {kb_info['explanation']}\n\n"
                f"💡 **Maslahat:** {kb_info['advice']}\n\n"
                f"{footer}"
            )
        else:
            footer = (
                "🏫 *Материал подготовлен в качестве методической поддержки для школьного психолога и педагогического состава.*"
                if is_staff else
                "🏫 *Вы всегда можете подойти к нашему школьному психологу, чтобы вместе обсудить этот вопрос в безопасной обстановке.*"
            )
            return (
                f"📌 **{kb_info['title']}**\n\n"
                f"🔹 **Что это простыми словами:** {kb_info['explanation']}\n\n"
                f"💡 **Рекомендация:** {kb_info['advice']}\n\n"
                f"{footer}"
            )

    def _generate_via_ollama_chat(
        self, 
        user_text: str, 
        lang: str, 
        user_profile: dict | None = None,
        chat_history: list[dict] | None = None
    ) -> str:
        system_content = self._build_system_prompt(lang, user_profile)

        # Формируем цепочку сообщений: системный промпт + история диалога
        messages = [{"role": "system", "content": system_content}]

        if chat_history:
            # Берем последние 6 сообщений из переданной истории диалога
            for m in chat_history[-6:]:
                role = "assistant" if m.get("sender") == "bot" else "user"
                messages.append({"role": role, "content": m.get("text", "")})

        # Добавляем текущую реплику пользователя
        messages.append({"role": "user", "content": user_text})

        payload = json.dumps({
            "model": self.model_name,
            "messages": messages,
            "stream": False,
            "options": {
                "temperature": 0.7,
                "num_predict": 1024,
                "top_p": 0.9,
                "repeat_penalty": 1.15
            }
        }).encode("utf-8")

        try:
            req = urllib.request.Request(
                self.ollama_chat_url,
                data=payload,
                headers={"Content-Type": "application/json"}
            )
            with urllib.request.urlopen(req, timeout=120.0) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                assistant_reply = data.get("message", {}).get("content", "").strip()

                # Запоминаем ответ ассистента в историю
                self.history.append({"role": "assistant", "content": assistant_reply})
                return assistant_reply
        except Exception:
            return self._generate_fallback(user_text, lang, user_profile)

    def _generate_fallback(self, user_text: str, lang: str, user_profile: dict | None = None) -> str:
        text = user_text.lower()
        role = user_profile.get("role", "student") if user_profile else "student"

        # 1. Приветствие
        if any(w in text for w in ["привет", "здравствуй", "salom", "hello"]):
            return {
                "uz": "Assalomu alaykum! Maktab raqamli xizmatiga xush kelibsiz. Qanday yordam bera olaman?",
                "ru": "Привет! Рад тебя слышать. Как проходит твой день, чем могу помочь?",
                "en": "Hello! Welcome to our school support service. How can I assist you today?"
            }.get(lang, "Привет! Рад тебя слышать. Чем могу помочь?")

        # 2. Отрицания тревоги ("меня ничего не тревожит", "все хорошо", "не волнуюсь")
        if any(w in text for w in ["не тревож", "ничего не тревожит", "все хорошо", "все отлично", "всё хорошо", "всё отлично", "не боюсь", "не переживаю", "hammasi yaxshi"]):
            return {
                "uz": "Juda soz! Ko'nglingiz xotirjam va hammasi joyida ekanidan xursandman. Darslar, maktab loyihalari yoki qiziqarli mavzularda yordam bera olamanmi?",
                "ru": "Очень здорово! Искренне рад, что у тебя всё спокойно и на душе порядок. Чем могу быть полезен: разобрать сложный предмет, обсудить школьный проект или просто пообщаться?",
                "en": "Glad to hear that everything is going well and peaceful! How can I assist you today with studies or school projects?"
            }.get(lang, "Рад, что всё хорошо! Чем могу помочь?")

        # 3. Вопросы о психологии и саморазвитии
        if any(w in text for w in ["о психолог", "что такое психолог", "psixologiya"]):
            return {
                "uz": "Psixologiya — insonning his-tuyg'ulari, xatti-harakatlari va munosabatlarini o'rganuvchi ajoyib fan. Maktabda u o'quvchilarga o'zini tushunishga, stressni yengishga va mustahkam do'stlik qurishga yordam beradi. Qaysi yo'nalishi sizni ko'proq qiziqtiradi?",
                "ru": "Психология — это наука о том, как устроены наши мысли, эмоции, поведение и общение. В школе она помогает научиться понимать себя, уверенно выступать, справляться с волнением перед экзаменами и выстраивать доверительные отношения. Какая тема тебе сейчас наиболее интересна?",
                "en": "Psychology is the study of mind, emotions, and human behavior. In school, it helps with self-confidence, stress management, and healthy relationships. What aspect interests you most?"
            }.get(lang, "Психология помогает лучше понимать себя и свои эмоции.")

        # 4. Консультация по третьему лицу (ученик, ребенок, сын, дочь)
        if any(w in text for w in ["ученик", "ребенок", "ребёнок", "сын", "дочь", "дочка", "дети", "o'quvchi", "bolam", "farzand"]):
            return {
                "uz": (
                    "O'quvchi va bolalar bilan bog'liq vaziyatlarda har doim ularning yoshini va xatti-harakatining ruhiy sababini inobatga olish zarur.\n\n"
                    "1. Kichik yoshda bolalarga tanbeh berish emas, balki qulay muhit yaratish va diqqatini xavfsiz mashg'ulotga almashtirish yordam beradi.\n"
                    "2. Vaziyat qaysi darsda yoki qanday sharoitda kuchayishini kuzatish muhim.\n"
                    "Bolaning yoshi necha va aynan qanday holat yuz beryapti? Batafsilroq aytsangiz, aniqroq metodik maslahat bera olaman."
                ),
                "ru": (
                    "В работе с детьми и учениками важно в первую очередь отделять физиологическую реакцию нервной системы от осознанного поведения.\n\n"
                    "1. **Возрастная специфика:** Для младших школьников бессмысленны запреты и нотации — лобные доли самоконтроля ещё созревают. Необходимы физическая смена активности и сенсорная разгрузка.\n"
                    "2. **Для подростков:** Важен анализ триггеров напряжения (учебная перегрузка, страх ошибки, конфликты).\n\n"
                    "Уточните, пожалуйста, о каком возрасте идет речь и при каких обстоятельствах это проявляется чаще всего? Я дам адресные методические рекомендации."
                ),
                "en": (
                    "When addressing student or child behavioral concerns, it's essential to assess both developmental stage and neurological triggers.\n"
                    "Could you specify the student's age/grade and the specific context when this occurs?"
                )
            }.get(lang, "Уточните возраст ребенка и обстоятельства, чтобы подобрать точную методику.")

        # 5. Личные переживания (грусть, обида, тоска)
        elif any(w in text for w in ["грустн", "грущ", "печал", "тоск", "плохо", "плач", "слез", "одинок", "обидн", "надоел", "тяжело"]):
            return {
                "uz": (
                    "Senga hozir qiyin va xafa ekaningdan chin dildan afsusdaman. Ko'ngil cho'kkanda bu yukni bir o'zing ko'tarib yurishing shart emas.\n\n"
                    "Nima bo'ldi, o'rtoq? Bugun maktabda yoki do'stlaring bilan biror ko'ngilsizlik yuz berdimi? "
                    "Agar xohlasang, batafsil aytib ber — men seni hech qanday tanqidsiz, diqqat bilan eshitishga tayyorman."
                ),
                "ru": (
                    "Мне очень жаль, что тебе сейчас так тоскливо и тяжело на душе. Грустить — это совершенно нормально, и очень тяжело носить эту тяжесть в себе в одиночку.\n\n"
                    "Расскажи, что произошло? Что-то случилось сегодня в школе или с друзьями, или это чувство копилось уже давно? "
                    "Я никуда не тороплюсь и готов выслушать всё, чем ты захочешь поделиться."
                ),
                "en": (
                    "I'm really sorry you're feeling so down and heavy right now. Carrying sadness alone can be exhausting.\n\n"
                    "What happened? Did something specific happen today at school or with friends, or has this been building up for a while? "
                    "Take your time—I'm right here and ready to listen to whatever you want to share."
                )
            }.get(lang, "Мне очень жаль, что тебе сейчас тоскливо. Расскажи, что случилось? Я внимательно тебя слушаю.")

        # 6. Острая паника и соматический приступ у самого собеседника
        elif any(w in text for w in ["паник", "задыха", "трясет", "колотится сердце", "удушье", "страшно до дрожи"]):
            return {
                "uz": (
                    "Bu holat kuchli hayajon va stressdan kelib chiqadi. Hozir eng muhimi — nafasni me'yorga keltirish:\n\n"
                    "🫁 **Fiziologik nafas mashqi:** Burun orqali 2 marta ketma-ket qisqa chuqur nafas oling, "
                    "so'ng og'iz orqali sekin va to'liq chiqaring. Buni 3-4 marta takrorlang. Bu yurak urishini 30 soniyada sekinlashtiradi."
                ),
                "ru": (
                    "То, что ты описываешь — это естественная реакция вегетативной нервной системы на острый приступ тревоги.\n\n"
                    "🫁 **Сделай прямо сейчас 'Физиологический вздох':**\n"
                    "1. Сделай два коротких вдоха носом подряд (один глубокий и сразу короткий довдох).\n"
                    "2. Затем сделай один долгий и плавный выдох через рот.\n"
                    "Повтори 3-4 раза. Это биохимически снижает уровень углекислого газа и замедляет пульс меньше чем за минуту."
                ),
                "en": (
                    "What you describe is an acute stress reaction of your nervous system.\n\n"
                    "🫁 **Do the Physiological Sigh right now:**\n"
                    "1. Take two quick inhales through your nose (one deep, then a quick top-up).\n"
                    "2. Release one long, slow exhale through your mouth.\n"
                    "Repeat 3-4 times. This physically resets your heart rate within 30 seconds."
                )
            }.get(lang, "Сделай глубокий вдох носом и медленный выдох через рот.")

        elif any(w in text for w in ["английск", "урок", "школ", "устал"]):
            return "Школьные уроки порой действительно выматывают, особенно когда предмет не вдохновляет или давит каждый день. А что именно больше всего раздражает или пугает — требования, объем или страх получить плохую оценку?"
        else:
            return "Я рядом и готов помочь. Расскажи подробнее, о какой школьной ситуации или вопросе ты хочешь поговорить?"

if __name__ == "__main__":
    b = EmpasisBrain()
    print("Ollama активна:", b._is_ollama_available())