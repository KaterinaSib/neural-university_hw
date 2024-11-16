from fastapi import FastAPI
from chunks import Chunk
from pydantic import BaseModel

data_from_url= "https://docs.google.com/document/d/11MU3SnVbwL_rM-5fIC14Lc3XnbAV4rY1Zd_kpcMuH4Y"

# инициализация индексной базы
chunk = Chunk(path_to_base=data_from_url)

# класс с типами данных параметров 
class Item(BaseModel): 
    text: str

count = 0
# создаем объект приложения
app = FastAPI()

# функция обработки get запроса + декоратор 
@app.get("/")
def read_root():
    return {f"message": f"Общее количество обращений: {count}"}

# функция обработки post запроса + декоратор 
@app.post("/api/get_answer")
def get_answer(question: Item):
    global count
    count += 1
    answer = chunk.get_answer(query=question.text)
    return {"message": answer}

# Запуск сервера:
# uvicorn main:app --reload
