# when-did-I-xx-last-time
Cloudflare Worker

Before deploying, update database ID with your own.

## Endpoints

### 1. 获取事项列表

#### `GET /api/items`

返回所有事项及其最近一次发生时间。

**Response**

```json
[
  {
    "id": 1,
    "name": "浇花",
    "last_time": 1736592301
  },
  {
    "id": 2,
    "name": "换滤芯",
    "last_time": null
  }
]
```

---

### 2. 新增事项

#### `POST /api/items`

创建一个新的事项。

**Request Body**

```json
{
  "name": "事项名称"
}
```

**Response**

```json
{
  "id": 3
}
```

---

### 3. 刷新事项时间（记录一次发生）

#### `POST /api/items/{id}/refresh`

将指定事项的「最近发生时间」更新为当前服务器时间，并写入历史记录。

**Path Parameters**

| 参数   | 类型     | 说明    |
| ---- | ------ | ----- |
| `id` | number | 事项 ID |

**Response**

```json
{
  "ok": true
}
```

---

### 4. 获取事项历史记录

#### `GET /api/items/{id}/history`

返回指定事项的**所有历史发生时间**，按时间倒序排列（最近的在前）。

**Path Parameters**

| 参数   | 类型     | 说明    |
| ---- | ------ | ----- |
| `id` | number | 事项 ID |

**Response**

```json
[
  1736592301,
  1736500000,
  1736400000
]
```

> 返回值为 **Unix 时间戳数组（秒）**，而非对象数组。

---

## Error Handling

当前版本未区分详细错误类型，统一返回 HTTP 500 或空响应。
前端需假设网络或服务器异常可能发生，并自行处理失败提示。

（未来可扩展为结构化错误响应）

---

## Notes

* 所有时间均由服务器生成，避免客户端时间不一致问题
* API 为无状态设计
* 未包含认证与权限控制，默认单用户使用场景
* API 结构已冻结，前后端依赖此约定
