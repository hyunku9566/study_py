# 🐍 파이썬 레벨 테스트 시스템

이 프로젝트는 학생들의 파이썬 실력을 평가하기 위한 Streamlit 기반의 레벨 테스트 시스템입니다.

## ✨ 주요 기능

- **학생용 테스트 페이지**: 19개 단원, 단원당 100문제(랜덤 10문제 출제) 제공.
- **실시간 채점**: 작성한 코드를 즉시 실행하고 테스트 케이스별 통과 여부 확인.
- **고급 에디터**: 자동완성 및 문법 강조(Syntax Highlighting) 기능이 포함된 코드 에디터.
- **부정행위 방지**: 화면 이탈(탭 전환 등) 감지 및 자동 저장 기능.
- **관리자 대시보드**: 학생별 정답률, 제출 횟수, 화면 이탈 기록 등 상세 통계 제공.

## 🛠 설치 및 실행 방법 (`uv` 사용)

이 프로젝트는 가장 빠른 파이썬 패키지 관리자인 `uv`를 사용합니다.

### 1. `uv` 설치 (미설치된 경우)

- **macOS/Linux**:
  ```bash
  curl -LsSf https://astral.sh/uv/install.sh | sh
  ```
- **Windows**:
  ```powershell
  powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
  ```

### 2. 프로젝트 실행

스크립트 하나로 모든 의존성 설치와 앱 실행이 가능합니다.

- **macOS/Linux**:
  ```bash
  chmod +x run_apps.sh
  ./run_apps.sh
  ```
- **Windows**:
  `run_apps.bat` 파일을 더블 클릭하거나 터미널에서 실행하세요.

### 3. 접속 주소

- **학생용 페이지**: [http://localhost:8501](http://localhost:8501)
- **관리자 페이지**: [http://localhost:8502](http://localhost:8502) (비밀번호: `admin`)

## 📂 프로젝트 구조

- `level_test.py`: 메인 학생용 테스트 애플리케이션.
- `admin.py`: 관리자용 결과 분석 대시보드.
- `problems/`: 각 단원별 문제 JSON 파일 데이터.
- `results/`: 학생들의 테스트 결과가 저장되는 폴더.
- `generate_problems_gemini.py`: Gemini API를 사용한 문제 자동 생성 도구.

## 📝 문제 생성 가이드 (선택 사항)

Gemini API를 사용하여 더 많은 문제를 생성하고 싶다면:

1. 환경변수에 API 키 등록: `export gemini="your_api_key"`
2. 스크립트 실행: `uv run generate_problems_gemini.py`

---
문의사항이 있으시면 관리자에게 연락 바랍니다.

# study_py
