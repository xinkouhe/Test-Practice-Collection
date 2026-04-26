# 禅道 API 测试用例（用户模块）

本文件为测试用例的 Markdown 展示版，完整可执行用例请查看 `zentao_api_testcases.xlsx`。

---

## TC-001 获取 Token（P1）
**前置条件**：已注册账号  
**方法**：POST /tokens  
**请求体**：
```json
{"account": "demo", "password": "quickon4You"}
```
**预期**：201，返回 token  
**实际**：通过  
**备注**：无  

---

## TC-002 获取用户信息（P2）
**前置条件**：已获得 Token  
**方法**：GET /users/{id}  
**预期**：200，返回用户字段（id/type/dept/account/realname）  
**实际**：字段完整  
**备注**：无  

---

## TC-004 创建用户（P1）
**前置条件**：已获得 Token  
**方法**：POST /users  
**预期**：200，创建成功  
**实际**：返回 400，提示“性别不能为空”  
**备注**：文档未标注 gender 为必填  

---

## TC-009 无 Token 获取用户列表（P1）
**方法**：GET /users  
**预期**：401  
**实际**：200，返回完整列表  
**备注**：疑似 APIfox 自动注入 Token  

---

## TC-010 POST 修改用户信息（P1）
**方法**：POST /users/{id}  
**预期**：4xx  
**实际**：200 + 空响应  
**备注**：不符合 REST 规范  

---

（其余用例略，详见 Excel）
