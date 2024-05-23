import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv('JWT_SECRET')
    ALGORITHM = os.getenv('JWT_ALGORITHM')
    EXP_DELTA_SECONDS = int(os.getenv('JWT_EXP_DELTA_SECONDS'))
