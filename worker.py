import json
import time
from workers import WorkerEntrypoint, Response

class Default(WorkerEntrypoint):

    async def on_fetch(self, request):
        url = request.url
        method = request.method

        if url.endswith("/api/items") and method == "GET":
            return await self.list_items()

        if url.endswith("/api/items") and method == "POST":
            return await self.add_item(request)

        if "/refresh" in url and method == "POST":
            item_id = url.split("/")[-2]
            return await self.refresh_item(item_id)

        if "/history" in url and method == "GET":
            item_id = url.split("/")[-2]
            return await self.get_history(item_id)

        # Frontend
        return await self.env.ASSETS.fetch(request)

    async def list_items(self):
        result = await self.env.DB.prepare(
            "SELECT id, name, last_time FROM items ORDER BY id"
        ).all()
        return Response(json.dumps(result.results))

    async def add_item(self, request):
        data = await request.json()
        name = data.get("name")

        if not name:
            return Response("Missing name", status=400)

        now = int(time.time())

        await self.env.DB.prepare(
            "INSERT INTO items (name, last_time) VALUES (?, ?)"
        ).bind(name, now).run()

        row = await self.env.DB.prepare(
            "SELECT id FROM items WHERE name = ?"
        ).bind(name).first()

        item_id = row.id

        await self.env.DB.prepare(
            "INSERT INTO item_history (item_id, time) VALUES (?, ?)"
        ).bind(item_id, now).run()

        return Response("OK")


    async def refresh_item(self, item_id):
        now = int(time.time())

        await self.env.DB.prepare(
            "UPDATE items SET last_time = ? WHERE id = ?"
        ).bind(now, item_id).run()

        await self.env.DB.prepare(
            "INSERT INTO item_history (item_id, time) VALUES (?, ?)"
        ).bind(item_id, now).run()

        return Response("OK")

    async def get_history(self, item_id):
        result = await self.env.DB.prepare(
            "SELECT time FROM item_history WHERE item_id = ? ORDER BY time DESC"
        ).bind(item_id).all()

        return Response(json.dumps(result.results))
