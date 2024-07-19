from aiohttp import web

JSON = """          
          # -- https://t.me/AshutoshGoswami24 -- #
# -- https://github.com/AshutoshGoswami24/Auto-Rename-Bot -- #



▄▀█ █▀ █░█ █░█ ▀█▀ █▀█ █▀ █░█ █▀▀ █▀█ █▀ █░█░█ ▄▀█ █▀▄▀█ █ ▀█ █░█
█▀█ ▄█ █▀█ █▄█ ░█░ █▄█ ▄█ █▀█ █▄█ █▄█ ▄█ ▀▄▀▄▀ █▀█ █░▀░█ █ █▄ ▀▀█

          # -- https://t.me/AshutoshGoswami24 -- #
# -- https://github.com/AshutoshGoswami24/Auto-Rename-Bot -- #
"""

routes = web.RouteTableDef()

@routes.get("/", allow_head=True)
async def root_route_handler(request):
    return web.json_response(JSON)


async def web_server():
    web_app = web.Application(client_max_size=30000000)
    web_app.add_routes(routes)
    return web_app



          # -- https://t.me/AshutoshGoswami24 -- #
# -- https://github.com/AshutoshGoswami24/Auto-Rename-Bot -- #
