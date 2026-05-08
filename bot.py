import os
import asyncio
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters, ConversationHandler
import httpx
from utils import find_rrb_result

BOT_TOKEN = os.environ.get("8640224009:AAGr1DPdJVLnsLK5hLNsNKlzF8AdEyzxgbc")

# Conversation states
EXAM, YEAR = range(2)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Hi! I can provide RRB exam results.\nType 'rrb ntpc' or 'group d' to start."
    )

async def exam_choice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.lower()
    if "rrb" in text and "ntpc" in text:
        context.user_data['exam'] = "NTPC"
    elif "group d" in text:
        context.user_data['exam'] = "Group D"
    else:
        await update.message.reply_text("Invalid choice. Type 'rrb ntpc' or 'group d'.")
        return EXAM

    await update.message.reply_text("Which year do you want the result for?")
    return YEAR

async def year_choice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    year = update.message.text.strip()
    context.user_data['year'] = year
    exam = context.user_data['exam']

    async with httpx.AsyncClient() as session:
        result = await find_rrb_result(session, exam, year)
        if result:
            await update.message.reply_text(
                f"Exam: {exam} {year}\n"
                f"Status: {result['status']}\n"
                f"Result Date: {result['result_date']}\n"
                f"Link: {result['link']}"
            )
        else:
            await update.message.reply_text("No result found for this year.")
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Cancelled.")
    return ConversationHandler.END

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[MessageHandler(filters.TEXT & (~filters.COMMAND), exam_choice)],
        states={
            EXAM: [MessageHandler(filters.TEXT & (~filters.COMMAND), exam_choice)],
            YEAR: [MessageHandler(filters.TEXT & (~filters.COMMAND), year_choice)],
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )

    app.add_handler(CommandHandler("start", start))
    app.add_handler(conv_handler)
    app.run_polling()

if __name__ == "__main__":
    main()
