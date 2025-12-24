import streamlit as st
import json
import os
from datetime import datetime
import pandas as pd

st.set_page_config(page_title="관리자 페이지", layout="wide")

RESULTS_DIR = "results"
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
PROBLEMS_PER_CHAPTER = 10

def load_all_results():
    """모든 결과 파일 로드"""
    if not os.path.exists(RESULTS_DIR):
        return []
    
    results = []
    for filename in os.listdir(RESULTS_DIR):
        if filename.endswith("_result.json"):
            filepath = os.path.join(RESULTS_DIR, filename)
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    results.append(data)
            except:
                continue
    
    return results

def calculate_score(solve_status, selected_problems):
    """점수 계산"""
    if not solve_status:
        return 0, 0, 0
    
    # selected_problems가 없으면 solve_status의 키에서 추정
    if not selected_problems:
        # 기존 형식 호환: chapter_idx_problemId 형식에서 추정
        total_problems = len(solve_status)
    else:
        total_problems = sum(len(probs) for probs in selected_problems.values() if isinstance(probs, list))
    
    if total_problems == 0:
        return 0, 0, 0
    
    pass_count = 0
    for key, value in solve_status.items():
        if isinstance(value, dict):
            if value.get("status") == "PASS":
                pass_count += 1
        elif value == "PASS":
            pass_count += 1
    
    score = (pass_count / total_problems) * 100 if total_problems > 0 else 0
    return pass_count, total_problems, score

def get_chapter_scores(solve_status, selected_problems):
    """단원별 점수"""
    chapter_scores = []
    for idx, (chapter_name, _) in enumerate(CHAPTERS_INFO):
        if selected_problems:
            chapter_problems = selected_problems.get(str(idx), [])
            if not chapter_problems:
                chapter_problems = selected_problems.get(idx, [])
        else:
            # selected_problems가 없으면 solve_status에서 추정
            chapter_problems = []
            for key in solve_status.keys():
                if key.startswith(f"{idx}_"):
                    try:
                        pid = int(key.split("_")[1])
                        chapter_problems.append(pid)
                    except:
                        pass
        
        pass_count = 0
        for pid in chapter_problems:
            prob_key = f"{idx}_{pid}"
            status_info = solve_status.get(prob_key, {})
            if isinstance(status_info, dict):
                if status_info.get("status") == "PASS":
                    pass_count += 1
            elif status_info == "PASS":
                pass_count += 1
        
        total = len(chapter_problems)
        rate = (pass_count / total * 100) if total > 0 else 0
        chapter_scores.append({
            "단원": chapter_name,
            "정답": pass_count,
            "총 문제": total,
            "정답률": f"{rate:.1f}%"
        })
    
    return chapter_scores

def main():
    st.title("📊 관리자 페이지 - 학생 테스트 결과 관리")
    st.markdown("---")
    
    # 비밀번호 확인 (간단한 보안)
    if 'admin_authenticated' not in st.session_state:
        password = st.text_input("관리자 비밀번호를 입력하세요", type="password")
        if st.button("로그인"):
            # 기본 비밀번호: admin (실제로는 환경변수나 설정 파일에서 가져와야 함)
            if password == "admin":
                st.session_state['admin_authenticated'] = True
                st.rerun()
            else:
                st.error("비밀번호가 올바르지 않습니다.")
        return
    
    # 모든 결과 로드
    all_results = load_all_results()
    
    if not all_results:
        st.warning("아직 테스트 결과가 없습니다.")
        return
    
    # 전체 통계
    st.header("📈 전체 통계")
    col1, col2, col3, col4 = st.columns(4)
    
    total_students = len(set(r['user_name'] for r in all_results))
    finished_tests = sum(1 for r in all_results if r.get('is_finished', False))
    total_tests = len(all_results)
    
    with col1:
        st.metric("총 학생 수", total_students)
    with col2:
        st.metric("완료된 테스트", finished_tests)
    with col3:
        st.metric("진행 중인 테스트", total_tests - finished_tests)
    with col4:
        avg_score = 0
        if finished_tests > 0:
            scores = []
            for r in all_results:
                if r.get('is_finished', False):
                    selected = r.get('selected_problems', {})
                    _, _, score = calculate_score(r.get('solve_status', {}), selected)
                    scores.append(score)
            avg_score = sum(scores) / len(scores) if scores else 0
        st.metric("평균 점수", f"{avg_score:.1f}점")
    
    st.markdown("---")
    
    # 학생 목록 및 검색
    st.header("👥 학생 목록")
    
    # 검색 기능
    search_term = st.text_input("🔍 학생 이름 검색", "")
    
    # 학생별로 그룹화
    student_data = {}
    for result in all_results:
        name = result['user_name']
        if search_term and search_term.lower() not in name.lower():
            continue
        
        if name not in student_data:
            student_data[name] = []
        student_data[name].append(result)
    
    # 학생별로 정렬 (최신순)
    sorted_students = sorted(student_data.items(), 
                            key=lambda x: max(r.get('date', '') for r in x[1]), 
                            reverse=True)
    
    # 탭으로 구분
    tab1, tab2 = st.tabs(["학생 목록", "상세 통계"])
    
    with tab1:
        # 학생별 요약 테이블
        summary_data = []
        for name, results in sorted_students:
            latest = max(results, key=lambda x: x.get('date', ''))
            selected = latest.get('selected_problems', {})
            pass_count, total, score = calculate_score(latest.get('solve_status', {}), selected)
            
            summary_data.append({
                "학생 이름": name,
                "최근 테스트 날짜": latest.get('date', ''),
                "완료 여부": "✅ 완료" if latest.get('is_finished', False) else "⏳ 진행중",
                "정답 수": f"{pass_count}/{total}",
                "점수": f"{score:.1f}점",
                "이탈 횟수": len(latest.get('exit_logs', [])),
                "테스트 횟수": len(results)
            })
        
        if summary_data:
            df = pd.DataFrame(summary_data)
            st.dataframe(df, use_container_width=True, hide_index=True)
        else:
            st.info("검색 결과가 없습니다.")
    
    with tab2:
        # 선택한 학생의 상세 정보
        if sorted_students:
            student_names = [name for name, _ in sorted_students]
            selected_student = st.selectbox("학생 선택", student_names)
            
            student_results = student_data[selected_student]
            latest_result = max(student_results, key=lambda x: x.get('date', ''))
            
            st.subheader(f"📋 {selected_student}님의 테스트 결과")
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("테스트 날짜", latest_result.get('date', ''))
            with col2:
                st.metric("시작 시간", latest_result.get('start_time', ''))
            with col3:
                exit_count = len(latest_result.get('exit_logs', []))
                st.metric("화면 이탈 횟수", f"{exit_count}회", delta="부정행위 주의" if exit_count > 0 else None, delta_color="inverse")
            
            # 이탈 로그 상세
            if exit_count > 0:
                with st.expander("🔍 화면 이탈 상세 시간"):
                    for i, log in enumerate(latest_result.get('exit_logs', [])):
                        st.write(f"{i+1}. {log}")
            
            # 점수 정보
            selected = latest_result.get('selected_problems', {})
            pass_count, total, score = calculate_score(latest_result.get('solve_status', {}), selected)
            
            st.markdown("### 📊 점수 정보")
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("정답 수", f"{pass_count}/{total}")
            with col2:
                st.metric("점수", f"{score:.1f}점")
            with col3:
                st.metric("정답률", f"{(pass_count/total*100) if total > 0 else 0:.1f}%")
            
            # 단원별 성취도
            st.markdown("### 📈 단원별 성취도")
            chapter_scores = get_chapter_scores(latest_result.get('solve_status', {}), selected)
            
            for item in chapter_scores:
                rate_val = float(item['정답률'].replace('%', ''))
                col_c1, col_c2 = st.columns([1, 3])
                with col_c1:
                    st.write(f"**{item['단원']}** ({item['정답']}/{item['총 문제']})")
                with col_c2:
                    st.progress(rate_val / 100)
            
            # 제출 횟수 통계
            st.markdown("### 📝 제출 횟수 통계")
            solve_status = latest_result.get('solve_status', {})
            total_submissions = 0
            pass_submissions = []
            fail_submissions = []
            
            for key, value in solve_status.items():
                if isinstance(value, dict):
                    submissions = value.get('submissions', 0)
                    total_submissions += submissions
                    if value.get('status') == 'PASS':
                        first_pass = value.get('first_pass', submissions)
                        pass_submissions.append(first_pass)
                    else:
                        fail_submissions.append(submissions)
            
            if total_submissions > 0:
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("총 제출 횟수", total_submissions)
                with col2:
                    avg_pass = sum(pass_submissions) / len(pass_submissions) if pass_submissions else 0
                    st.metric("평균 정답 도달 횟수", f"{avg_pass:.1f}회")
                with col3:
                    avg_fail = sum(fail_submissions) / len(fail_submissions) if fail_submissions else 0
                    st.metric("평균 오답 제출 횟수", f"{avg_fail:.1f}회")
            
            # 문제별 상세 정보
            st.markdown("### 📋 문제별 상세 정보")
            with st.expander("문제별 정답/오답 및 제출 횟수 보기"):
                problem_details = []
                solve_status = latest_result.get('solve_status', {})
                
                if selected:
                    # selected_problems가 있는 경우
                    for idx, (chapter_name, _) in enumerate(CHAPTERS_INFO):
                        chapter_problems = selected.get(str(idx), selected.get(idx, []))
                        for pid in chapter_problems:
                            prob_key = f"{idx}_{pid}"
                            status_info = solve_status.get(prob_key, {})
                            
                            if isinstance(status_info, dict):
                                status = status_info.get('status', '미제출')
                                submissions = status_info.get('submissions', 0)
                                first_pass = status_info.get('first_pass', None)
                                
                                problem_details.append({
                                    "단원": chapter_name,
                                    "문제 번호": pid,
                                    "상태": "✅ 정답" if status == "PASS" else "❌ 오답" if status == "FAIL" else "⭕ 미제출",
                                    "제출 횟수": submissions,
                                    "정답 도달 횟수": first_pass if first_pass else "-"
                                })
                            elif status_info:  # 기존 형식
                                problem_details.append({
                                    "단원": chapter_name,
                                    "문제 번호": pid,
                                    "상태": "✅ 정답" if status_info == "PASS" else "❌ 오답" if status_info == "FAIL" else "⭕ 미제출",
                                    "제출 횟수": "-",
                                    "정답 도달 횟수": "-"
                                })
                else:
                    # selected_problems가 없는 경우 (기존 형식)
                    for key, value in solve_status.items():
                        try:
                            parts = key.split('_')
                            if len(parts) == 2:
                                idx = int(parts[0])
                                pid = int(parts[1])
                                chapter_name = CHAPTERS_INFO[idx][0] if idx < len(CHAPTERS_INFO) else f"단원{idx}"
                                
                                if isinstance(value, dict):
                                    status = value.get('status', '미제출')
                                    submissions = value.get('submissions', 0)
                                    first_pass = value.get('first_pass', None)
                                    
                                    problem_details.append({
                                        "단원": chapter_name,
                                        "문제 번호": pid,
                                        "상태": "✅ 정답" if status == "PASS" else "❌ 오답" if status == "FAIL" else "⭕ 미제출",
                                        "제출 횟수": submissions,
                                        "정답 도달 횟수": first_pass if first_pass else "-"
                                    })
                                else:
                                    problem_details.append({
                                        "단원": chapter_name,
                                        "문제 번호": pid,
                                        "상태": "✅ 정답" if value == "PASS" else "❌ 오답" if value == "FAIL" else "⭕ 미제출",
                                        "제출 횟수": "-",
                                        "정답 도달 횟수": "-"
                                    })
                        except:
                            continue
                
                if problem_details:
                    df_details = pd.DataFrame(problem_details)
                    st.dataframe(df_details, use_container_width=True, hide_index=True)
                else:
                    st.info("문제 정보가 없습니다.")
            
            # 이전 테스트 기록
            if len(student_results) > 1:
                st.markdown("### 📚 이전 테스트 기록")
                history_data = []
                for result in sorted(student_results, key=lambda x: x.get('date', ''), reverse=True):
                    selected_h = result.get('selected_problems', {})
                    pass_c, total_h, score_h = calculate_score(result.get('solve_status', {}), selected_h)
                    history_data.append({
                        "날짜": result.get('date', ''),
                        "완료 여부": "✅" if result.get('is_finished', False) else "⏳",
                        "점수": f"{score_h:.1f}점",
                        "정답 수": f"{pass_c}/{total_h}"
                    })
                
                df_history = pd.DataFrame(history_data)
                st.dataframe(df_history, use_container_width=True, hide_index=True)
    
    # 로그아웃 및 메인 이동
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 이동")
    main_url = "http://localhost:8501"
    st.sidebar.markdown(f"[📝 테스트 페이지로 이동]({main_url})")
    
    if st.sidebar.button("로그아웃"):
        st.session_state['admin_authenticated'] = False
        st.rerun()

if __name__ == "__main__":
    main()

