# GitHub Actions 自动打包说明

本目录包含 GitHub Actions 工作流配置，用于自动打包 Windows 和 Mac 应用程序。

## 使用方法

### 方法一：通过标签触发（推荐）

1. **提交代码到 GitHub**
   ```bash
   git add .
   git commit -m "更新功能"
   git push
   ```

2. **创建版本标签并推送**
   ```bash
   git tag v1.0.0
   git push origin v1.0.0
   ```

3. **查看打包结果**
   - 访问 GitHub 仓库的 "Actions" 标签页
   - 查看工作流运行状态
   - 完成后在 "Artifacts" 部分下载打包好的应用

### 方法二：手动触发

1. **访问 GitHub 仓库**
   - 进入 "Actions" 标签页
   - 选择 "Build Application" 工作流
   - 点击 "Run workflow" 按钮
   - 选择分支并点击 "Run workflow"

2. **等待打包完成**
   - 通常需要 5-10 分钟
   - 可以在 Actions 页面查看实时日志

3. **下载打包结果**
   - 打包完成后，在 "Artifacts" 部分下载
   - Windows 版本：`广告数据分析系统-Windows`
   - Mac 版本：`广告数据分析系统-Mac`

## 工作流说明

### 触发条件

- **标签推送**：当推送以 `v` 开头的标签时（如 `v1.0.0`）
- **手动触发**：在 GitHub Actions 页面手动运行
- **可选**：可以修改配置，使其在推送到 main 分支时自动触发

### 打包环境

- **Windows**: `windows-latest` (Windows Server 2022)
- **Mac**: `macos-latest` (macOS 13)
- **Python**: 3.11

### 输出文件

- Windows: `广告数据分析系统.exe`
- Mac: `广告数据分析系统`

## 注意事项

1. **首次使用需要设置仓库**
   - 确保代码已推送到 GitHub 仓库
   - 确保仓库是公开的或你有 Actions 权限

2. **文件保留时间**
   - 打包文件会在 GitHub 上保留 30 天
   - 建议及时下载到本地保存

3. **标签命名规范**
   - 使用语义化版本号：`v1.0.0`、`v1.1.0`、`v2.0.0` 等
   - 必须以 `v` 开头

4. **修改触发条件**
   - 如果需要修改触发条件，编辑 `.github/workflows/build.yml`
   - 取消注释 `push: branches: - main` 部分即可在每次推送时自动打包

## 故障排除

### 打包失败

1. **检查日志**
   - 在 Actions 页面查看详细错误信息
   - 常见问题：依赖安装失败、文件路径错误

2. **检查配置文件**
   - 确保 `build_app.spec` 文件正确
   - 确保 `requirements.txt` 包含所有依赖

3. **重新运行**
   - 点击失败的运行，选择 "Re-run jobs"

### 下载文件失败

1. **检查文件大小**
   - 打包文件可能较大（100-200MB）
   - 确保网络连接稳定

2. **使用浏览器下载**
   - 某些情况下，右键点击下载链接可能失败
   - 尝试直接点击下载

## 本地测试

在推送到 GitHub 之前，建议先在本地测试打包：

```bash
# Windows
build_windows.bat

# Mac
./build_mac.sh
```

确保本地打包成功后再推送到 GitHub。

