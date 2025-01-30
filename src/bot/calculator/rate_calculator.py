

def calculate_water_rate(weigth: float, activity_minutes: float) -> float:
    return weigth * 30 + activity_minutes / 30 * 500
    
    
def calculate_calory_rate(weigth: float, heigth: float, age: int, activity_minutes: float) -> float:
    return 10 * weigth + 6.25 * heigth - 5 * age + activity_minutes / 30 * 300