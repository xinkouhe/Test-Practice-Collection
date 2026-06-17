# test-practice-collection

测试练习仓库，按“接口测试 -> UI 自动化探索 -> 测试文档”组织。

## 仓库里有什么

- `02_flask_user_api`
  - 本地 Flask 用户模块接口测试练习。
  - 重点展示 `requests`、`unittest`、正反场景覆盖、鉴权校验和流程测试。
- `01_zentao_demo_test`
  - 基于 ZenTao Demo API 的测试用例、缺陷记录和接口文档练习。
  - 重点展示接口测试思路、测试文档和缺陷记录能力。
- `03_ui_automation/framework/playwright_login_163music`
  - 当前更适合作为展示项目的 UI 自动化版本。
  - 重点展示状态等待、结构化结果、批量执行、报告归档和问题诊断。
- `03_ui_automation/framework/selenium_login_163music`
  - Selenium 早期探索和问题定位记录。
  - 保留 flaky 问题分析、日志、截图和迁移思路，不作为稳定回归基线。

## 推荐阅读顺序

1. `02_flask_user_api/README.md`
2. `01_zentao_demo_test/README.md`
3. `03_ui_automation/framework/playwright_login_163music/README.md`
4. `03_ui_automation/framework/selenium_login_163music/README.md`

## 适合展示的能力

- 接口测试用例设计与正反场景覆盖
- `requests` + `unittest` 基础自动化
- 测试文档和缺陷记录整理
- 第三方站点 UI 自动化中的状态诊断与 flaky 分析
- 从探索脚本到工程化探针的演进思路

## 说明

- 本仓库以学习和练习为主，不把练习项目包装成完整业务系统。
- UI 自动化部分使用第三方站点，存在验证码、分支域名、`iframe` 和动态渲染等不稳定因素，因此更强调观察、诊断和结构化输出能力，而不是宣称稳定回归通过。
