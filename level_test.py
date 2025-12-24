import streamlit as st
import streamlit.components.v1 as components
from streamlit_ace import st_ace
import sys
import io
import contextlib
import json
import os
import time
import random
from datetime import datetime

# ==========================================
# 1. 설정 및 초기화
# ==========================================

st.set_page_config(page_title="파이썬 레벨테스트", layout="wide")

# 세션 상태 초기화
if 'user_name' not in st.session_state:
    st.session_state['user_name'] = ""
if 'start_time' not in st.session_state:
    st.session_state['start_time'] = None
if 'end_time' not in st.session_state:
    st.session_state['end_time'] = None
if 'solve_status' not in st.session_state:
    st.session_state['solve_status'] = {}  # { "chapter_problemId": {"status": "PASS"/"FAIL", "submissions": 3, "first_pass": "..."} }
if 'test_finished' not in st.session_state:
    st.session_state['test_finished'] = False
if 'selected_problems' not in st.session_state:
    st.session_state['selected_problems'] = {}  # { chapter_idx: [problem_ids...] }

# 결과 저장 폴더
RESULTS_DIR = "results"
PROBLEMS_DIR = "problems"

# 챕터 정보 (각 단원당 100문제)
CHAPTERS_INFO = [
    ("출력", 100),
    ("변수와 입력", 100),
    ("연산자", 100),
    ("문자열1", 100),
    ("리스트 1", 100),
    ("선택제어문", 100),
    ("디버깅", 100),
    ("반복제어문 1", 100),
    ("반복제어문 2", 100),
    ("반복제어문 3", 100),
    ("문자열 2", 100),
    ("리스트 2", 100),
    ("리스트 3", 100),
    ("기타 자료형", 100),
    ("함수 1", 100),
    ("함수 2", 100),
    ("함수 3 - 재귀함수", 100),
    ("클래스", 100),
    ("파일입출력", 100)
]

# 각 단원당 출제할 문제 수
PROBLEMS_PER_CHAPTER = 10

# ==========================================
# 2. 자바스크립트 (부정행위 감지)
# ==========================================
js_code = """
<script>
    document.addEventListener('visibilitychange', function() {
        if (document.hidden) {
            console.log("Tab hidden");
        } else {
            let now = new Date().toLocaleString();
            if (document.body.innerText.includes("테스트 결과 리포트")) {
                return;
            }
            alert("⚠️ 경고: 화면 이탈이 감지되었습니다! (" + now + ")");
        }
    });
</script>
"""
components.html(js_code, height=0, width=0)


# ==========================================
# 3. 유틸리티 함수
# ==========================================

def save_results(final=False):
    """현재까지의 풀이 기록을 JSON 파일로 저장"""
    if not st.session_state['user_name']:
        return None

    now_str = datetime.now().strftime("%Y-%m-%d")
    filename = f"{now_str}_{st.session_state['user_name']}_result.json"
    file_path = os.path.join(RESULTS_DIR, filename)

    data = {
        "user_name": st.session_state['user_name'],
        "date": now_str,
        "start_time": st.session_state['start_time'],
        "end_time": st.session_state['end_time'] if final else None,
        "last_updated": datetime.now().strftime("%H:%M:%S"),
        "is_finished": st.session_state['test_finished'],
        "solve_status": st.session_state['solve_status'],
        "selected_problems": st.session_state.get('selected_problems', {}),
        "exit_logs": st.session_state.get('exit_logs', [])
    }

    try:
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return filename
    except Exception as e:
        st.error(f"저장 중 오류 발생: {e}")
        return None

def load_problem_data(chapter_name, chapter_index):
    expected_filename = f"{chapter_index+1:02d}_{chapter_name}.json"
    file_path = os.path.join(PROBLEMS_DIR, expected_filename)
    if os.path.exists(file_path):
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return None
    return None

def get_selected_problems_for_chapter(chapter_index, total_problems):
    """각 단원에서 랜덤으로 선택된 문제 목록을 반환"""
    if chapter_index not in st.session_state['selected_problems']:
        # 랜덤으로 10문제 선택
        all_problem_ids = list(range(1, total_problems + 1))
        selected = sorted(random.sample(all_problem_ids, min(PROBLEMS_PER_CHAPTER, len(all_problem_ids))))
        st.session_state['selected_problems'][chapter_index] = selected
    return st.session_state['selected_problems'][chapter_index]

class MockInput:
    def __init__(self, inputs_str):
        self.inputs = inputs_str.strip().split('\n') if inputs_str else []
        self.current = 0
    
    def readline(self):
        if self.current < len(self.inputs):
            ret = self.inputs[self.current]
            self.current += 1
            return ret
        return "" 

    def __call__(self, prompt=""):
        return self.readline()

@contextlib.contextmanager
def stdout_capture():
    capture = io.StringIO()
    old_stdout = sys.stdout
    sys.stdout = capture
    try:
        yield capture
    finally:
        sys.stdout = old_stdout

def execute_user_code(code_input, user_inputs=""):
    mock_input_obj = MockInput(user_inputs)
    exec_globals = {'input': mock_input_obj, '__builtins__': __builtins__.copy()}
    exec_globals['__builtins__']['input'] = mock_input_obj

    try:
        with stdout_capture() as captured_output:
            exec(code_input, exec_globals)
        return captured_output.getvalue(), None
    except Exception as e:
        return None, str(e)

def normalize_output(output):
    """출력을 정규화하여 비교 (공백 제거, 줄바꿈 정리)"""
    if output is None:
        return ""
    return output.strip().replace('\r\n', '\n').replace('\r', '\n')

def run_test_cases(user_code, test_cases):
    """여러 테스트 케이스를 실행하고 결과를 반환"""
    results = []
    all_passed = True
    
    for i, test_case in enumerate(test_cases):
        test_input = test_case.get('input', '')
        expected_output = normalize_output(test_case.get('output', ''))
        
        # 코드 실행
        output, error = execute_user_code(user_code, test_input)
        
        if error:
            results.append({
                'test_num': i + 1,
                'passed': False,
                'error': error,
                'input': test_input,
                'expected': expected_output,
                'actual': None
            })
            all_passed = False
        else:
            actual_output = normalize_output(output)
            passed = (expected_output == actual_output)
            
            if not passed:
                all_passed = False
            
            results.append({
                'test_num': i + 1,
                'passed': passed,
                'input': test_input,
                'expected': expected_output,
                'actual': actual_output
            })
    
    return all_passed, results

# ==========================================
# 4. 결과 리포트 화면
# ==========================================
def show_report_page():
    st.title("📊 테스트 결과 리포트")
    st.markdown("---")
    
    col1, col2, col3 = st.columns(3)
    col1.metric("수험자", st.session_state['user_name'])
    
    start_dt = datetime.strptime(st.session_state['start_time'], "%H:%M:%S")
    end_dt = datetime.strptime(st.session_state['end_time'], "%H:%M:%S")
    duration = end_dt - start_dt
    col2.metric("소요 시간", str(duration))
    
    total_solved = sum(1 for v in st.session_state['solve_status'].values() 
                       if (isinstance(v, dict) and v.get("status") == "PASS") or v == "PASS")
    total_problems = sum(PROBLEMS_PER_CHAPTER for _ in CHAPTERS_INFO)  # 각 단원당 10문제씩
    score = (total_solved / total_problems) * 100 if total_problems > 0 else 0
    
    col3.metric("총 점수", f"{score:.1f}점", f"{total_solved} / {total_problems} 문제")

    st.markdown("### 📈 단원별 성취도")
    
    report_data = []
    for idx, (chapter_name, total_count) in enumerate(CHAPTERS_INFO):
        selected_problems = st.session_state['selected_problems'].get(idx, [])
        selected_count = len(selected_problems)
        pass_count = sum(1 for k, v in st.session_state['solve_status'].items() 
                         if k.startswith(f"{idx}_") and 
                         ((isinstance(v, dict) and v.get("status") == "PASS") or v == "PASS"))
        rate = (pass_count / selected_count) * 100 if selected_count > 0 else 0
        report_data.append({
            "단원": chapter_name,
            "문제수": selected_count,
            "정답": pass_count,
            "정답률": f"{rate:.1f}%"
        })
    
    for item in report_data:
        rate_val = float(item['정답률'].replace('%', ''))
        col_c1, col_c2 = st.columns([1, 3])
        with col_c1:
            st.write(f"**{item['단원']}** ({item['정답']}/{item['문제수']})")
        with col_c2:
            st.progress(rate_val / 100)
    
    st.markdown("---")
    st.success(f"평가 결과가 파일로 저장되었습니다.")
    
    if st.button("처음으로 돌아가기"):
        st.session_state.clear()
        st.rerun()

# ==========================================
# 5. 메인 로직
# ==========================================

def main():
    # --- 로그인 화면 ---
    if not st.session_state['user_name']:
        st.title("📝 파이썬 레벨테스트 입장")
        st.info("이름을 입력하고 평가를 시작하세요.")
        name_input = st.text_input("이름 (Name)")
        if st.button("테스트 시작하기", type="primary"):
            if name_input.strip():
                st.session_state['user_name'] = name_input.strip()
                st.session_state['start_time'] = datetime.now().strftime("%H:%M:%S")
                st.session_state['test_finished'] = False
                st.session_state['selected_problems'] = {}  # 새 테스트 시작 시 문제 목록 초기화
                save_results()
                st.rerun()
            else:
                st.warning("이름을 입력해주세요.")
        return

    # --- 테스트 종료 화면 ---
    if st.session_state['test_finished']:
        show_report_page()
        return

    # --- 메인 테스트 화면 ---
    
    col_info1, col_info2, col_info3 = st.columns([2, 1, 1])
    with col_info1:
        st.markdown(f"### 수험자: **{st.session_state['user_name']}** 님")
    with col_info2:
        st.caption(f"시작: {st.session_state['start_time']}")
    with col_info3:
        if st.button("💾 중간 저장"):
            save_results()
            st.toast("저장 완료")

    st.markdown("---")

    # 사이드바
    st.sidebar.header("학습 목차")
    chapter_names = [info[0] for info in CHAPTERS_INFO]
    selected_chapter = st.sidebar.selectbox("단원 선택", chapter_names)
    
    chapter_idx = chapter_names.index(selected_chapter)
    total_problems_count = CHAPTERS_INFO[chapter_idx][1]
    
    # 랜덤으로 선택된 문제 목록 가져오기
    selected_problems = get_selected_problems_for_chapter(chapter_idx, total_problems_count)
    
    # 문제 번호를 선택된 문제 중에서 선택
    problem_labels = [f"문제 {pid}" for pid in selected_problems]
    selected_label_idx = st.sidebar.selectbox(
        f"문제 선택 (총 {len(selected_problems)}문제 출제)", 
        range(len(problem_labels)),
        format_func=lambda x: problem_labels[x]
    )
    problem_number = selected_problems[selected_label_idx]

    solved_count = sum(1 for k, v in st.session_state['solve_status'].items() 
                       if k.startswith(f"{chapter_idx}_") and isinstance(v, dict) and v.get("status") == "PASS")
    st.sidebar.caption(f"현재 단원 완료: {solved_count} / {len(selected_problems)}")
    st.sidebar.progress(solved_count / len(selected_problems) if len(selected_problems) > 0 else 0)
    
    # 선택된 문제 목록 표시
    with st.sidebar.expander("📋 출제 문제 목록"):
        for i, pid in enumerate(selected_problems):
            prob_key = f"{chapter_idx}_{pid}"
            status_info = st.session_state['solve_status'].get(prob_key, {})
            if isinstance(status_info, dict):
                status = status_info.get("status", "")
                submissions = status_info.get("submissions", 0)
                status_icon = "✅" if status == "PASS" else "❌" if status == "FAIL" else "⭕"
                status_text = f"{status_icon} 문제 {pid}"
                if submissions > 0:
                    status_text += f" ({submissions}회)"
                st.write(status_text)
            else:
                # 기존 형식 호환성
                status_icon = "✅" if status_info == "PASS" else "⭕"
                st.write(f"{status_icon} 문제 {pid}")

    st.sidebar.divider()
    
    # 관리자 페이지 링크
    st.sidebar.markdown("### 관리자")
    admin_url = "http://localhost:8502"  # 관리자 페이지 전용 포트
    st.sidebar.markdown(f"[🔐 관리자 페이지]({admin_url})")
    
    st.sidebar.divider()
    
    if st.sidebar.button("🛑 테스트 종료 및 제출", type="primary", help="평가를 마치고 결과를 확인합니다."):
        st.session_state['end_time'] = datetime.now().strftime("%H:%M:%S")
        st.session_state['test_finished'] = True
        save_results(final=True)
        st.rerun()

    # 문제 로드
    data = load_problem_data(selected_chapter, chapter_idx)
    current_problem = None
    if data and "problems" in data:
        for p in data["problems"]:
            if p["id"] == problem_number:
                current_problem = p
                break
    
    if not current_problem:
        st.error("문제를 불러올 수 없습니다.")
        return

    # 화면 구성
    col1, col2 = st.columns([1, 1])

    with col1:
        prob_key = f"{chapter_idx}_{problem_number}"
        status_info = st.session_state['solve_status'].get(prob_key, {})
        status_text = ""
        if isinstance(status_info, dict):
            status = status_info.get("status", "")
            submissions = status_info.get("submissions", 0)
            status_icon = "✅" if status == "PASS" else "❌" if status == "FAIL" else ""
            status_text = f" {status_icon}"
            if submissions > 0:
                status_text += f" (제출: {submissions}회)"
        else:
            # 기존 형식 호환성
            status_icon = "✅" if status_info == "PASS" else ""
            status_text = f" {status_icon}"
        
        st.subheader(f"Q{problem_number}. {current_problem['title']}{status_text}")
        st.info(f"**문제 설명**\n\n{current_problem['description']}")
        
        # test_cases가 있으면 첫 번째 테스트 케이스를 예시로 표시
        test_cases = current_problem.get('test_cases', [])
        if test_cases:
            first_test = test_cases[0]
            st.markdown("#### 실행 예시")
            c1, c2 = st.columns(2)
            with c1:
                example_input = first_test.get('input', '-')
                st.text_area("입력 예시", example_input if example_input else "(입력 없음)", height=80, disabled=True)
            with c2:
                st.text_area("출력 예시", first_test.get('output', '-'), height=80, disabled=True)
            if len(test_cases) > 1:
                st.caption(f"💡 총 {len(test_cases)}개의 테스트 케이스가 있습니다. 모두 통과해야 정답입니다.")
        else:
            # 기존 형식 호환성 (example_input/example_output)
            st.markdown("#### 실행 예시")
            c1, c2 = st.columns(2)
            with c1:
                st.text_area("입력 예시", current_problem.get('example_input', '-'), height=80, disabled=True)
            with c2:
                st.text_area("출력 예시", current_problem.get('example_output', '-'), height=80, disabled=True)

    with col2:
        st.subheader("💻 코드 작성")
        editor_key = f"code_{chapter_idx}_{problem_number}"
        input_key = f"input_{chapter_idx}_{problem_number}"
        
        # Ace Editor 설정 (자동완성, 문법 강조)
        user_code = st_ace(
            value=current_problem.get('default_code', '# 여기에 코드를 작성하세요\n'),
            language="python",
            theme="monokai",
            keybinding="vscode",
            font_size=14,
            tab_size=4,
            show_gutter=True,
            show_print_margin=False,
            wrap=True,
            auto_update=True,
            readonly=False,
            min_lines=15,
            key=editor_key
        )
        
        col_in_label, col_in_btn = st.columns([2, 1])
        with col_in_label:
            st.caption("**표준 입력 (Standard Input)**")
        with col_in_btn:
            if test_cases and len(test_cases) > 0:
                if st.button("📥 첫 테스트 입력 가져오기", key=f"btn_copy_{prob_key}"):
                    first_input = test_cases[0].get('input', '')
                    st.session_state[input_key] = first_input
                    st.rerun()
            else:
                if st.button("📥 예시 입력 가져오기", key=f"btn_copy_{prob_key}"):
                    ex_input = current_problem.get('example_input', '')
                    if ex_input != '-':
                        st.session_state[input_key] = ex_input
                        st.rerun()

        if input_key not in st.session_state:
             st.session_state[input_key] = ""
             
        user_inputs = st.text_area("입력값 작성", height=100, key=input_key, label_visibility="collapsed")
        
        if st.button("▶️ 실행 및 채점 (Run & Test)", type="primary", use_container_width=True):
            st.markdown("### 실행 결과")
            
            # test_cases가 있으면 자동 채점, 없으면 기존 방식
            if test_cases:
                all_passed, test_results = run_test_cases(user_code, test_cases)
                
                # 테스트 결과 표시
                for result in test_results:
                    with st.expander(f"테스트 케이스 {result['test_num']} {'✅ 통과' if result['passed'] else '❌ 실패'}", expanded=not result['passed']):
                        if result.get('error'):
                            st.error(f"에러: {result['error']}")
                        else:
                            col_t1, col_t2 = st.columns(2)
                            with col_t1:
                                st.text("입력:")
                                st.code(result['input'] if result['input'] else "(입력 없음)", language="text")
                                st.text("예상 출력:")
                                st.code(result['expected'], language="text")
                            with col_t2:
                                st.text("실제 출력:")
                                st.code(result['actual'], language="text")
                                if not result['passed']:
                                    st.warning("❌ 출력이 일치하지 않습니다.")
                
                # 최종 결과
                # 제출 횟수 업데이트
                if prob_key not in st.session_state['solve_status']:
                    st.session_state['solve_status'][prob_key] = {
                        "status": "FAIL",
                        "submissions": 0,
                        "first_pass": None
                    }
                
                st.session_state['solve_status'][prob_key]["submissions"] += 1
                
                if all_passed:
                    st.balloons()
                    st.success(f"🎉 모든 테스트 케이스 통과! 정답입니다! ({len(test_cases)}/{len(test_cases)})")
                    st.session_state['solve_status'][prob_key]["status"] = "PASS"
                    if st.session_state['solve_status'][prob_key]["first_pass"] is None:
                        st.session_state['solve_status'][prob_key]["first_pass"] = st.session_state['solve_status'][prob_key]["submissions"]
                    save_results()
                else:
                    passed_count = sum(1 for r in test_results if r['passed'])
                    st.error(f"❌ 테스트 실패: {passed_count}/{len(test_cases)} 통과")
                    st.session_state['solve_status'][prob_key]["status"] = "FAIL"
                    save_results()
                
                # 제출 횟수 표시
                submissions = st.session_state['solve_status'][prob_key]["submissions"]
                status = st.session_state['solve_status'][prob_key]["status"]
                if status == "PASS":
                    first_pass = st.session_state['solve_status'][prob_key]["first_pass"]
                    st.info(f"✅ 정답! (제출 횟수: {submissions}회, {first_pass}회째에 정답)")
                else:
                    st.info(f"❌ 오답 (제출 횟수: {submissions}회)")
            else:
                # 기존 방식 (단일 출력 비교)
                output, error = execute_user_code(user_code, user_inputs)
                
                if error:
                    st.markdown(f"""<div style="background-color:#2d0a0a; color:#ff6b6b; padding:15px; border-radius:5px; font-family:monospace; white-space:pre-wrap;">🚫 에러 발생:\n{error}</div>""", unsafe_allow_html=True)
                else:
                    display_output = output if output else "(출력값이 없습니다)"
                    st.markdown(f"""<div style="background-color:#0e1117; color:#00ff00; padding:15px; border-radius:5px; font-family:monospace; white-space:pre-wrap; border:1px solid #333;">{display_output}</div>""", unsafe_allow_html=True)
                    
                    expected = current_problem.get('example_output', '').strip()
                    actual = normalize_output(output)
                    
                    # 제출 횟수 업데이트
                    if prob_key not in st.session_state['solve_status']:
                        st.session_state['solve_status'][prob_key] = {
                            "status": "FAIL",
                            "submissions": 0,
                            "first_pass": None
                        }
                    
                    st.session_state['solve_status'][prob_key]["submissions"] += 1
                    
                    if expected and expected != "-" and expected == actual:
                        st.balloons()
                        st.success("정답입니다! 완벽해요 🎉")
                        st.session_state['solve_status'][prob_key]["status"] = "PASS"
                        if st.session_state['solve_status'][prob_key]["first_pass"] is None:
                            st.session_state['solve_status'][prob_key]["first_pass"] = st.session_state['solve_status'][prob_key]["submissions"]
                        save_results()
                        submissions = st.session_state['solve_status'][prob_key]["submissions"]
                        first_pass = st.session_state['solve_status'][prob_key]["first_pass"]
                        st.info(f"✅ 정답! (제출 횟수: {submissions}회, {first_pass}회째에 정답)")
                    elif expected and expected != "-":
                        st.warning("결과가 예시와 다릅니다. 다시 확인해보세요.")
                        st.session_state['solve_status'][prob_key]["status"] = "FAIL"
                        save_results()
                        submissions = st.session_state['solve_status'][prob_key]["submissions"]
                        st.info(f"❌ 오답 (제출 횟수: {submissions}회)")

if __name__ == "__main__":
    main()
