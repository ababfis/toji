import os
import dotenv

dotenv_path = os.path.join(os.path.dirname(__file__), '..', '.env')
if os.path.exists(dotenv_path):
    dotenv.load_dotenv(dotenv_path)

BOT_TOKEN = os.getenv('BOT_TOKEN')
