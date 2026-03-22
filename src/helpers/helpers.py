import hashlib
from dotenv import load_dotenv
import os

load_dotenv(override=True)

def return_releaseId() -> str:
    data = os.getenv('VERSION', 'version[1.0]')
    releaseId = data.encode('utf-8')

    hash_object = hashlib.sha256(releaseId)

    hex_dig = hash_object.hexdigest()

    return hex_dig