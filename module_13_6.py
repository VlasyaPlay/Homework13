from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import asyncio


api = ''
bot = Bot(token=api)
dp = Dispatcher(bot, storage=MemoryStorage())

kb = ReplyKeyboardMarkup(resize_keyboard=True)
button = KeyboardButton(text='Рассчитать')
button2 = KeyboardButton(text='Информация')
kb.add(button)
kb.add(button2)

kb2 = InlineKeyboardMarkup(resize_keyboard=True)
in_line_button = InlineKeyboardButton(text='Рассчитать норму калорий', callback_data='calories')
in_line_button2 = InlineKeyboardButton(text='Формулы расчета', callback_data='formulas')
kb2.add(in_line_button)
kb2.add(in_line_button2)


class UserState(StatesGroup):
    age = State()
    growth = State()
    weight = State()


@dp.message_handler(text='Рассчитать')
async def main_menu(message):
    await message.answer('Выбирете опцию', reply_markup=kb2)


@dp.callback_query_handler(text='formulas')
async def get_formulas(call):
    await call.message.answer('(10 × вес в кг) + (6,25 × рост в см) − (5 × возраст в годах) + 5')
    await call.answer()


@dp.message_handler(commands=['start'])
async def start(message):
    await message.answer('Выбирете действие', reply_markup=kb)


@dp.message_handler(text='Информация')
async def inform(message):
    await message.answer('Для рассчета калорий нажмите на "Рассчитать"')


@dp.callback_query_handler(text='calories')
async def set_age(call):
    await call.message.answer('Введите свой возраст')
    await call.answer()
    await UserState.age.set()


@dp.message_handler(state=UserState.age)
async def set_growth(message, state):
    await state.update_data(age=message.text)
    await message.answer('Введите свой рост')
    await UserState.growth.set()


@dp.message_handler(state=UserState.growth)
async def set_weight(message, state):
    await state.update_data(growth=message.text)
    await message.answer('Введите свой вес')
    await UserState.weight.set()


@dp.message_handler(state=UserState.weight)
async def send_calories(message, state):
    await state.update_data(weight=message.text)
    data = await state.get_data()
    age = float(data['age'])
    growth = float(data['growth'])
    weight = float(data['weight'])

    fms = 10 * weight + 6.25 * growth - 5 * age + 5
    calories = fms * 1.2

    await message.answer(calories)
    await state.finish()


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)