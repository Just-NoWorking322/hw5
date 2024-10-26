
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import CommandStart
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from config import token
import asyncio
import logging
import sqlite3

bot = Bot(token=token)
dp = Dispatcher()

connection = sqlite3.connect("brunos.db")
cursor = connection.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS brunos (
    id INTEGER PRIMARY KEY,
    user_name TEXT,
    full_name TEXT,
    age INTEGER,
    telephone_number TEXT,
    e_mail TEXT
);
""")

start_buttons = [
    [KeyboardButton(text="Зарегистрироваться"), KeyboardButton(text="/profile")],
    [KeyboardButton(text="Помощь"), KeyboardButton(text="/menu")],
    [KeyboardButton(text="Создатели")]
]
start_keyboard = ReplyKeyboardMarkup(keyboard=start_buttons, resize_keyboard=True, one_time_keyboard=True)

confirm_buttons = [
    [InlineKeyboardButton(text="нет ❌", callback_data="not"), InlineKeyboardButton(text="да ✅", callback_data="yes")]
]
confirm_keyboard = InlineKeyboardMarkup(inline_keyboard=confirm_buttons)

class Register(StatesGroup):
    user_name = State()
    full_name = State()
    age = State()
    telephone_number = State()
    e_mail = State()

@dp.message(CommandStart())
async def start(message: types.Message):
    await message.answer(f"Привет, {message.from_user.full_name}!", reply_markup=start_keyboard)

@dp.message(F.text == "Зарегистрироваться")
async def register_start(message: types.Message, state: FSMContext):
    await message.answer("Введите ФИО:")
    await state.set_state(Register.full_name)

@dp.message(F.text == "Создатели")
async def razrab(message: types.Message):
    await message.answer("@bnshiro")
    

@dp.message(Register.full_name)
async def register_age(message: types.Message, state: FSMContext):
    await state.update_data(full_name=message.text)
    await message.answer("Введите возраст:")
    await state.set_state(Register.age)

@dp.message(Register.age)
async def register_telephone(message: types.Message, state: FSMContext):
    await state.update_data(age=message.text)
    await message.answer("Введите номер телефона:")
    await state.set_state(Register.telephone_number)

@dp.message(Register.telephone_number)
async def register_email(message: types.Message, state: FSMContext):
    await state.update_data(telephone_number=message.text)
    await message.answer("Введите email:")
    await state.set_state(Register.e_mail)

@dp.message(Register.e_mail)
async def confirm_data(message: types.Message, state: FSMContext):
    await state.update_data(e_mail=message.text)
    data = await state.get_data()
    
    full_name = data["full_name"]
    age = data["age"]
    telephone_number = data["telephone_number"]
    e_mail = data["e_mail"]
    
    await message.answer(
        f"""Подтвердите данные:
        ФИО: {full_name}
        Возраст: {age}
        Номер телефона: {telephone_number}
        Email: {e_mail}
        """, reply_markup=confirm_keyboard
    )

@dp.callback_query(F.data == "yes")
async def save_data(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    cursor.execute(
        "INSERT INTO brunos (id, full_name, age, telephone_number, e_mail) VALUES (?, ?, ?, ?, ?)",
            (callback.from_user.id, data["full_name"], data["age"], data["telephone_number"], data["e_mail"])
        )
    connection.commit()
        
    await callback.answer("Данные сохранены!")
    await callback.message.edit_text("Регистрация завершена")
    await state.clear()

@dp.callback_query(F.data == "not")
async def cancel_data(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer("Регистрация отменена.")
    await state.clear()

@dp.message(F.text == "/profile")
async def show_profile(message: types.Message):
    cursor.execute("SELECT * FROM brunos WHERE id = ?", (message.from_user.id,))
    user_data = cursor.fetchone()
    
    if user_data:
        await message.answer(
            f"""Ваш профиль:
            ФИО: {user_data[2]}
            Возраст: {user_data[3]}
            Номер телефона: {user_data[4]}
            Email: {user_data[5]}
            """
        )
    else:
        await message.answer("Вы не зарегистрированы. Используйте /start для регистрации.")

@dp.message(F.text == "/menu")
async def show_menu(message: types.Message):
    menu_buttons = [
        [KeyboardButton(text="Информация"), KeyboardButton(text="Помощь")]
    ]
    menu_keyboard = ReplyKeyboardMarkup(keyboard=menu_buttons, resize_keyboard=True, one_time_keyboard=True)
    await message.answer("Выберите опцию:", reply_markup=menu_keyboard)

@dp.message(F.text == "Информация")
async def info(message: types.Message):
    await message.answer("Бот не иммеет определенных задач кроме регистрации на данный момент")

@dp.message(F.text == "Помощь")
async def help(message: types.Message):
    await message.answer("Вам нужна помощь? пишите в telegram: @bnshiro")


async def main():
    logging.basicConfig(level="INFO")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
