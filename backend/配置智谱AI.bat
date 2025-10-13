@echo off
chcp 65001 >nul
echo ========================================
echo   智谱AI配置助手
echo ========================================
echo.

echo 📝 第一步：注册智谱AI账号
echo.
echo 1. 访问：https://open.bigmodel.cn/
echo 2. 注册并登录
echo 3. 进入"控制台" → "API密钥"
echo 4. 创建新的API Key
echo 5. 复制API Key
echo.
pause

echo.
echo 📝 第二步：配置.env文件
echo.

if not exist .env (
    echo 正在创建.env文件...
    copy .env.example .env >nul
    echo ✅ .env文件已创建
) else (
    echo ℹ️  .env文件已存在
)

echo.
echo 请在.env文件中填入以下内容：
echo.
echo LLM_PROVIDER=zhipu
echo ZHIPU_API_KEY=你的API_Key
echo ZHIPU_MODEL=glm-4
echo.

echo 正在打开.env文件...
timeout /t 2 >nul
notepad .env

echo.
echo ========================================
echo ✅ 配置完成！
echo.
echo 📝 下一步：
echo    1. 确保已填入ZHIPU_API_KEY
echo    2. 运行：python init_db.py
echo    3. 运行：python -m uvicorn app.main:app --reload
echo.
echo 💡 测试：访问 http://localhost:8000/docs
echo ========================================
echo.

pause
