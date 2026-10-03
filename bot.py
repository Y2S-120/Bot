import smtplib
import threading
import asyncio
import time as t
from email.message import EmailMessage

from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ConversationHandler,
    ContextTypes,
    filters,
)

BOT_TOKEN = "8583078666:AAEoEj3mekhNQRcvGin_KslczTK8Y9nbjus"

ACCOUNTS = [
        ("mazen97988@gmail.com", "imzefktipwekyown"),
        ("nkmnllm@gmail.com", "iwmdmfgezvghryxs"),
        ("noctenneir@gmail.com", "cqncgqnzdkoffsem"),
        ("veltrixsiw@gmail.com", "wbzfttvppeyznrt"),
        ("mazen979887@gmail.com", "yrlkniiocnahshlb"),
        ("khalid66861@gmail.com", "pniykwrpwiqtgeio"),
        ("ibrahim979101@gmail.com", "wwivqzwzpaaleype"),
        ("kbrhom32@gmail.com", "sffbqqofpmvxtzzj"),
        ("formazen123.1@gmail.com", "qmynsqbpynrjpdzh"),
        ("formazen123.2@gmail.com", "fgmnoatpaibxtnky"),
        ("mkhalil97978@gmail.com", "bbbpdnfyvyrxqrlq"),
        ("mkhalil0791@gmail.com", "lhqvjgpfzortafod"),
        ("fahmed97811@gmail.com", "ezefqpzlfqsuofkk"),
        ("maahmed110as@gmail.com", "hbpogyszrojdixyu"),
        ("mmhmd96811@gmail.com", "kxxvemiirtuomuqr"),
        ("euro43488@gmail.com", "qgnkvotnwpghsylu"),
        ("euro63828@gmail.com", "efwynvhdpuhbxxwo"),
        ("auaha5539@gmail.com", "ayrntvvgxadmzyes"),
        ("daniahmed1000@gmail.com", "gbbhsrvzdyifhnpm"),
        ("farah0696961@gmail.com", "amhexfyosbefwfpx"),
]

PER_MSG_DELAY = 0.5
BETWEEN_ROUNDS_DELAY = 10
MAX_ROUNDS = 20

RECIPIENTS, SUBJECT, MESSAGE, TIMES = range(4)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.bot_data.get("sending"):
        await update.message.reply_text("A sending process is already running. Please wait.")
        return ConversationHandler.END

    context.user_data.clear()
    await update.message.reply_text("Enter The Emails (separated by comma):")
    return RECIPIENTS


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Cancelled. Send /start to try again.")
    return ConversationHandler.END


async def get_recipients(update, context):
    raw = update.message.text or ""
    rec = [e.strip() for e in raw.split(",") if e.strip()]
    if not rec:
        await update.message.reply_text("No valid emails. Try again:")
        return RECIPIENTS
    context.user_data["rec"] = rec
    await update.message.reply_text("Enter The Subject:")
    return SUBJECT


async def get_subject(update, context):
    context.user_data["sub"] = update.message.text or ""
    await update.message.reply_text("Enter The Message:")
    return MESSAGE


async def get_message(update, context):
    context.user_data["text"] = update.message.text or ""
    await update.message.reply_text(f"Enter The Times (1 - {MAX_ROUNDS}):")
    return TIMES


async def get_times(update, context):
    raw = (update.message.text or "").strip()
    try:
        n = int(raw)
    except ValueError:
        await update.message.reply_text("Must be a valid number. Try again:")
        return TIMES
    if n < 1 or n > MAX_ROUNDS:
        await update.message.reply_text(f"Must be between 1 and {MAX_ROUNDS}. Try again:")
        return TIMES

    chat_id = update.effective_chat.id
    rec = context.user_data["rec"]
    sub = context.user_data["sub"]
    text = context.user_data["text"]

    context.bot_data["sending"] = True

    await update.message.reply_text(f"Starting sending now... ({n} rounds per account)")

    loop = asyncio.get_running_loop()
    app = context.application
    bot_data = context.bot_data

    threading.Thread(
        target=run_sending,
        args=(app, loop, chat_id, rec, sub, text, n, bot_data),
        daemon=True,
    ).start()

    return ConversationHandler.END


def run_sending(app, loop, chat_id, rec, sub, text, n, bot_data):
    def notify(msg):
        try:
            asyncio.run_coroutine_threadsafe(
                app.bot.send_message(chat_id=chat_id, text=msg),
                loop,
            )
        except Exception:
            pass

    errors = []
    errors_lock = threading.Lock()
    stats = {"sent": 0, "failed": 0}
    start_time = t.time()

    def log_error(msg):
        with errors_lock:
            errors.append(msg)
            stats["failed"] += 1

    def log_sent():
        with errors_lock:
            stats["sent"] += 1

    def build_status(broken=False):
        duration = round(t.time() - start_time, 1)
        lines = [
            "Status Report",
            "",
            f"Sent: {stats['sent']}",
            f"Failed: {stats['failed']}",
            f"Duration: {duration}s",
        ]
        if broken:
            lines.append("Stopped early (barrier broken)")
        if errors:
            lines.append("")
            lines.append("Problems:")
            for e in errors:
                lines.append(f"- {e}")
        return "\n".join(lines)

    try:
        accounts = ACCOUNTS[:]
        num_workers = len(accounts)
        if num_workers == 0:
            notify("No accounts to use.")
            return

        barrier_end = threading.Barrier(num_workers + 1)
        barrier_start = threading.Barrier(num_workers + 1)

        def worker(email, password):
            try:
                conn = smtplib.SMTP("smtp.gmail.com", 587, timeout=30)
                conn.ehlo()
                conn.starttls()
                conn.login(email, password)
            except Exception as e:
                log_error(f"[{email}] Login failed: {e}")
                try:
                    barrier_end.abort()
                    barrier_start.abort()
                except Exception:
                    pass
                return

            try:
                for i in range(n):
                    try:
                        msg = EmailMessage()
                        msg["From"] = email
                        msg["To"] = ", ".join(rec)
                        msg["Subject"] = sub
                        msg.set_content(text)
                        conn.send_message(msg)
                        log_sent()
                    except Exception as send_e:
                        log_error(f"[{email}] Send error in round {i+1}: {send_e}")

                    t.sleep(PER_MSG_DELAY)

                    try:
                        barrier_end.wait()
                        barrier_start.wait()
                    except threading.BrokenBarrierError:
                        break
            finally:
                try:
                    conn.quit()
                except Exception:
                    pass

        threads = []
        for email, password in accounts:
            th = threading.Thread(target=worker, args=(email, password), daemon=True)
            threads.append(th)
            th.start()
            t.sleep(0.05)

        broken = False
        for i in range(n):
            try:
                barrier_end.wait()
            except threading.BrokenBarrierError:
                try:
                    barrier_end.abort()
                    barrier_start.abort()
                except Exception:
                    pass
                broken = True
                break

            if i < n - 1:
                notify(f"Round {i+1}/{n} finished. Waiting {BETWEEN_ROUNDS_DELAY}s...")
                t.sleep(BETWEEN_ROUNDS_DELAY)
            else:
                notify(f"Round {i+1}/{n} finished.")

            try:
                barrier_start.wait()
            except threading.BrokenBarrierError:
                try:
                    barrier_end.abort()
                    barrier_start.abort()
                except Exception:
                    pass
                broken = True
                break

        for th in threads:
            th.join(timeout=2)

        notify(build_status(broken))
    finally:
        bot_data["sending"] = False


def main():
    app = Application.builder().token(BOT_TOKEN).build()

    conv = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            RECIPIENTS: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_recipients)],
            SUBJECT:    [MessageHandler(filters.TEXT & ~filters.COMMAND, get_subject)],
            MESSAGE:    [MessageHandler(filters.TEXT & ~filters.COMMAND, get_message)],
            TIMES:      [MessageHandler(filters.TEXT & ~filters.COMMAND, get_times)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    app.add_handler(conv)
    print("Bot is running...")
    app.run_polling()


if __name__ == "__main__":
    main()
