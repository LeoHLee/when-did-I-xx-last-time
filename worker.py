import json
import time
from workers import WorkerEntrypoint, Response


def json_response(data, status=200):
    return Response(
        json.dumps(data),
        status=status,
        headers={"Content-Type": "application/json"},
    )


class Default(WorkerEntrypoint):

    async def on_fetch(self, request):
        url = request.url
        method = request.method

        # -------- API 路由 --------

        if url.endswith("/api/items") and method == "GET":
            return await self.list_items()

        if url.endswith("/api/items") and method == "POST":
            return await self.add_item(request)

        if "/api/items/" in url and url.endswith("/refresh") and method == "POST":
            item_id = url.split("/")[-2]
            return await self.refresh_item(request, item_id)

        if "/api/items/" in url and url.endswith("/history") and method == "GET":
            item_id = url.split("/")[-2]
            return await self.get_history(item_id)

        # -------- 非 API：交给静态资源 --------
        return await self.env.ASSETS.fetch(request)

    # -----------------------------
    # API 实现
    # -----------------------------

    async def list_items(self):
        result = await self.env.DB.prepare(
            "SELECT id, name, last_time FROM items ORDER BY id"
        ).all()

        items = []
        for row in result.results:
            items.append({
                "id": row.id,
                "name": row.name,
                "last_time": row.last_time,
            })

        return json_response(items)

    async def add_item(self, request):
        try:
            data = await request.json()
        except Exception:
            return json_response({"error": "Invalid JSON"}, status=400)

        name = data.get("name")
        if not name:
            return json_response({"error": "Missing name"}, status=400)

        # 允许用户指定时间，未提供则使用当前时间
        timestamp = int(time.time())
        ts = data.get("time")
        if ts is not None:
            timestamp = int(ts)

        try:
            await self.env.DB.prepare(
                "INSERT INTO items (name, last_time) VALUES (?, ?)"
            ).bind(name, timestamp).run()
        except Exception:
            return json_response({"error": "Item already exists"}, status=409)

        row = await self.env.DB.prepare(
            "SELECT id FROM items WHERE name = ?"
        ).bind(name).first()

        item_id = row.id

        await self.env.DB.prepare(
            "INSERT INTO item_history (item_id, time) VALUES (?, ?)"
        ).bind(item_id, timestamp).run()

        return json_response({"id": item_id, "name": name, "last_time": timestamp}, status=201)

    async def refresh_item(self, request, item_id):
        # 尝试从请求体中读取可选的时间戳，未提供则使用当前时间
        timestamp = int(time.time())
        try:
            data = await request.json()
            ts = data.get("time")
            if ts is not None:
                timestamp = int(ts)
        except Exception:
            pass

        await self.env.DB.prepare(
            "UPDATE items SET last_time = ? WHERE id = ?"
        ).bind(timestamp, item_id).run()

        await self.env.DB.prepare(
            "INSERT INTO item_history (item_id, time) VALUES (?, ?)"
        ).bind(item_id, timestamp).run()

        return json_response({"id": int(item_id), "last_time": timestamp})

    async def get_history(self, item_id):
        result = await self.env.DB.prepare(
            "SELECT time FROM item_history WHERE item_id = ? ORDER BY time DESC"
        ).bind(item_id).all()

        history = []
        for row in result.results:
            history.append(row.time)

        return json_response(history)
