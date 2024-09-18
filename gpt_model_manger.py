from langchain.chat_models import AzureChatOpenAI
from langchain.embeddings import OpenAIEmbeddings
from langchain.llms import AzureOpenAI
from django.conf import settings


class GPTModelManager:
    _instance = None

    CHAT_GPT_3_5_TURBO_TEMP_0 = None

    CHAT_GPT_4_TEMP_0 = None
    CHAT_GPT_4_TEMP_0_1 = None
    CHAT_GPT_4_TEMP_0_2 = None
    CHAT_GPT_4_TEMP_0_3 = None

    LLM_GPT_4_TEMP_0 = None

    EMBEDDINGS_GPT = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(GPTModelManager, cls).__new__(cls, *args, **kwargs)
            cls._init_gpt_instances()  # Initialisiere GPT-Modelle
        return cls._instance

    @classmethod
    def _init_gpt_instances(cls):
        """Initialisiert die GPT-Modelle und speichert sie als Klassenvariablen."""
        cls.CHAT_GPT_3_5_TURBO_TEMP_0 = AzureChatOpenAI(deployment_name=settings.AZURE_DEPLOYMENT_NAME_GPT_3_5,
                                                        openai_api_key=settings.AZURE_OPENAI_API_KEY,
                                                        openai_api_base=settings.AZURE_OPENAI_API_BASE,
                                                        openai_api_type=settings.AZURE_OPENAI_API_TYPE,
                                                        openai_api_version=settings.AZURE_OPENAI_API_VERSION,
                                                        temperature=0)

        cls.CHAT_GPT_4_TEMP_0 = AzureChatOpenAI(deployment_name=settings.AZURE_DEPLOYMENT_NAME_GPT_4_TURBO,
                                                openai_api_key=settings.AZURE_OPENAI_API_KEY,
                                                openai_api_base=settings.AZURE_OPENAI_API_BASE,
                                                openai_api_type=settings.AZURE_OPENAI_API_TYPE,
                                                openai_api_version=settings.AZURE_OPENAI_API_VERSION,
                                                temperature=0)

        cls.CHAT_GPT_4_TEMP_0_1 = AzureChatOpenAI(deployment_name=settings.AZURE_DEPLOYMENT_NAME_GPT_4_TURBO,
                                                  openai_api_key=settings.AZURE_OPENAI_API_KEY,
                                                  openai_api_base=settings.AZURE_OPENAI_API_BASE,
                                                  openai_api_type=settings.AZURE_OPENAI_API_TYPE,
                                                  openai_api_version=settings.AZURE_OPENAI_API_VERSION,
                                                  temperature=0.1)

        cls.CHAT_GPT_4_TEMP_0_2 = AzureChatOpenAI(deployment_name=settings.AZURE_DEPLOYMENT_NAME_GPT_4_TURBO,
                                                  openai_api_key=settings.AZURE_OPENAI_API_KEY,
                                                  openai_api_base=settings.AZURE_OPENAI_API_BASE,
                                                  openai_api_type=settings.AZURE_OPENAI_API_TYPE,
                                                  openai_api_version=settings.AZURE_OPENAI_API_VERSION,
                                                  temperature=0.2)

        cls.CHAT_GPT_4_TEMP_0_3 = AzureChatOpenAI(deployment_name=settings.AZURE_DEPLOYMENT_NAME_GPT_4_TURBO,
                                                  openai_api_key=settings.AZURE_OPENAI_API_KEY,
                                                  openai_api_base=settings.AZURE_OPENAI_API_BASE,
                                                  openai_api_type=settings.AZURE_OPENAI_API_TYPE,
                                                  openai_api_version=settings.AZURE_OPENAI_API_VERSION,
                                                  temperature=0.3)

        cls.LLM_GPT_4_TEMP_0 = AzureOpenAI(deployment_name=settings.AZURE_DEPLOYMENT_NAME_GPT_4_TURBO,
                                           openai_api_key=settings.AZURE_OPENAI_API_KEY,
                                           openai_api_base=settings.AZURE_OPENAI_API_BASE,
                                           openai_api_type=settings.AZURE_OPENAI_API_TYPE,
                                           openai_api_version=settings.AZURE_OPENAI_API_VERSION,
                                           temperature=0
                                           )

        cls.EMBEDDINGS_GPT = OpenAIEmbeddings(deployment=settings.AZURE_DEPLOYMENT_NAME_TEXT_EMBEDDING,
                                              openai_api_key=settings.AZURE_OPENAI_API_KEY,
                                              openai_api_base=settings.AZURE_OPENAI_API_BASE,
                                              openai_api_type=settings.AZURE_OPENAI_API_TYPE,
                                              openai_api_version=settings.AZURE_OPENAI_API_VERSION
                                              )
