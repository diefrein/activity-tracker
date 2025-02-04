from aiogram.fsm.state import State, StatesGroup

class UserForm(StatesGroup):
    name = State()
    weigth = State()
    heigth = State()
    age = State()
    activity_minutes = State()
    city = State()
    calory_target = State()
    
class FoodForm(StatesGroup):
    food_amount = State()