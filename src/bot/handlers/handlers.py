from aiogram import types, F, Router
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from storage.states import UserForm

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
    
    global user_data
    user_data[chat_id] = data

    await msg.answer(f"Ваш профиль = {user_data}")
    await state.clear()
    
@router.message(Command("profile"))
async def start_handler(msg: Message):
    if (msg.chat.id in user_data.keys()):
        await msg.answer(f"Ваш профиль = {user_data[msg.chat.id]}")
    else:
        await msg.answer(f"У вас нет активного профиля. Для создания выполните команду /set_profile")