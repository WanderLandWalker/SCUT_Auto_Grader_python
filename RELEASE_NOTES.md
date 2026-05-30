# Release Notes

## v1.0 (2026-05-30)

### 初始版本

首个发布版本，包含以下核心功能：

#### 扫描功能 (scan_reviews.py)
- 自动登录华南理工大学作业互评系统
- 遍历所有题目和学生，提取未评作业数据
- 智能检测已评分作业，自动跳过
- 处理 ASP.NET Postback 异步刷新机制
- 导出数据为标准 JSON 格式 (reviews.json)

#### 提交功能 (submit_reviews.py)
- 读取评分结果 JSON 文件
- 自动匹配题目和学生
- 填入分数和评语并提交
- 提交结果统计（成功/跳过/失败）

#### 技术特性
- 基于 Selenium 自动化框架
- 支持 Microsoft Edge 浏览器
- 自动管理浏览器驱动 (webdriver-manager)
- 智能等待页面加载完成
- 本地数据存储，保护隐私

### 使用说明

1. 安装依赖：`pip install selenium webdriver-manager`
2. 扫描未评作业：`python scan_reviews.py`
3. 准备评分数据（手动编辑或使用 AI）
4. 提交评分：`python submit_reviews.py`

### 相关项目

- [SCUT_Auto_Grader](https://github.com/WanderLandWalker/SCUT_Auto_Grader) - 油猴脚本版，支持更多功能