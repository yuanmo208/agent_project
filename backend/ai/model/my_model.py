from langchain_openai import ChatOpenAI
from langchain_ollama import ChatOllama
from dotenv import load_dotenv
import os
load_dotenv()


class ModelManage:
    # 定义私有属性
    _model = None
    # 定义本地模型私有属性
    _local_model = None
    # 定义语音模型
    _vosk_model = None

    # 定义静态函数,在线模型

    @staticmethod
    def get_model():
        # 判断_model 是否未空
        if ModelManage._model is None:
            # 创建模型
            ModelManage._model = ChatOpenAI(
                model=os.getenv("MODEL_ONLINE_NAME"),
                api_key=os.getenv("DASHSCOPE_API_KEY"),
                base_url=os.getenv("OPENAI_API_BASE"),
                streaming=True,  # 开启流式输出
                extra_body={
                    "enable_thinking": False  # 是否开启思考过程
                }
            )
        return ModelManage._model

    # 本地模型创建

    @staticmethod
    def get_local_model():
        # 判断_model 是否未空
        if ModelManage._local_model is None:
            # 创建模型
            ModelManage._local_model = ChatOllama(
                model=os.getenv("MODEL_LOCAL_NAME"),
                base_url=os.getenv("LOCAL_URL"),
                streaming=False,  # 开启流式输出
            )
        return ModelManage._local_model




