# UI 自动化练习

这个目录记录两条路径：

- `Selenium`
  - 早期探索版本，主要用于复盘第三方站点登录链路里的 flaky 问题。
- `Playwright`
  - 后续工程化版本，重点是状态观察、结构化结果、批量执行和报告维护。

## 推荐阅读

1. `framework/playwright_login_163music/README.md`
2. `framework/selenium_login_163music/README.md`

## 目录说明

- `framework/playwright_login_163music`
  - 当前更适合作为展示项目的版本。
- `framework/selenium_login_163music`
  - 保留探索轨迹、日志、截图和问题分析。

## 说明

- 这部分依赖第三方站点，存在验证码、`iframe`、动态弹窗和分支域名等不稳定因素。
- 因此这里更强调问题定位、观察能力和工程化收口，而不是把它包装成稳定的业务回归项目。
