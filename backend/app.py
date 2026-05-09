from fastapi import FastAPI
from api.webhooks import router as webhook_router


def create_app() -> FastAPI:
    app = FastAPI()
    app.include_router(webhook_router)

    @app.get("/")
    def main():
        return {"response": "Hello"}

    return app


app = create_app()
