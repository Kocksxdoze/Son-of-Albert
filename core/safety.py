import re

class SafetyGuard:
    def __init__(self):
        # 1. Словарь триггеров на 3 языках (в нижнем регистре)
        self.triggers = {
            "ru": [
                "суицид", "убить себя", "умереть", "не хочу жить", "покончить с собой",
                "порезать", "вскрыть вены", "селфхарм", "спрыгнуть", "передоз"
            ],
            "uz": [
                "o'lish", "o'ldirish", "jonimga tegdi", "yashashni xohlamayman",
                "o'z joniga qasd", "o'zimni o'ldiraman", "kesish", "qon", "ўлиш", "ўзини ўлдириш"
            ],
            "en": [
                "suicide", "kill myself", "want to die", "end my life",
                "cut myself", "self harm", "don't want to live"
            ]
        }

        # 2. Официальные экстренные контакты Республики Узбекистан
        self.emergency_contacts = {
            "ru": (
                "🚨 **ВНИМАНИЕ! ТЕБЕ НЕ НУЖНО БЫТЬ ОДНОМУ В ЭТОТ МОМЕНТ.**\n\n"
                "Твоя жизнь имеет огромную ценность. Пожалуйста, обратись за бесплатной и анонимной помощью:\n"
                "📞 **1146** — Национальная горячая линия помощи детям и женщинам (круглосуточно)\n"
                "📞 **1039** — Горячая линия Детского омбудсмана Республики Узбекистан\n"
                "📞 **1003** — Телефон доверия Минздрава РУз\n"
                "📞 **112 / 102** — Единая служба экстренной помощи\n"
                "🏫 Также обязательно обратись к нашему **школьному психологу** — его кабинет открыт для тебя."
            ),
            "uz": (
                "🚨 **DIQQAT! SEN HOZIR YOLG'IZ EMASSAN.**\n\n"
                "Sening hayoting juda qadrli. Iltimos, zudlik bilan bepul va maxfiy yordamga murojaat qil:\n"
                "📞 **1146** — Bolalar va ayollar uchun milliy ishonch telefoni (24/7)\n"
                "📞 **1039** — O'zbekiston Respublikasi Bolalar ombudsmani ishonch telefoni\n"
                "📞 **1003** — O'zbekiston Respublikasi Sog'liqni saqlash vazirligi ishonch telefoni\n"
                "📞 **112 / 102** — Yagona shoshilinch xizmat\n"
                "🏫 Shuningdek, albatta **maktabimiz psixologiga** murojaat qil — uning eshigi sen uchun ochiq."
            ),
            "en": (
                "🚨 **ATTENTION! YOU ARE NOT ALONE RIGHT NOW.**\n\n"
                "Your life matters. Please reach out for immediate, free, and confidential help in Uzbekistan:\n"
                "📞 **1146** — National Helpline for Children and Women (24/7)\n"
                "📞 **1039** — Office of the Children's Ombudsman of Uzbekistan\n"
                "📞 **1003** — Ministry of Health Helpline\n"
                "📞 **112 / 102** — Emergency Services\n"
                "🏫 You can also contact our **School Psychologist** — their door is always open for you."
            )
        }

    def check_crisis(self, text: str, lang: str = "ru") -> tuple[bool, str]:
        """
        Проверяет сообщение на наличие опасных триггеров.
        Возвращает: (найден_ли_кризис, сообщение_помощи_или_пустота)
        """
        clean_text = text.lower()

        # Проверяем триггеры по всем языкам
        for language, words in self.triggers.items():
            for word in words:
                # Поиск целых слов или вхождений
                if word in clean_text:
                    # Возвращаем экстренное сообщение на выбранном языке пользователя
                    response = self.emergency_contacts.get(lang, self.emergency_contacts["ru"])
                    return True, response

        return False, ""

if __name__ == "__main__":
    guard = SafetyGuard()
    
    # Тест 1: Русский
    crisis, msg = guard.check_crisis("мне кажется, я хочу порезать руки", lang="ru")
    print("Тест RU (должен быть True):", crisis)
    if crisis:
        print(msg)
        print("-" * 50)

    # Тест 2: Узбекский
    crisis_uz, msg_uz = guard.check_crisis("men yashashni xohlamayman", lang="uz")
    print("Тест UZ (должен быть True):", crisis_uz)
    if crisis_uz:
        print(msg_uz)
        print("-" * 50)

    # Тест 3: Обычная фраза
    safe, _ = guard.check_crisis("Мне грустно из-за контрольной по математике", lang="ru")
    print("Тест Безопасно (должен быть False):", safe)