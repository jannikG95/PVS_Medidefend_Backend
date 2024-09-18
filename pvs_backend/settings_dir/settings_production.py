"""
Django production settings for aidjangoplatform project.
"""
# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

# ALLOWED_HOSTS = ["212.227.170.196", "medidefend.jannik-geyer.de", "10.202.20.2"]
ALLOWED_HOSTS = ['*']

CORS_ALLOWED_ORIGINS = [
    'https://medidefend.jannik-geyer.de',
]

# GPT Login Data
AZURE_OPENAI_API_KEY = "7c53126a3d674474a76176d04ad0cfe8"
AZURE_OPENAI_API_BASE = "https://ai-platform-resource-uk-south.openai.azure.com/"
AZURE_OPENAI_API_TYPE = "azure"
AZURE_OPENAI_API_VERSION = "2023-05-15"
AZURE_DEPLOYMENT_NAME_GPT_4 = "GPT-4-UK-SOUTH"
AZURE_DEPLOYMENT_NAME_GPT_4_TURBO = "GPT-4-TURBO-UK-SOUTH"
AZURE_DEPLOYMENT_NAME_GPT_3_5 = "GPT-3-5-UK-SOUTH"
AZURE_DEPLOYMENT_NAME_TEXT_EMBEDDING = "TEXT-EMBEDDING-ADA-UK-SOUTH"
