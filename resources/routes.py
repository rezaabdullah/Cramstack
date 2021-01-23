from .pgcb import Pgcb, PgcbHome, PgcbFilter

def initialize_routes(api):
    api.add_resource(PgcbHome, "/")
    api.add_resource(Pgcb, "/show_all")
    api.add_resource(PgcbFilter, "/filter")