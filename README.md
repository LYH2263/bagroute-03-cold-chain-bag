# BagRoute

投递装袋：按路线订户顺序装袋，重量与体积双约束，超限拒收；支持冷链订户独立成袋与冷链体积上限。

## 冷链规则

- 订户点可标记为冷链（`PATCH /api/stops/{id}`）。
- 冷链站只能进入冷链袋，非冷链站不得进入冷链袋，冷热绝不混袋。
- 每条路线在普通体积上限之外另有更严的冷链体积上限 `max_cold_volume_l`，落库保存，可在路线页维护（`PATCH /api/routes/{id}`，不得超过普通体积上限）。
- 冷链站对照冷链体积上限与共用重量上限；非冷链站仍对照普通重量/体积双上限。
- 拒收原因区分「超体积」与「冷链超体积」。

## 启动

```bash
docker compose up --build
```

| 服务 | 地址 |
| --- | --- |
| 前端 | http://localhost:4300 |
| API | http://localhost:9300 |
| API 文档 | http://localhost:9300/docs |
| Postgres | localhost:5444 |

健康检查：`GET http://localhost:9300/api/health`

## 页面

- `/routes` — 路线
- `/stops` — 订户点
- `/pack` — 装袋
- `/bags` — 袋明细
- `/rejects` — 拒收
- `/weights` — 袋重

## 使用说明

1. 查看路线与订户点顺序。
2. 在装袋页选择路线执行双约束装袋。
3. 袋明细与袋重查看结果，拒收页查看超限订户。

## 开发与测试

```bash
docker compose exec api pytest -q
```
