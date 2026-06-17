# Flask 用户模块接口测试练习

本目录是一个本地 Flask 用户模块接口练习，用于练习 `requests`、`unittest` 和基础接口测试写法。

## 测试范围

- `POST /register`
- `POST /login`
- `GET /user/<user_id>`
- `DELETE /user/<user_id>`
- `POST /logout`

## 测试点

- 注册、登录、查询、删除、退出登录
- 空账号、空密码、重复注册
- 无效 Token、未登录访问
- 删除不存在用户
- 注册 -> 登录 -> 查询 -> 删除 的流程测试

## 运行方式

1. 启动服务

```bash
python app/routest.py
```

2. 运行测试

```bash
python -m unittest tests/test_user_api.py
```

或者：

```bash
pytest -q
```

## 说明

- 服务端使用内存字典保存用户和 Token，不依赖数据库。
- 因此测试中使用随机账号，避免用例之间互相影响。
- 文件中的 `expectedFailure` 用于记录已知缺陷或实现限制。
