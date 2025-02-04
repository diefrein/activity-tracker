import json
import logging
import random
from aiogram import types, F, Router
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
import requests

from storage.states import FoodForm, UserForm
from calculator.rate_calculator import calculate_water_rate, calculate_calory_rate

open_food_url = "http://world.openfoodfacts.org"

user_data = {}

router = Router()

@router.message(Command("set_profile"))
async def set_profile(msg: Message, state: FSMContext):
    await msg.answer("Введите имя пользователя:")
    await state.update_data(chat_id=msg.chat.id)
    await state.set_state(UserForm.name)
    
@router.message(UserForm.name)
async def name(msg: Message, state: FSMContext):
    await state.update_data(name=msg.text)
    await msg.answer("Введите ваш вес (в кг):")
    await state.set_state(UserForm.weigth)
    
@router.message(UserForm.weigth)
async def weigth(msg: Message, state: FSMContext):
    await state.update_data(weigth=msg.text)
    await msg.answer("Введите ваш рост:")
    await state.set_state(UserForm.heigth)
    
@router.message(UserForm.heigth)
async def heigth(msg: Message, state: FSMContext):
    await state.update_data(heigth=msg.text)
    await msg.answer("Введите ваш возраст:")
    await state.set_state(UserForm.age)
    
@router.message(UserForm.age)
async def age(msg: Message, state: FSMContext):
    await state.update_data(age=msg.text)
    await msg.answer("Какое среднее время вашей дневной активности (в минутах):")
    await state.set_state(UserForm.activity_minutes)
    
@router.message(UserForm.activity_minutes)
async def activity_minutes(msg: Message, state: FSMContext):
    await state.update_data(activity_minutes=msg.text)
    await msg.answer("Введите населенный пункт, в котором вы проживаете:")
    await state.set_state(UserForm.city)
    
@router.message(UserForm.city)
async def city(msg: Message, state: FSMContext):
    await state.update_data(city=msg.text)
    await msg.answer("Введите вашу цель по калориям (оставьте пустым для автоматического расчета):")
    await state.set_state(UserForm.calory_target)
    
@router.message(UserForm.calory_target)
async def calory_target(msg: Message, state: FSMContext):
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
    data["burnt_calory"] = 0
    
    global user_data
    user_data[chat_id] = data

    await msg.answer(f"Ваш профиль = {data}")
    await state.clear()
    
@router.message(Command("profile"))
async def profile(msg: Message):
    if (msg.chat.id in user_data.keys()):
        await msg.answer(f"Ваш профиль = {user_data[msg.chat.id]}")
    else:
        await msg.answer(f"У вас нет активного профиля. Для создания выполните команду /set_profile")
        
@router.message(Command("log_water"))
async def log_water(msg: Message):
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
        
@router.message(Command("log_workout"))
async def log_workout(msg: Message):
    if (msg.chat.id not in user_data.keys()):
        await msg.answer(f"У вас нет активного профиля. Для создания выполните команду /set_profile")
        return
    data = user_data[msg.chat.id]
    
    workout_type = msg.text.split()[1]
    workout_duration = float(msg.text.split()[2])
    burnt_calory = (1 + random.uniform(0.1, 0.5)) * 200 * workout_duration / 30
    
    data["burnt_calory"] += burnt_calory
    message = f"{workout_type} - {int(burnt_calory)} калорий."
    
    additional_water = 200 * workout_duration / 30
    if (additional_water > 0):
        message += f" Дополнительно: выпейте {int(additional_water)} мл воды."
   
    await msg.answer(message)
    
@router.message(Command("check_progress"))
async def check_progress(msg: Message):
    if (msg.chat.id not in user_data.keys()):
        await msg.answer(f"У вас нет активного профиля. Для создания выполните команду /set_profile")
        return
    data = user_data[msg.chat.id]
    
    current_water = data["current_water"]
    remain_water = data["water_rate"] - current_water
    
    current_calory = data["current_calory"]
    calory_rate = data["calory_rate"]
    burnt_calory = data["burnt_calory"]
    
    message = f"""
    Прогресс:
    Вода:
    - Выпито: {int(current_water)} мл из {int(data["water_rate"])} мл.
    - Осталось: {int(remain_water)} мл.
    
    Калории:
    - Потреблено: {int(current_calory)} ккал из {int(calory_rate)} ккал.
    - Сожжено: {int(burnt_calory)} ккал.
    - Баланс: {int(current_calory - burnt_calory)} ккал.
    """
    await msg.answer(message)
    
@router.message(Command("log_food"))
async def log_food(msg: Message, state: FSMContext):
    if (msg.chat.id not in user_data.keys()):
        await msg.answer(f"У вас нет активного профиля. Для создания выполните команду /set_profile")
        return
    
    product_name = msg.text.split()[1]
    
    params = {
        "categories_tags": {product_name}, 
        "page_size": 10
    }

    request = open_food_url + "/api/v2/search"
    response = requests.get(request, params = params)
    json_data = json.loads(response.text)
    # logging.info(f"json_data = {json_data}")
    
    energy_kcal = 0
    for product in json_data["products"]:
        nutriments = product["nutriments"]
        if ("energy-kcal" in nutriments.keys()):
            energy_kcal = nutriments["energy-kcal"]
            break
            
    if (energy_kcal > 0):
        await state.update_data(product_name=product_name)
        await state.update_data(energy_kcal=energy_kcal)
        await state.set_state(FoodForm.food_amount)
        await msg.answer(f"{product_name} - {energy_kcal} ккал на 100 г. Сколько грамм вы съели?")
    else:
        await msg.answer(f"Указанный продукт не найден")
    
@router.message(FoodForm.food_amount)
async def food_amount(msg: Message, state: FSMContext):
    if (msg.chat.id not in user_data.keys()):
        await msg.answer(f"У вас нет активного профиля. Для создания выполните команду /set_profile")
        return
    data = user_data[msg.chat.id]

    food_amount = float(msg.text.split()[0])
    state_data = await state.get_data()
    energy_kcal = state_data.get("energy_kcal")
    
    consumed_calory = energy_kcal * float(food_amount / 100)
    data["current_calory"] += consumed_calory
    
    await msg.answer(f"Записано: {int(consumed_calory)} ккал.")
    await state.clear()
    
@router.message(Command("load_test_user"))
async def load_test_user(msg: Message):

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
    data["burnt_calory"] = 0

    data["name"] = "Кирилл"
    data["city"] = city
    
    global user_data
    user_data[257377723] = data

    await msg.answer(f"Ваш профиль = {user_data}")
    