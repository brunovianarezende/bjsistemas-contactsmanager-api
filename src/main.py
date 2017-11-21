from pymongo import MongoClient

from servicefusion.server import app
from servicefusion.model import MongoBackend

if __name__ == '__main__':
    mongo = MongoClient('mongodb://127.0.0.1:27017')
    app.config.update(dict(
        BACKEND=MongoBackend(mongo.servicefusion)
    ))
    app.run()
