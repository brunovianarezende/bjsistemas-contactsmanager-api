from servicefusion.server import app
from servicefusion.model import InMemoryBackend

if __name__ == '__main__':
    app.config.update(dict(
        BACKEND=InMemoryBackend()
    ))
    app.run()
