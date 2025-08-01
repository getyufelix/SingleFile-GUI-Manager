# SingleFile GUI Manager

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

一个为SingleFile插件设计的GUI管理界面，帮助您更高效地组织和管理保存的HTML文件。

## 功能特性

- 📂 可视化文件浏览器
- 🔍 强大的搜索功能
- ✏️ 文件与目录重命名（支持中文）
- 🗑️ 文件与目录删除
- 📁 目录结构管理
- 🚀 快速预览保存的网页
- 🎨 简洁直观的用户界面

## 技术栈

- **前端**: HTML5, CSS3, JavaScript (Vanilla JS)
- **后端**: Python Flask
- **部署**: Docker支持

## 快速开始

### 使用Docker运行

```bash
docker run -d -p 5000:5000 -v /path/to/your/html/files:/html_files getyufelix/singlefile-gui:latest
```

### 本地运行

1. 确保已安装Python 3.7+
2. 安装依赖:
   ```bash
   pip install flask
   ```
3. 启动应用:
   ```bash
   python app.py
   ```
4. 访问 `http://localhost:5000`

## 配置

修改 `app.py` 中的 `BASE_DIR` 变量设置您的HTML文件存储路径:

```python
BASE_DIR = os.path.expanduser("/html_files")  # 默认路径
```

## 与SingleFile插件集成

1. 配置SingleFile插件将文件保存到本应用监听的目录
2. 使用本应用管理您保存的所有网页

## 许可证

MIT License - 详见 [LICENSE](LICENSE) 文件

## 项目状态

目前处于 **Beta** 阶段，欢迎反馈和建议！
