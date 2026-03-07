# 维护指南

## 发布流程

1. 确保 `main` 分支在 CI 中为绿色。
2. 在 `CHANGELOG.md` 的 `Unreleased` 下更新变更。
3. 创建版本标签：
```bash
git tag v0.1.1
git push origin v0.1.1
```
4. `release.yml` 会构建产物并创建 GitHub Release。
5. 若已配置 `PYPI_API_TOKEN`，还会同时发布到 PyPI。

## 依赖管理

- Dependabot 每周会为 pip 和 GitHub Actions 发起更新。
- 通过以下命令审查依赖 PR：
```bash
make check
```
- 安全扫描通过 `security.yml` 和 `pip-audit` 运行。

## 分支保护（推荐）

在 `main` 上启用：

- 必须通过 PR 审核（至少 1 人）
- 必须通过状态检查：CI + Security
- 必须解决所有会话评论
- 限制直接 push

## 负责人

- 在 `.github/CODEOWNERS` 中更新真实团队/用户。
- 确保至少两位维护者具备合并与发布权限。
