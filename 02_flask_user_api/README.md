# Flask 用户模块接口测试练习

## 项目定位

这是一个本地 Flask 用户模块接口测试练习，用来覆盖注册、登录、查询、删除、退出登录等基础接口场景。

## 能展示什么

- 使用 `requests` 发送接口请求
- 使用 `unittest` 组织测试用例
- 覆盖正向、负向、鉴权和资源异常场景
- 通过流程测试串起“注册 -> 登录 -> 查询 -> 删除”
- 记录已知缺陷和接口实现限制

## 接口范围

- `POST /register`
- `POST /login`
- `GET /user/<user_id>`
- `DELETE /user/<user_id>`
- `POST /logout`

## 主要测试点

- 正向场景：注册、登录、查询、删除、退出登录
- 参数异常：空账号、空密码、重复注册
- 鉴权异常：无效 Token、未登录访问
- 资源异常：删除不存在用户
- 流程测试：注册 -> 登录 -> 查询 -> 删除

## 运行方式

1. 启动接口服务

```bash
python app/routest.py
```

2. 运行测试

```bash
python -m unittest tests/test_user_api.py
```

或：

```bash
pytest -q
```

## 目录说明

- `app/routest.py`
  - 本地练习用 Flask 服务。
- `tests/test_user_api.py`
  - 接口测试用例，覆盖正向、负向和流程测试。

## 说明

- 服务端使用内存字典保存用户和 Token，便于本地练习。
- 因为没有数据库 reset，测试里使用随机账号避免相互干扰。
- 当前保留了若干 `expectedFailure`，用来记录实现中的已知缺陷或设计不足。

## 已知限制

- 不是生产级服务
- 未接数据库
- Token 生命周期和参数校验仍然简化
