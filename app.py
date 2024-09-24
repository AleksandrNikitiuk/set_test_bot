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
import json
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
from warnings import filterwarnings
from telegram.warnings import PTBUserWarning

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
# set higher logging level for httpx to avoid all GET and POST requests being logged
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)

THEME, LEVEL, QUESTIONS, QUESTION, ANSWERS, ANSWER, CORRECT_ANSWER = range(7)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Starts creating a test."""
    
    context.user_data['user_name'] = update.message.from_user
    
    context.user_data['theme'] = ""
    context.user_data['level'] = ""
    context.user_data['questions'] = []
    context.user_data['question_number'] = 0
    context.user_data['enter_question'] = True
    
    buttons = [
        [
            InlineKeyboardButton(text="Новый тест", callback_data='new_test'),
            InlineKeyboardButton(text="Закончить", callback_data='end'),
        ],
    ]
    keyboard = InlineKeyboardMarkup(buttons)

    await update.message.reply_text(
        "Этот бот предназначен для создания тестов для HomeOfLanguagesBot. ",
        reply_markup=keyboard,
    )

    return THEME

async def ask_for_theme(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Asks for a test theme."""
    
    logger.info("User %s is starting to create a new test.", context.user_data.get('user_name').first_name)
    
    text = "Какая тема?"

    await update.callback_query.answer()
    await update.callback_query.edit_message_text(text=text)

    return LEVEL


async def save_theme_and_ask_for_level(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Saves the theme and asks for a test level."""
    
    context.user_data['theme'] = update.message.text
    logger.info("A theme is %s.", context.user_data.get('theme'))

    await update.message.reply_text(
        "Какой уровень?",
    )

    return QUESTIONS

async def questions(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Stores the selected level and asks for questions."""

    context.user_data['level'] = update.message.text
    logger.info("A level is %s.", context.user_data.get('level'))
    
    buttons = [
        [
            InlineKeyboardButton(text="Добавить новый вопрос", callback_data='new_question'),
            InlineKeyboardButton(text="Закончить", callback_data='end_questions'),
        ],
    ]
    keyboard = InlineKeyboardMarkup(buttons)

    await update.message.reply_text(
        "Добавить новый вопрос? ",
        reply_markup=keyboard,
    )

    return QUESTION

async def question(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Asks for a question."""
    
    if context.user_data.get('questions') == None:
        context.user_data['questions'] = []
        context.user_data['question_number'] = 0
    context.user_data['enter_question'] = True

    await update.callback_query.answer()
    await update.callback_query.edit_message_text(
        "_Если в вопросе предполагается пропуск, который должен заполнить ученик, напишите по английски слово_ *Answer* _или_ *answer* _в зависимости от того, в начале предложения находится слово или нет. Вопрос может быть введен на любом языке._\n\nВведите вопрос: "
    , parse_mode='Markdown')

    return ANSWERS

async def answers(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Stores the question and asks for a answer."""
    
    questions = context.user_data.get('questions')
    question_number = context.user_data.get('question_number')
    if context.user_data.get('enter_question'):
        question_with_answers = {'question': update.message.text.split(), 'answers': [], 'correct_answer': ""}
        questions.append(question_with_answers)
        context.user_data['enter_question'] = False
        context.user_data['answers_number'] = 0
    else:
        questions[question_number]['answers'].append(update.message.text)
        context.user_data['answers_number'] += 1
    context.user_data['questions'] = questions
    logger.info("Current question with answers are %s.", questions)
    
    buttons = [
        [
            InlineKeyboardButton(text="Добавить новый ответ", callback_data='new_answer'),
            InlineKeyboardButton(text="Закончить", callback_data='end'),
        ],
    ]
    keyboard = InlineKeyboardMarkup(buttons)

    await update.message.reply_text(
        "*Количество ответов: " + str(context.user_data.get('answers_number')) + ".*\n_Если введено менее двух вариантов ответов, то по нажатию на кнопки Закончить будут установлены варианты_ *True* _и_ *False*.\n\nДобавить новый ответ? ",
        reply_markup=keyboard,
        parse_mode='Markdown'
    )

    return ANSWER

async def answer(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Chooses the correct answer."""
    
    text = "Введите ответ: "

    await update.callback_query.answer()
    await update.callback_query.edit_message_text(text=text)

    return ANSWERS

async def generate_buttons(answers):
    "Generates the answers buttons for choosing correct answer."
    num_buttons = len(answers)
    buttons = []
    for i in range(1, num_buttons + 1):
        button = InlineKeyboardButton(text=answers[i - 1], callback_data=f'button_{i}')
        buttons.append(button)
    return [buttons]

async def end_answers(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Asks for a correct answer."""
    
    """buttons = [
        [
            InlineKeyboardButton(text="1", callback_data='one'),
            InlineKeyboardButton(text="2", callback_data='two'),
            InlineKeyboardButton(text="3", callback_data='three'),
            InlineKeyboardButton(text="4", callback_data='four'),
        ],
    ]"""
    questions = context.user_data.get('questions')
    question_number = context.user_data.get('question_number')

    if len(questions[question_number]['answers']) <= 1:
        questions[question_number]['answers'] = []
        questions[question_number]['answers'].append("True")
        questions[question_number]['answers'].append("False")
        context.user_data['questions'] = questions

    keyboard = InlineKeyboardMarkup( await generate_buttons(questions[question_number]['answers']) )

    text = "Какой ответ правильный? "

    await update.callback_query.answer()
    await update.callback_query.edit_message_text(text=text, reply_markup=keyboard)

    return CORRECT_ANSWER

async def correct_answer(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Stores the correct answer and asks for a new question."""
    
    questions = context.user_data.get('questions')
    question_number = context.user_data.get('question_number')
    context.user_data['question_number'] = question_number + 1
    correct_answer_button_name = update.callback_query.data
    match str(correct_answer_button_name):
        case "button_1":
            questions[question_number]['correct_answer'] = questions[question_number]['answers'][0]
        case "button_2":
            questions[question_number]['correct_answer'] = questions[question_number]['answers'][1]
        case "button_3":
            questions[question_number]['correct_answer'] = questions[question_number]['answers'][2]
        case "button_4":
            questions[question_number]['correct_answer'] = questions[question_number]['answers'][3]
    context.user_data['questions'] = questions
    logger.info("Correct answer is %s.", questions[question_number]['correct_answer'])
    
    buttons = [
        [
            InlineKeyboardButton(text="Добавить новый вопрос", callback_data='new_question'),
            InlineKeyboardButton(text="Закончить", callback_data='end_questions'),
        ],
    ]
    keyboard = InlineKeyboardMarkup(buttons)

    await update.callback_query.answer()
    await update.callback_query.edit_message_text(
        "*Количество вопросов: " + str(context.user_data['question_number']) + ".*\n\nДобавить новый вопрос?",
        reply_markup=keyboard,
        parse_mode='Markdown'
    )

    return QUESTION

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancels and ends the test creating. Saves data."""
    
    if not context.user_data.get('questions') is None:
        with open('test_data.json', 'w', encoding='utf-8') as test_data_json_file:
            json.dump([context.user_data.get('theme'), context.user_data.get('level')], test_data_json_file, ensure_ascii=False)
        with open('questions.json', 'w', encoding='utf-8') as questions_json_file:
            json.dump(context.user_data.get('questions'), questions_json_file, ensure_ascii=False)
    
    text = "До скорой встречи!"

    await update.callback_query.answer()
    await update.callback_query.edit_message_text(text=text)

    return  ConversationHandler.END


def main() -> None:
    """Run the bot."""
    # Create the Application and pass it your bot's token.
    application = Application.builder().token("7422563960:AAFYrkWObqC3iKx6mT7qg5qhzYUSdUW8cy4").build()

    filterwarnings(action="ignore", message=r".*CallbackQueryHandler", category=PTBUserWarning)

    # Add conversation handler with the states THEME, LEVEL, QUESTIONS, QUESTION, ANSWERS, ANSWER and CORRECT_ANSWER
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            THEME: [CallbackQueryHandler(ask_for_theme, pattern="^new_test$")],
            LEVEL: [MessageHandler(filters.TEXT, save_theme_and_ask_for_level)],
            QUESTIONS: [MessageHandler(filters.TEXT, questions)],
            QUESTION: [CallbackQueryHandler(question, pattern="^new_question$"),
                       CallbackQueryHandler(cancel, pattern="^end_questions$")],
            ANSWERS: [MessageHandler(filters.TEXT, answers)],
            ANSWER: [CallbackQueryHandler(answer, pattern="^new_answer$"),
                     CallbackQueryHandler(end_answers, pattern="^end$")],
            CORRECT_ANSWER: [CallbackQueryHandler(correct_answer, pattern="^button_1|button_2|button_3|button_4$")],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    application.add_handler(conv_handler)

    # Run the bot until the user presses Ctrl-C
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()