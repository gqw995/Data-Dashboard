# GitHub Actions 自动打包使用指南

## 快速开始

### 第一步：准备 GitHub 仓库

1. **在 GitHub 上创建新仓库**（如果还没有）
   - 访问 https://github.com/new
   - 创建仓库（可以是私有或公开）

2. **将代码推送到 GitHub**
   ```bash
   # 初始化 Git（如果还没有）
   git init
   
   # 添加远程仓库
   git remote add origin https://github.com/你的用户名/你的仓库名.git
   
   # 添加所有文件
   git add .
   
   # 提交
   git commit -m "初始提交：广告数据分析系统"
   
   # 推送到 GitHub
   git push -u origin main
   ```

### 第二步：触发自动打包

#### 方法一：通过标签触发（推荐）

```bash
# 创建版本标签
git tag v1.0.0

# 推送标签到 GitHub
git push origin v1.0.0
```

#### 方法二：手动触发

1. 访问你的 GitHub 仓库
2. 点击 "Actions" 标签页
3. 选择 "Build Application" 工作流
4. 点击 "Run workflow" 按钮
5. 选择分支（通常是 `main`）
6. 点击绿色的 "Run workflow" 按钮

### 第三步：下载打包好的应用

1. **等待打包完成**
   - 通常需要 5-10 分钟
   - 可以在 Actions 页面查看实时进度

2. **下载应用**
   - 打包完成后，在 Actions 页面找到对应的运行
   - 滚动到页面底部的 "Artifacts" 部分
   - 下载：
     - `广告数据分析系统-Windows`（Windows 版本）
     - `广告数据分析系统-Mac`（Mac 版本）

## 详细说明

### 工作流触发条件

当前配置会在以下情况自动打包：

1. **推送标签**：当你推送以 `v` 开头的标签时（如 `v1.0.0`、`v1.1.0`）
2. **手动触发**：在 GitHub Actions 页面手动运行

### 修改触发条件

如果你想在每次推送到 main 分支时自动打包，编辑 `.github/workflows/build.yml`：

找到这部分：
```yaml
# 也可以设置为每次推送到main分支时触发（可选）
# push:
#   branches:
#     - main
```

取消注释（删除 `#`）：
```yaml
push:
  branches:
    - main
```

### 版本标签命名

建议使用语义化版本号：
- `v1.0.0` - 主版本.次版本.修订版本
- `v1.1.0` - 新功能
- `v2.0.0` - 重大更新

创建标签：
```bash
# 创建标签
git tag v1.0.0

# 查看所有标签
git tag

# 删除标签（如果需要）
git tag -d v1.0.0
git push origin :refs/tags/v1.0.0
```

### 查看打包日志

如果打包失败，可以查看详细日志：

1. 在 Actions 页面点击失败的运行
2. 点击对应的 job（如 "Build Windows Executable"）
3. 展开各个步骤查看详细错误信息

### 常见问题

**Q: 打包失败怎么办？**
- 检查 Actions 页面的错误日志
- 确保 `requirements.txt` 包含所有依赖
- 确保 `build_app.spec` 文件正确

**Q: 如何更新打包配置？**
- 编辑 `.github/workflows/build.yml`
- 提交并推送更改
- 下次触发时会使用新配置

**Q: 打包文件会保留多久？**
- 默认保留 30 天
- 可以在配置中修改 `retention-days` 参数

**Q: 可以同时打包多个版本吗？**
- 可以，工作流会并行运行 Windows 和 Mac 的打包任务

## 优势

使用 GitHub Actions 自动打包的优势：

✅ **无需本地环境**：不需要 Windows 或 Mac 电脑  
✅ **自动化**：推送代码即可自动打包  
✅ **多平台**：同时打包 Windows 和 Mac 版本  
✅ **版本管理**：通过标签管理不同版本  
✅ **历史记录**：所有打包历史都保存在 GitHub 上  

## 下一步

1. 将代码推送到 GitHub
2. 创建第一个版本标签
3. 下载打包好的应用
4. 分发给用户使用

享受自动打包的便利吧！🎉

