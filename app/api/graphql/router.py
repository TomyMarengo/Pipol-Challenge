"""GraphQL router configuration."""

import strawberry
from strawberry.fastapi import GraphQLRouter
from app.api.graphql.resolvers import Query


# Create the GraphQL schema
schema = strawberry.Schema(
    query=Query,
    description="GraphQL API for product analytics data"
)

# Create the GraphQL router
graphql_router = GraphQLRouter(
    schema,
    path="/graphql",
)

