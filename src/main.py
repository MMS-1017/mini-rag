from fastapi import FastAPI
from routes import base, data, nlp
from motor.motor_asyncio import AsyncIOMotorClient
from helpers.config import get_settings
from stores.llm.LLMProviderFactory import LLMProviderFactory
from stores.vectordb.VectorDBProviderFactory import VectorDBProviderFactory

app = FastAPI()

async def startup_span():
    settings = get_settings()
    app.mongo_conn = AsyncIOMotorClient(settings.MONGODB_URL) # to attach data
    app.db_client = app.mongo_conn[settings.MONGODB_DB_NAME]

    llm_provider_factory = LLMProviderFactory(settings)
    vector_db_provider_factory = VectorDBProviderFactory(settings)

    # Generation client
    app.generation_client = llm_provider_factory.create_provider(provider_name=settings.GENERATION_BACKEND)
    app.generation_client.set_generation_model(model_name=settings.GENERATION_MODEL)

    # Embedding client
    app.embedding_client = llm_provider_factory.create_provider(provider_name=settings.EMBEDDING_BACKEND)
    app.embedding_client.set_embedding_model(model_name=settings.EMBEDDING_MODEL,
                                             embedding_size=settings.EMBEDDING_SIZE)

    # vectorDB client
    app.vector_db_client = vector_db_provider_factory.create_provider(
        provider_name=settings.VECTORDB_BACKEND
    )

    app.vector_db_client.connect()

async def shutdown_span():
    app.mongo_conn.close()
    app.vector_db_client.disconnect()

app.router.lifespan.on_startup.append(startup_span)
app.router.lifespan.on_shutdown.append(shutdown_span)

app.include_router(base.base_router)
app.include_router(data.data_router)
app.include_router(nlp.nlp_router)