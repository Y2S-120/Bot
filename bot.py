import smtplib
import threading
import asyncio
import random
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
        ("mazen979887@gmail.com", "yrlkniiocnahshlb"),
        ("khalid66861@gmail.com", "pniykwrpwiqtgeio"),
        ("ibrahim979101@gmail.com", "wwivqzwzpaaleype"),
        ("kbrhom32@gmail.com", "sffbqqofpmvxtzzj"),
        ("formazen123.1@gmail.com", "qmynsqbpynrjpdzh"),
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
        ("youeandme@gmail.com", "wynbigyzldvgsspx"),
        ("vaid.adit7@gmail.com", "wsrchrfsimkfmbql"),
        ("dannytoboss@gmail.com", "pfpghfmzzjpffgzc"),
        ("elmahambeng@gmail.com", "phmklwwxiydbvunn"),
        ("gymnasticsforlifeee@gmail.com", "ljamwgzvomkqirde"),
        ("isabellwatwbl@gmail.com", "zjehnehgbfdeqfcj"),
        ("klyacike@gmail.com", "anamdzesbzmaszbl"),
        ("lisbethrevsz@gmail.com", "evlhzhgyqkvbajej"),
        ("mansparkes35@gmail.com", "ptgtpfsgejkevgpu"),
        ("masoodkardost2014@gmail.com", "xlxhxhaydfoeeoxu"),
        ("mmsbz1728@gmail.com", "zjbnekqotxvrvzqi"),
        ("nazhi2699@gmail.com", "rhtxusrqiczlgppl"),
        ("needsel284@gmail.com", "lnavaviwaaumskue"),
        ("aayekcorb@gmail.com", "kopumakdtoxgrtjx"),
        ("abdo.kamalbashir@gmail.com", "djgjyytyfqhenkpn"),
        ("alikemalimcirkus@gmail.com", "bmgssvpuoovrtcgf"),
        ("alrhbynayl@gmail.com", "cpnjodgfamlvonss"),
        ("amin.jala654@gmail.com", "yagukgcahqvmsqnb"),
        ("angiemendezllc@gmail.com", "dvsdqqjyprignsew"),
        ("antosxamsey@gmail.com", "zrchmebqijnhqtki"),
        ("aurorarinau54@gmail.com", "eeddmdqmlmqtfeng"),
        ("bbsnansjsjj@gmail.com", "uwvokxwojhdulwhz"),
        ("bradkinsmf@gmail.com", "zgyhypniotwtipxe"),
        ("coderinggl@gmail.com", "wisamfdxodcrgknn"),
        ("nonasujo@gmail.com", "evkgofjvzdqrahpv"),
        ("orvalkaner@gmail.com", "kzugzlrtbrgpomlu"),
        ("osuhndaendiaozogsic@gmail.com", "ddosiimiudtlsgey"),
        ("otheshyintitea@gmail.com", "esgemyjzfrbilxuy"),
        ("princess1936lp@gmail.com", "sahnfeivsjfpcivs"),
        ("ranesesvjtp@gmail.com", "rxumzxdnnzzwpsog"),
        ("sarah233cristina600flor@gmail.com", "pbltxohwgulkbgau"),
        ("sarisarahnia@gmail.com", "nsuvmxqyzzileaxb"),
        ("serifesarigul1769@gmail.com", "eedajizdrjofmeqn"),
        ("sharonterqnw@gmail.com", "iievetogtdzfnvvs"),
        ("shervnn6050@gmail.com", "estatxkqrvfodlkv"),
        ("stelasapato@gmail.com", "rhevvggcmrpnvvyh"),
        ("telloe1963@gmail.com", "iubocxwzznxxszaf"),
        ("teresamtierney@gmail.com", "wpcclnbfjzuoccvv")
]

PER_MSG_DELAY = 2.0
MAX_ROUNDS = 2

SUBJECT_PREFIXES = [
    ("", 50),
    ("Hello - ", 10),
    ("Hi - ", 10),
    ("Welcome - ", 10),
    ("Greetings - ", 10),
    ("Hey - ", 10),
]

RECIPIENTS, SUBJECT, MESSAGE, TIMES = range(4)


def build_subject(base_subject):
    prefixes = [p for p, _ in SUBJECT_PREFIXES]
    weights = [w for _, w in SUBJECT_PREFIXES]
    prefix = random.choices(prefixes, weights=weights, k=1)[0]
    return f"{prefix}{base_subject}"


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
        num_recipients = len(rec)

        if num_workers == 0:
            notify("No accounts to use.")
            return
        if num_recipients == 0:
            notify("No recipients.")
            return

        chunks = []
        for i in range(num_recipients):
            start = i * num_workers // num_recipients
            end = (i + 1) * num_workers // num_recipients
            chunks.append(accounts[start:end])

        account_to_chunk = {}
        for chunk_idx, chunk in enumerate(chunks):
            for acc in chunk:
                account_to_chunk[acc[0]] = chunk_idx

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

            account_subject = build_subject(sub)

            sent_to = set()
            skip_catchup = False

            try:
                for round_idx in range(n):
                    recipient_idx = (account_to_chunk[email] + round_idx) % num_recipients
                    recipient = rec[recipient_idx]

                    try:
                        msg = EmailMessage()
                        msg["From"] = email
                        msg["To"] = recipient
                        msg["Subject"] = account_subject
                        msg.set_content(text)
                        conn.send_message(msg)
                        log_sent()
                        sent_to.add(recipient)
                    except Exception as send_e:
                        log_error(f"[{email}] Send error in round {round_idx+1}: {send_e}")

                    t.sleep(PER_MSG_DELAY)

                    try:
                        barrier_end.wait()
                        barrier_start.wait()
                    except threading.BrokenBarrierError:
                        skip_catchup = True
                        break

                if not skip_catchup:
                    for recipient in rec:
                        if recipient not in sent_to:
                            try:
                                msg = EmailMessage()
                                msg["From"] = email
                                msg["To"] = recipient
                                msg["Subject"] = account_subject
                                msg.set_content(text)
                                conn.send_message(msg)
                                log_sent()
                                sent_to.add(recipient)
                            except Exception as send_e:
                                log_error(f"[{email}] Catch-up error: {send_e}")
                            t.sleep(PER_MSG_DELAY)
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
            th.join(timeout=120)

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