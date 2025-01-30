from aiogram import types, F, Router
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
import logging

from storage.states import UserForm
from calculator.rate_calculator import calculate_water_rate, calculate_calory_rate

user_data = {}

router = Router()

@router.message(Command("set_profile"))
async def start_handler(msg: Message, state: FSMContext):
    await msg.answer("Введите имя пользователя:")
    await state.update_data(chat_id=msg.chat.id)
    await state.set_state(UserForm.name)
    
@router.message(UserForm.name)
async def start_handler(msg: Message, state: FSMContext):
    await state.update_data(name=msg.text)
    await msg.answer("Введите ваш вес (в кг):")
    await state.set_state(UserForm.weigth)
    
@router.message(UserForm.weigth)
async def start_handler(msg: Message, state: FSMContext):
    await state.update_data(weigth=msg.text)
    await msg.answer("Введите ваш рост:")
    await state.set_state(UserForm.heigth)
    
@router.message(UserForm.heigth)
async def start_handler(msg: Message, state: FSMContext):
    await state.update_data(heigth=msg.text)
    await msg.answer("Введите ваш возраст:")
    await state.set_state(UserForm.age)
    
@router.message(UserForm.age)
async def start_handler(msg: Message, state: FSMContext):
    await state.update_data(age=msg.text)
    await msg.answer("Какое среднее время вашей дневной активности (в минутах):")
    await state.set_state(UserForm.activity_minutes)
    
@router.message(UserForm.activity_minutes)
async def start_handler(msg: Message, state: FSMContext):
    await state.update_data(activity_minutes=msg.text)
    await msg.answer("Введите населенный пункт, в котором вы проживаете:")
    await state.set_state(UserForm.city)
    
@router.message(UserForm.city)
async def start_handler(msg: Message, state: FSMContext):
    await state.update_data(city=msg.text)
    await msg.answer("Введите вашу цель по калориям (оставьте пустым для автоматического расчета):")
    await state.set_state(UserForm.calory_target)
    
@router.message(UserForm.calory_target)
async def start_handler(msg: Message, state: FSMContext):
    await state.update_data(calory_target=msg.text)
    data = await state.get_data()
    chat_id = data.get("chat_id")
    data.pop("chat_id")
    
    weigth = float(data["weigth"])
    activity_minutes = float(data["activity_minutes"])
    heigth = float(data["heigth"])
    age = int(data["age"])

    water_rate = calculate_water_rate(weigth, activity_minutes)
    calory_rate = calculate_calory_rate(weigth, heigth, age, activity_minutes)
    data["water_rate"] = water_rate
    data["current_water"] = 0
    data["calory_rate"] = calory_rate
    data["current_calory"] = 0
    
    global user_data
    user_data[chat_id] = data

    await msg.answer(f"Ваш профиль = {data}")
    await state.clear()
    
@router.message(Command("profile"))
async def start_handler(msg: Message):
    if (msg.chat.id in user_data.keys()):
        await msg.answer(f"Ваш профиль = {user_data[msg.chat.id]}")
    else:
        await msg.answer(f"У вас нет активного профиля. Для создания выполните команду /set_profile")
        
@router.message(Command("log_water"))
async def start_handler(msg: Message):
    if (msg.chat.id not in user_data.keys()):
        await msg.answer(f"У вас нет активного профиля. Для создания выполните команду /set_profile")
        return
    data = user_data[msg.chat.id]
    
    water = float(msg.text.split()[1])
    current_water = float(data["current_water"]) + water
    data["current_water"] = current_water
    water_remain = float(data["water_rate"]) - current_water
    
    if (water_remain <= 0):
        await msg.answer(f"Норма воды выполнена")
    else:
        await msg.answer(f"Текущее количество выпитой воды: {current_water}, осталось для выполнения нормы: {water_remain}")
    
@router.message(Command("load_test_user"))
async def start_handler(msg: Message):

    weigth = 75
    heigth = 180
    age = 24
    city = "Moscow"
    activity_minutes = 30

    data = {}
    water_rate = calculate_water_rate(weigth, activity_minutes)
    calory_rate = calculate_calory_rate(weigth, heigth, age, activity_minutes)
    data["water_rate"] = water_rate
    data["current_water"] = 0
    data["calory_rate"] = calory_rate
    data["current_calory"] = 0
    
    data["name"] = "Кирилл"
    data["city"] = city
    
    global user_data
    user_data[257377723] = data

    await msg.answer(f"Ваш профиль = {user_data}")
    