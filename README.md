# SCUT_Auto_Grader_python

**华南理工大学作业互评自动脚本 - Python版**

[![Release](https://img.shields.io/badge/Release-v1.0-blue?style=flat)](https://github.com/WanderLandWalker/SCUT_Auto_Grader_python/releases/latest)[![License](https://img.shields.io/badge/License-MIT-green?style=flat)](https://github.com/WanderLandWalker/SCUT_Auto_Grader_python/blob/main/LICENSE)

---

## 简介

这是一个基于 Selenium 的 Python 自动化脚本，用于华南理工大学作业互评系统。与[油猴脚本版](https://github.com/WanderLandWalker/SCUT_Auto_Grader)不同，本版本需要下载到本地运行，适合需要更灵活控制或无法使用油猴脚本的场景。

## 功能

### 核心功能

| 功能 | 说明 |
|------|------|
| **扫描未评作业** | `scan_reviews.py` - 自动遍历所有题目和学生，提取未评作业数据并导出为 JSON |
| **提交评分结果** | `submit_reviews.py` - 根据评分 JSON 文件自动填入分数和评语并提交 |

### 技术特性

- **自动化浏览器操作**：使用 Selenium 控制 Edge 浏览器，模拟真实用户操作
- **智能等待机制**：处理 ASP.NET Postback 异步刷新，确保页面加载完成
- **已评检测**：自动识别已评分作业，跳过已处理的学生
- **批量处理**：支持批量扫描和批量提交，提高效率
- **JSON 数据交换**：扫描结果保存为标准 JSON 格式，方便与外部 AI 或人工评分工具对接

## 安装

### 环境要求

- Python 3.7+
- Microsoft Edge 浏览器
- Edge WebDriver（或使用 webdriver-manager 自动管理）

### 安装步骤

1. 克隆或下载本仓库：
   ```bash
   git clone https://github.com/WanderLandWalker/SCUT_Auto_Grader_python.git
   cd SCUT_Auto_Grader_python
   ```

2. 安装依赖：
   ```bash
   pip install selenium webdriver-manager
   ```

   或者使用 requirements.txt（如果有）：
   ```bash
   pip install -r requirements.txt
   ```

## 使用

### 第一步：扫描未评作业

```bash
python scan_reviews.py
```

1. 运行脚本后，按提示输入学号和密码
2. 脚本自动启动 Edge 浏览器并登录互评系统
3. 遍历所有题目和学生，提取未评作业数据
4. 扫描完成后，数据保存到 `reviews.json` 文件

### 第二步：准备评分数据

扫描完成后，你可以：

**方式一：手动评分**
- 直接编辑 `reviews.json` 文件，为每个作业添加 `score`（分数）和 `comment`（评语）字段

**方式二：使用 AI 评分**
- 将 `reviews.json` 发送给 AI（如 DeepSeek、ChatGPT 等）
- AI 会根据参考答案和学生回答生成评分和评语
- 将 AI 返回的结果保存为新的 JSON 文件

**方式三：使用油猴脚本版的导出/导入功能**
- 本项目是油猴脚本版的配套工具，扫描结果可导入到油猴脚本版进行提交

### 第三步：提交评分

```bash
python submit_reviews.py
```

1. 运行脚本，按提示输入评分结果文件路径（默认为 `reviews.json`）
2. 输入学号和密码
3. 脶本自动遍历评分数据，为每个作业填入分数和评语并提交
4. 完成后显示提交结果统计

## JSON 数据格式

扫描生成的 `reviews.json` 格式如下：

```json
[
  {
    "title": "作业题目名称",
    "student": "学生姓名",
    "reference_answer": "参考答案内容",
    "student_content": "学生回答内容",
    "page_html": "<html>...</html>"
  }
]
```

提交评分时，需要添加 `score` 和 `comment` 字段：

```json
[
  {
    "title": "作业题目名称",
    "student": "学生姓名",
    "reference_answer": "参考答案内容",
    "student_content": "学生回答内容",
    "score": "95",
    "comment": "回答基本正确，但细节可以更完善。"
  }
]
```

## 注意事项

1. **浏览器驱动**：脚本会尝试使用 webdriver-manager 自动下载 Edge 驱动，如果失败则使用系统已安装的驱动
2. **网络环境**：需要能够访问华南理工大学教务系统（`1024.se.scut.edu.cn`）
3. **登录状态**：如果浏览器已登录教务系统，脚本会直接进入互评页面
4. **提交间隔**：建议在提交评分时适当等待，避免频繁请求被系统限制
5. **数据安全**：评分数据仅保存在本地 `reviews.json` 文件中，不会上传到任何服务器

## 与油猴脚本版的区别

| 特性 | Python 版 | 油猴脚本版 |
|------|-----------|------------|
| 运行方式 | 本地 Python 脚本 | 浏览器油猴脚本 |
| 依赖 | Python + Selenium | Tampermonkey/Violentmonkey |
| AI 集成 | 需要外部 AI 处理 | 内置 10+ AI 供应商 |
| 评分模式 | 扫描 + 提交分离 | 4 种模式一体化 |
| 适用场景 | 批量处理、二次开发 | 一键操作、简单易用 |

## 相关项目

- [SCUT_Auto_Grader](https://github.com/WanderLandWalker/SCUT_Auto_Grader) - 油猴脚本版，支持 4 种模式、10+ AI 供应商，全自动互评

## 许可证

[MIT License](LICENSE)

## 如果觉得有用

如果这个脚本帮到了你，欢迎给个 Star 支持一下！

[![GitHub Stars](https://img.shields.io/github/stars/WanderLandWalker/SCUT_Auto_Grader_python?style=social)](https://github.com/WanderLandWalker/SCUT_Auto_Grader_python)