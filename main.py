from sqlite3 import OperationalError
import asyncio
import logging
import sys
from os import getenv
from dotenv import load_dotenv
import requests
from datetime import datetime, timedelta

import database as db

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, BotCommand
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext

load_dotenv()  # Подгружаем информацию из .env файла

TOKEN = getenv("BOT_TOKEN")
dp = Dispatcher()


# Создание библиотеки состояний, на основе которых изменяется поведение бота
class RegisterName(StatesGroup):
    first_ask_name = State()
    ask_name = State()


# Метод для создания базы данных (не создаётся, если уже есть)
async def on_startup():
    await db.db_start()


# Метод для создания командного меню
async def set_main_menu(bot: Bot):
    # Создаем список с командами и их описанием для кнопки menu
    main_menu_commands = [
        BotCommand(command='/help',
                   description='Справка по работе бота'),
        BotCommand(command='/get_rate',
                   description='Получить сегодняшний курс доллара'),
        BotCommand(command='/get_yesterday_rate',
                   description='Получить вчерашний курс доллара'),
        BotCommand(command='/change_name',
                   description='Изменить имя'),
        BotCommand(command='/about_bot',
                   description='О боте')
    ]
    await bot.set_my_commands(main_menu_commands)


# Метод для получаения курса валют из локального файла
async def get_valutes_rate():
    reader = open("rates.txt")
    data = reader.read()
    reader.close()
    data = eval(data)
    return data


# Стартовый метод. Если взаимодействие происходит не в первый раз, сообщает, что бот уже знаком с пользователем.
# Также меняет состояние для принятия первого имени пользователя
@dp.message(CommandStart())
async def command_start_handler(message: Message, state: FSMContext) -> None:
    # await message.answer(f"Hello, {html.bold(message.from_user.full_name)}!")  # Обращение по логину
    try:
        user = await db.get_user(message.from_user.id)  # None, если пользователя нет
        if user:
            valutes_rate = await get_valutes_rate()
            rate = valutes_rate["Valute"]["USD"]["Value"]
            hello = f"{user[1]}, мы с вами уже знакомы, если вы хотели изменить имя, " \
                    f"необходимо воспользоваться командой " \
                    f"/change_name. Курс доллара сегодня {rate}р"
            await message.answer(hello)
        else:
            await state.set_state(RegisterName.first_ask_name)
            await message.answer("Добрый день. Как вас зовут?")
    except OperationalError:
        await message.answer("К сожалению, возникли проблемы с регистрацией. Попробуйте зарегистрироваться позже")


# Метод для добавления пользователя в базу данных. Меняет состояние в None
@dp.message(RegisterName.first_ask_name)
async def set_first_name(message: Message, state: FSMContext) -> None:
    try:
        valutes_rate = await get_valutes_rate()
        rate = valutes_rate["Valute"]["USD"]["Value"]
        await db.add_user(message.from_user.id, message.text, datetime.isoformat(datetime.now()))
        hello = f"Рад знакомству, {message.text}! Курс доллара сегодня {rate}р"
        await message.answer(hello)
    except OperationalError:
        await message.answer("Не удалось зарегистрировать имя, попробуйте немного позже")
    finally:
        await state.set_state(None)


# Метод, обрабатывающий команду /help (сообщение с подсказками о пользовании ботом)
@dp.message(Command("help"))
async def help_with_command(message: Message) -> None:
    text = "\U0001F315 Список всех команд Вы можете посмотреть в меню\n" \
           "\U0001F316 Хотите узнать сегодняшний курс доллара?\nКоманда /get_rate\n" \
           "\U0001F317 Хотите узнать вчерашний курс доллара?\nКоманда /get_yesterday_rate\n" \
           "\U0001F318 Хотите изменить имя?\nКоманда /change_name (не чаще, чем раз в 10 минут)\n" \
           "\U0001F311 Хотите узнать о встретившихся проблемах и путях их решения?\nКоманда /about_bot"
    try:
        user = await db.get_user(message.from_user.id)  # None, если пользователя нет
        first_line = f"{user[1]}, вот подсказки, которые помогут в работте с ботом\n"
        await message.answer(first_line + text)
    except OperationalError:
        first_line = f"Вот подсказки, которые помогут в работте с ботом\n"
        await message.answer(first_line + text)
    except TypeError:
        first_line = f"Вот подсказки, которые помогут в работте с ботом\n"
        await message.answer(first_line + text)
        await message.answer("Вы не зарегистрированы в системе. Зарегистрируйтесь по команде /start")


# Метод, обрабатывающий команду /get_rate. Сообщение с курсом на сегодня
@dp.message(Command("get_rate"))
async def get_rate(message: Message) -> None:
    try:
        user = await db.get_user(message.from_user.id)  # None, если пользователя нет
        valutes_rate = await get_valutes_rate()
        rate = valutes_rate["Valute"]["USD"]["Value"]
        await message.answer(f"{user[1]}, курс доллара сегодня {rate}р")
    except OperationalError:
        valutes_rate = await get_valutes_rate()
        rate = valutes_rate["Valute"]["USD"]["Value"]
        await message.answer(f"Курс доллара сегодня {rate}р")
    except TypeError:
        valutes_rate = await get_valutes_rate()
        rate = valutes_rate["Valute"]["USD"]["Value"]
        await message.answer(f"Курс доллара сегодня {rate}р")
        await message.answer("Вы не зарегистрированы в системе. Зарегистрируйтесь по команде /start")


# Метод, обрабатывающий команду /get_yesterday_rate. Сообщение с курсом на вчера
@dp.message(Command("get_yesterday_rate"))
async def get_yesterday_rate(message: Message) -> None:
    try:
        user = await db.get_user(message.from_user.id)  # None, если пользователя нет
        valutes_rate = await get_valutes_rate()
        rate = valutes_rate["Valute"]["USD"]["Previous"]
        await message.answer(f"{user[1]}, курс доллара вчера {rate}р")
    except OperationalError:
        valutes_rate = await get_valutes_rate()
        rate = valutes_rate["Valute"]["USD"]["Previous"]
        await message.answer(f"Курс доллара вчера {rate}р")
    except TypeError:
        valutes_rate = await get_valutes_rate()
        rate = valutes_rate["Valute"]["USD"]["Previous"]
        await message.answer(f"Курс доллара вчера {rate}р")
        await message.answer("Вы не зарегистрированы в системе. Зарегистрируйтесь по команде /start")


# Метод, обрабатывающий команду /change_name. Меняет состояние для принятия нового имени
@dp.message(Command("change_name"))
async def ask_change_name(message: Message, state: FSMContext) -> None:
    try:
        user = await db.get_user(message.from_user.id)  # None, если пользователя нет
        if user:
            last_time = datetime.fromisoformat(user[2])
            now_time = datetime.now()
            if now_time - last_time > timedelta(minutes=10):
                await state.set_state(RegisterName.ask_name)
                await message.answer(f"{user[1]}, решили сменить имя? Введите то, которое вы выбрали")
            else:
                await message.answer(f"{user[1]}, нельзя менять имя чаще, чем раз в 10 минут")
        else:
            await message.answer(f"Перед тем, как сменить имя, сначала зарегистрируйтесь, используя команду /start")
    except OperationalError:
        await message.answer("К сожалению, возникли проблемы с изменением имени. Попробуйте изменить имя позже")


# Метод бновляет имя в бд и сообщает об этом. Возвращает состояние в None
@dp.message(RegisterName.ask_name)
async def set_name(message: Message, state: FSMContext) -> None:
    try:
        valutes_rate = await get_valutes_rate()
        rate = valutes_rate["Valute"]["USD"]["Value"]
        hello = f"Рад новому знакомству, {message.text}! Курс доллара сегодня {rate}р"
        await db.update_user(message.from_user.id, message.text, datetime.now())
        await message.answer(hello)
    except OperationalError:
        await message.answer("Не удалось обновить имя, попробуйте немного позже")
    finally:
        await state.set_state(None)


# Метод, обрабатывающий команду /about_bot. Выводит сообщение с проблемами и решениями
@dp.message(Command("about_bot"))
async def about_bot(message: Message) -> None:
    try:
        user = await db.get_user(message.from_user.id)  # None, если пользователя нет
        reader = open("about_bot.txt", encoding="utf-8")
        # reader = open("about_bot.txt")
        data = f"{user[1]}, вот, какие проблемы мне встретились и как я их решал\n" + reader.read()
        reader.close()
        await message.answer(data)
        # await message.answer("\U00002705")
    except OperationalError:
        reader = open("about_bot.txt", encoding="utf-8")
        data = f"Вот, какие проблемы мне встретились и как я их решал\n" + reader.read()
        reader.close()
        await message.answer(data)
    except TypeError:
        reader = open("about_bot.txt", encoding="utf-8")
        data = f"Вот, какие проблемы мне встретились и как я их решал\n" + reader.read()
        reader.close()
        await message.answer(data)
        await message.answer("Вы не зарегистрированы в системе. Зарегистрируйтесь по команде /start")


# Метод, обрабатывающие обычные сообщения. Сообщает, что бот управляется с помощью команд
@dp.message()
async def echo_handler(message: Message) -> None:
    try:
        user = await db.get_user(message.from_user.id)  # None, если пользователя нет
        await message.answer(f"{user[1]}, для взаимодействия с ботом используйте команды.\n"
                             f"Подсказки вы можете получить, используя команду /help")
    except OperationalError:
        await message.answer(f"Для взаимодействия с ботом используйте команды.\n"
                             f"Подсказки вы можете получить, используя команду /help")
    except TypeError:
        await message.answer(f"Для взаимодействия с ботом используйте команды.\n"
                             f"Подсказки вы можете получить, используя команду /help")
        #                      f"Вы не зарегистрированы в системе. Зарегистрируйтесь по команде /start")
        await message.answer("Вы не зарегистрированы в системе. Зарегистрируйтесь по команде /start")


# Метод, который раз в 20 секунд обновляет файл с курсами валют
async def update_rate():
    while True:
        response = requests.get("https://www.cbr-xml-daily.ru/daily_json.js")

        writer = open('rates.txt', 'w')
        writer.write(response.text)
        writer.close()

        await asyncio.sleep(20)


# Основной метод, который запускает бота
async def main() -> None:
    bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))

    task1 = update_rate()
    task2 = asyncio.create_task(dp.start_polling(bot))

    await task1
    await task2


#  Метод, с которого всё начинается. Также вызывает создание меню для бота и создание бд
if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG, stream=sys.stdout)
    dp.startup.register(set_main_menu)
    dp.startup.register(on_startup)

    asyncio.run(main())
