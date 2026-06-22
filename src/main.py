from api import create_app
from dependencies import APIDependencies

apiDependencies = APIDependencies()

app = create_app(apiDependencies)
