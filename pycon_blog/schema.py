import graphene

from api.schema import query, mutation


class Query(query.Query, graphene.ObjectType):
    pass


class Mutation(mutation.Mutation, graphene.ObjectType):
    pass


schema = graphene.Schema(query=Query, mutation=Mutation)
