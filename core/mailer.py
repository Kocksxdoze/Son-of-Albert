import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

class Mailer:
    def __init__(self):
        self.smtp_host = os.environ.get("SMTP_HOST", "smtp.gmail.com")
        self.smtp_port = int(os.environ.get("SMTP_PORT", 587))
        self.smtp_user = os.environ.get("SMTP_USER", "")
        self.smtp_pass = os.environ.get("SMTP_PASSWORD", "")

    def send_verification_code(self, to_email: str, username: str, code: str) -> tuple[bool, str]:
        """
        Отправляет 6-значный проверочный код.
        Если SMTP не настроен — код выводится в консоль бэкенда (Dev-режим).
        """
        subject = f"🔐 Код подтверждения Empasis AI: {code}"
        
        # Режим разработки: вывод в консоль
        if not self.smtp_user or not self.smtp_pass:
            print("\n" + "=" * 60)
            print(f"[DEV MAILER] Verification Code:")
            print(f"   To: {to_email} ({username})")
            print(f"   Code: >>> {code} <<<")
            print("=" * 60 + "\n")
            return True, f"Код {code} отправлен (Dev режим: см. терминал)"

        # Реальная отправка через SMTP
        try:
            msg = MIMEMultipart("alternative")
            msg["Subject"] = subject
            msg["From"] = f"Empasis AI <{self.smtp_user}>"
            msg["To"] = to_email

            html_body = f"""
            <div style="font-family: Arial, sans-serif; background-color: #0b0f19; color: #ffffff; padding: 24px; border-radius: 16px; max-width: 500px;">
                <h2 style="color: #6366f1; margin-top: 0;">Empasis School Care AI 💙</h2>
                <p>Здравствуйте, <b>{username}</b>!</p>
                <p>Ваш код подтверждения для входа в школьный психологический сервис:</p>
                <div style="font-size: 28px; font-weight: bold; letter-spacing: 4px; color: #06b6d4; background: rgba(255,255,255,0.06); padding: 14px 20px; border-radius: 10px; display: inline-block; margin: 12px 0;">
                    {code}
                </div>
                <p style="font-size: 12px; color: #94a3b8;">Никому не передавайте этот код. Если вы не регистрировались в Empasis, просто проигнорируйте это письмо.</p>
            </div>
            """
            msg.attach(MIMEText(html_body, "html"))

            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_user, self.smtp_pass)
                server.sendmail(self.smtp_user, to_email, msg.as_string())

            return True, "Код успешно отправлен на вашу почту!"
        except Exception as e:
            print(f"⚠️ Ошибка отправки email: {e}")
            return False, f"Ошибка отправки email: {str(e)}"
