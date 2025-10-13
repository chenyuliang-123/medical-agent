@echo off
chcp 65001 >nul
echo ========================================
echo   慢病管理AI智能体 - 快速启动脚本
echo ========================================
echo.

echo [1/3] 检查环境...
where python >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ 未找到Python，请先安装Python 3.10+
    pause
    exit /b 1
)

where node >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ 未找到Node.js，请先安装Node.js 18+
    pause
    exit /b 1
)

echo ✅ 环境检查通过
echo.

echo [2/3] 启动后端服务...
cd backend

if not exist venv (
    echo 🔧 创建虚拟环境...
    python -m venv venv
)

call venv\Scripts\activate

if not exist chronic_disease.db (
    echo 🔧 初始化数据库...
    python init_db.py
)

echo 🚀 启动后端 (http://localhost:8000)
start cmd /k "cd /d %cd% && venv\Scripts\activate && python -m uvicorn app.main:app --reload --port 8000"

cd ..
echo.

echo [3/3] 启动前端服务...
cd frontend

if not exist node_modules (
    echo 🔧 安装依赖...
    call npm install
)

echo 🚀 启动前端 (http://localhost:5173)
start cmd /k "cd /d %cd% && npm run dev"

cd ..
echo.

echo ========================================
echo ✅ 启动完成！
echo.
echo 📝 后端服务: http://localhost:8000
echo 📝 API文档:   http://localhost:8000/docs
echo 📝 前端应用: http://localhost:5173
echo.
echo 💡 提示：
echo    - 确保已配置 backend/.env 文件
echo    - 默认用户ID为1（张三）
echo    - 查看 START.md 了解使用方法
echo ========================================
echo.

timeout /t 3 >nul
start http://localhost:5173

pause
