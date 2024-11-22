from fastapi import FastAPI
from chunks import Chunk
from pydantic import BaseModel

# инициализация индексной базы
chunk = Chunk(path_to_base="Simble.txt")

# класс с типами данных параметров 
class Item(BaseModel): 
    text: str

# создаем объект приложения
app = FastAPI()

# функция обработки get запроса + декоратор 
@app.get("/")
def read_root():
    return {"message": "answer"}

# функция обработки post запроса + декоратор 
@app.post("/api/get_answer")
async def get_answer(question: Item):
    answer = await chunk.get_answer(query=question.text)
    return {"message": answer}

# функция обработки асинхронного post запроса + декоратор 
@app.post("/api/get_answer_async")
async def get_answer(question: Item):
    answer = await chunk.get_answer(query=question.text)
    return {"message": answer}