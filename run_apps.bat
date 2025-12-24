@echo off
echo 🚀 파이썬 레벨테스트 시스템을 시작합니다 (uv 사용)...

# 의존성 설치
uv sync

# 학생용 테스트 페이지 실행 (8501 포트)
start /b uv run streamlit run level_test.py --server.port 8501
echo 📝 학생용 페이지 실행 중: http://localhost:8501

# 관리자 페이지 실행 (8502 포트)
start /b uv run streamlit run admin.py --server.port 8502
echo 🔐 관리자 페이지 실행 중: http://localhost:8502

echo ✅ 모든 시스템이 실행되었습니다. 종료하려면 이 창을 닫으세요.
pause

