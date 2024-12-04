from fastapi import FastAPI
from api.endpoints import users, magazines, plans, subscriptions, token
from db.base import Base
from db.sessions import engine

# Initialize the database
Base.metadata.create_all(bind=engine)

# Create FastAPI instance
app = FastAPI(title="Magazine Subscription API")

# Include routers
app.include_router(token.router, prefix="/token", tags=["token"])
app.include_router(users.router, prefix="/users", tags=["Users"])
app.include_router(magazines.router, prefix="/magazines", tags=["Magazines"])
app.include_router(plans.router, prefix="/plans", tags=["Plans"])
app.include_router(subscriptions.router, prefix="/subscriptions", tags=["Subscriptions"])
