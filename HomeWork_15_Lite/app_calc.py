from fastapi import FastAPI
from pydantic import BaseModel
import requests

app = FastAPI()

class Numbers(BaseModel):
    a: int
    b: int

@app.post("/add")
def add(numbers: Numbers):
    return f'{numbers.a} + {numbers.b} = {numbers.a + numbers.b}'

@app.post("/subtract")
def subtract(numbers: Numbers):
    return f'{numbers.a} - {numbers.b} = {numbers.a - numbers.b}'

@app.post("/multiply")
def multiply(numbers: Numbers):
    return f'{numbers.a} * {numbers.b} = {numbers.a * numbers.b}'

@app.post("/divide")
def divide(numbers: Numbers):
    if numbers.b == 0:
        return {"error": "Division by zero is not allowed"}
    return f'{numbers.a} / {numbers.b} = {numbers.a // numbers.b}'

# Запуск сервера:
# uvicorn app_calc:app --reload

if __name__ == "__main__":
    nums = Numbers(a=10, b=2)
    print(add(nums))
    print(subtract(nums))
    print(multiply(nums))
    print(divide(nums))