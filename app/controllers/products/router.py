"""GraphQL router configuration."""

import strawberry
from fastapi import Depends
from strawberry.fastapi import GraphQLRouter

from app.controllers.products.resolvers import Query
from app.core.dependencies import get_current_user


# Context class to pass authentication info to resolvers
async def get_context(user: dict = Depends(get_current_user)):
    """Get GraphQL context with authenticated user."""
    return {"user": user}


# Create the GraphQL schema
schema = strawberry.Schema(query=Query)

# Create the GraphQL router with authentication
graphql_router = GraphQLRouter(
    schema,
    path="/graphql",
    context_getter=get_context,
)
