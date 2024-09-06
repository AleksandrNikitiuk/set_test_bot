#!/usr/bin/env python
# pylint: disable=unused-argument
# This program is dedicated to the public domain under the CC0 license.

"""
First, a few callback functions are defined. Then, those functions are passed to
the Application and registered at their respective places.
Then, the bot is started and runs until we press Ctrl-C on the command line.

Usage:
Example of a bot-user conversation using ConversationHandler.
Send /start to initiate the conversation.
Press Ctrl-C on the command line or send a signal to the process to stop the
bot.
"""

import logging

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
    CallbackQueryHandler,
)

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
# set higher logging level for httpx to avoid all GET and POST requests being logged
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)

THEME, LEVEL, QUESTIONS, QUESTION, ANSWERS, ANSWER = range(6)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Starts the conversation and asks the user about their gender."""
    buttons = [
        [
            InlineKeyboardButton(text="Add new test", callback_data='new_test'),
            InlineKeyboardButton(text="Done", callback_data='end'),
        ],
    ]
    keyboard = InlineKeyboardMarkup(buttons)

    await update.message.reply_text(
        "Этот бот предназначен для создания тестов для HomeOfLanguagesBot. ",
        reply_markup=keyboard,
    )

    return THEME

async def ask_for_theme(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Prompt user to input data for selected feature."""
    text = "Какая тема?"

    await update.callback_query.answer()
    await update.callback_query.edit_message_text(text=text)

    return LEVEL


async def save_theme_and_ask_for_level(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Asks for a theme."""
    
    await update.message.reply_text(
        "Какой уровень?",
    )

    return QUESTIONS

async def questions(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Stores the selected theme and asks for a level."""
    
    buttons = [
        [
            InlineKeyboardButton(text="Add new question", callback_data='new_question'),
            InlineKeyboardButton(text="Done", callback_data='end'),
        ],
    ]
    keyboard = InlineKeyboardMarkup(buttons)

    await update.message.reply_text(
        "Добавить новый вопрос? ",
        reply_markup=keyboard,
    )

    return QUESTION

async def question(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Asks for a theme."""
    
    text = "Введите вопрос: "

    await update.callback_query.answer()
    await update.callback_query.edit_message_text(text=text)

    return ANSWERS

async def answers(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Stores the selected theme and asks for a level."""
    
    buttons = [
        [
            InlineKeyboardButton(text="Add new answer", callback_data='new_answer'),
            InlineKeyboardButton(text="Done", callback_data='end'),
        ],
    ]
    keyboard = InlineKeyboardMarkup(buttons)

    await update.message.reply_text(
        "Добавить новый ответ? ",
        reply_markup=keyboard,
    )

    return ANSWER

async def answer(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Asks for a theme."""
    
    text = "Введите ответ: "

    await update.callback_query.answer()
    await update.callback_query.edit_message_text(text=text)

    return ANSWERS

async def end(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Asks for a theme."""
    text = "Какой ответ правильный? "

    await update.callback_query.answer()
    await update.callback_query.edit_message_text(text=text)

    return QUESTIONS


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancels and ends the conversation."""
    user = update.message.from_user
    logger.info("User %s canceled the conversation.", user.first_name)
    await update.message.reply_text(
        "Bye! I hope we can talk again some day.", reply_markup=ReplyKeyboardRemove()
    )

    return ConversationHandler.END


def main() -> None:
    """Run the bot."""
    # Create the Application and pass it your bot's token.
    application = Application.builder().token("7422563960:AAFYrkWObqC3iKx6mT7qg5qhzYUSdUW8cy4").build()

    # Add conversation handler with the states GENDER, PHOTO, LOCATION and BIO
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            THEME: [CallbackQueryHandler(ask_for_theme, pattern="^new_test$")],
            LEVEL: [MessageHandler(filters.TEXT, save_theme_and_ask_for_level)],
            QUESTIONS: [MessageHandler(filters.TEXT, questions)],
            QUESTION: [CallbackQueryHandler(question, pattern="^new_question$")],
            ANSWERS: [MessageHandler(filters.TEXT, answers)],
            ANSWER: [CallbackQueryHandler(answer, pattern="^new_answer$"),
                     CallbackQueryHandler(end, pattern="^end$")],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    application.add_handler(conv_handler)

    # Run the bot until the user presses Ctrl-C
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()