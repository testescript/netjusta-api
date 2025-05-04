from endpoints import api_router

app = FastAPI()
app.include_router(api_router.router)
