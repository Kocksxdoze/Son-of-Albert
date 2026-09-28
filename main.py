import sys
import os

# Добавляем директорию backend в sys.path, чтобы модули core и storage импортировались без ошибок
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.safety import SafetyGuard
from storage.knowledge import PsychoKnowledge
from core.brain import EmpasisBrain

def print_banner(lang: str):
    """Выводит приветственный баннер и дисклеймер."""
    if lang == "uz":
        print("\n" + "=" * 65)
        print("  💙 EMPASIS AI (Beta) — Maktab psixologi raqamli yordamchisi")
        print("=" * 65)
        print("⚠️  DIQQAT: Ushbu tizim shifokor qabulini almashtirmaydi.")
        print("   Bu erkin suhbat, ruhiy dalda va ma'lumot olish maydoni.")
        print("   Chiqish uchun 'chiqish' yoki 'exit' deb yozing.")
        print("=" * 65 + "\n")
    elif lang == "en":
        print("\n" + "=" * 65)
        print("  💙 EMPASIS AI (Beta) — School Psychologist Digital Assistant")
        print("=" * 65)
        print("⚠️  NOTE: This system does not replace a licensed medical doctor.")
        print("   It is a safe space for listening, psycho-education, and support.")
        print("   Type 'exit' to quit.")
        print("=" * 65 + "\n")
    else:
        print("\n" + "=" * 65)
        print("  💙 EMPASIS AI (Beta) — Ассистент школьной психологической службы")
        print("=" * 65)
        print("⚠️  ДИСКЛЕЙМЕР: Система не является медицинской и не ставит диагнозы.")
        print("   Это безопасное пространство для поддержки и психопросвещения.")
        print("   Для выхода введите 'выход' или 'exit'.")
        print("=" * 65 + "\n")

def select_language() -> str:
    """Выбор языка при запуске."""
    print("\nTilni tanlang / Выберите язык / Select language:")
    print("1. O'zbekcha 🇺🇿")
    print("2. Русский 🇷🇺 (по умолчанию)")
    print("3. English 🇬🇧")
    
    choice = input("\nВаш выбор (1/2/3): ").strip()
    if choice == "1":
        return "uz"
    elif choice == "3":
        return "en"
    return "ru"

def main():
    # 1. Выбираем язык общения
    lang = select_language()
    print_banner(lang)

    # 2. Инициализируем компоненты MVP
    safety = SafetyGuard()
    knowledge = PsychoKnowledge()
    brain = EmpasisBrain()

    prompt_label = {
        "uz": "Siz: ",
        "ru": "Вы: ",
        "en": "You: "
    }.get(lang, "Вы: ")

    bot_label = "Empasis 💙: "

    # 3. Интерактивный диалоговый цикл
    while True:
        try:
            user_input = input(f"\n{prompt_label}").strip()
            
            if not user_input:
                continue

            # Команды выхода
            if user_input.lower() in ["exit", "quit", "выход", "chiqish", "tamom"]:
                farewell = {
                    "uz": "Suhbatingiz uchun rahmat. O'zingizni asrang! Kiringiz ochiq.",
                    "ru": "Спасибо за доверие. Берегите себя! Двери нашего кабинета всегда открыты.",
                    "en": "Thank you for sharing. Take care of yourself! We are always here for you."
                }.get(lang, "Берегите себя!")
                print(f"\n{bot_label}{farewell}\n")
                break

            # ЭТАП 1: Проверка на безопасность и кризис
            is_crisis, crisis_msg = safety.check_crisis(user_input, lang=lang)
            if is_crisis:
                print(f"\n{bot_label}\n{crisis_msg}\n")
                continue  # Прерываем обработку, выдаем экстренную помощь

            # ЭТАП 2: Поиск в базе знаний (если вопрос о терминах/состояниях)
            kb_info = knowledge.find_term(user_input)

            # ЭТАП 3: Генерация эмпатичного ответа
            response = brain.generate_response(user_input, lang=lang, kb_info=kb_info)
            print(f"\n{bot_label}{response}\n")

        except KeyboardInterrupt:
            print("\n\nСессия завершена. Берегите себя!")
            sys.exit(0)

if __name__ == "__main__":
    main()