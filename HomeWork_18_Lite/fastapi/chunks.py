from langchain_community.embeddings import OpenAIEmbeddings
from langchain.text_splitter import CharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain.docstore.document import Document
from dotenv import load_dotenv
import openai
import os
from openai import AsyncOpenAI, OpenAI
import time


# получим переменные окружения из .env
load_dotenv()

# API-key
openai.api_key = os.environ.get("OPENAI_API_KEY")

# задаем system
default_system = "Ты-консультант в компании Simble, ответь на вопрос клиента на основе документа с информацией. Не придумывай ничего от себя, отвечай максимально по документу. Не упоминай Документ с информацией для ответа клиенту. Клиент ничего не должен знать про Документ с информацией для ответа клиенту"


class Chunk():

    def __init__(self, path_to_base:str, sep:str=" ", ch_size:int=1024):
        
        # загружаем базу
        with open(path_to_base, 'r', encoding='utf-8') as file:
            document = file.read()

        # создаем список чанков
        source_chunks = []
        splitter = CharacterTextSplitter(separator=sep, chunk_size=ch_size)
        for chunk in splitter.split_text(document):
            source_chunks.append(Document(page_content=chunk, metadata={}))

        # создаем индексную базу
        embeddings = OpenAIEmbeddings(
            model="text-embedding-3-small",
            api_key=openai.api_key,
            base_url="https://api.proxyapi.ru/openai/v1",
        )
        self.db = FAISS.from_documents(source_chunks, embeddings)
 

    async def get_answer(self, system:str = default_system, query:str = None):
        start_time = time.time()
        '''Функция получения ответа от chatgpt'''
        # релевантные отрезки из базы
        docs = self.db.similarity_search(query, k=4)
        message_content = '\n'.join([f'{doc.page_content}' for doc in docs])
        messages = [
            {"role": "system", "content": system},
            {"role": "user", "content": f"Ответь на вопрос клиента. Не упоминай документ с информацией для ответа клиенту в ответе. Документ с информацией для ответа клиенту: {message_content}\n\nВопрос клиента: \n{query}"}
        ]

        client = AsyncOpenAI(
            api_key=openai.api_key,
            base_url="https://api.proxyapi.ru/openai/v1",
            )
        # получение ответа от chatgpt
        completion = await client.chat.completions.create(model="gpt-4o-mini",
                                                  messages=messages,
                                                  temperature=0,
                                                  )
        print(f"Время выполнения: {time.time() - start_time} секунд")
        
        return completion.choices[0].message.content
            