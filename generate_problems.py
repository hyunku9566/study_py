import json
import os

# 챕터 정보 (챕터명, 문제 수)
CHAPTERS_INFO = [
    ("출력", 16),
    ("변수와 입력", 21),
    ("연산자", 25),
    ("문자열1", 19),
    ("리스트 1", 22),
    ("선택제어문", 22),
    ("디버깅", 5),
    ("반복제어문 1", 17),
    ("반복제어문 2", 30),
    ("반복제어문 3", 25),
    ("문자열 2", 24),
    ("리스트 2", 26),
    ("리스트 3", 30),
    ("기타 자료형", 21),
    ("함수 1", 21),
    ("함수 2", 18),
    ("함수 3 - 재귀함수", 19),
    ("클래스", 17),
    ("파일입출력", 10)
]

# 미리 넣어둘 실제 예시 문제들
REAL_PROBLEMS = {
    "출력": {
        1: {
            "title": "Hello World",
            "description": "화면에 'Hello World'를 출력하시오.",
            "ex_in": "-", "ex_out": "Hello World",
            "code": "print('Hello World')"
        },
        2: {
            "title": "두 줄 출력",
            "description": "다음과 같이 두 줄을 출력하시오.\n\nPython\nProgramming",
            "ex_in": "-", "ex_out": "Python\nProgramming",
            "code": "print('Python')\nprint('Programming')"
        },
        3: {
            "title": "특수문자 출력",
            "description": "화면에 '!@#$%^&*()' 를 출력하시오.",
            "ex_in": "-", "ex_out": "!@#$%^&*()",
            "code": "print('!@#$%^&*()')"
        }
    },
    "변수와 입력": {
        1: {
            "title": "정수형 변수",
            "description": "변수 a에 10을 저장하고 출력하시오.",
            "ex_in": "-", "ex_out": "10",
            "code": "a = 10\nprint(a)"
        },
        2: {
            "title": "입력 받아 출력하기",
            "description": "키보드로 문자열 하나를 입력받아 그대로 출력하시오.\n(실행 시 입력창이 없으므로 input() 함수 사용 시 예시 입력을 활용합니다)",
            "ex_in": "Hello", "ex_out": "Hello",
            "code": "a = input()\nprint(a)"
        }
    },
    "연산자": {
        1: {
            "title": "합계 구하기",
            "description": "두 수 10과 20의 합을 출력하시오.",
            "ex_in": "-", "ex_out": "30",
            "code": "print(10 + 20)"
        },
        2: {
            "title": "몫과 나머지",
            "description": "10을 3으로 나눈 몫과 나머지를 각각 줄을 바꿔 출력하시오.",
            "ex_in": "-", "ex_out": "3\n1",
            "code": "print(10 // 3)\nprint(10 % 3)"
        }
    },
    "선택제어문": {
        1: {
            "title": "양수 판별",
            "description": "변수 n이 10일 때, 양수이면 'positive'를 출력하는 코드를 작성하시오.",
            "ex_in": "-", "ex_out": "positive",
            "code": "n = 10\nif n > 0:\n    print('positive')"
        }
    }
}

PROBLEMS_DIR = "problems"
os.makedirs(PROBLEMS_DIR, exist_ok=True)

print("문제 파일 생성을 시작합니다...")

for idx, (chapter_name, count) in enumerate(CHAPTERS_INFO):
    problems_list = []
    
    # 미리 준비된 예제 문제 가져오기
    chapter_real_data = REAL_PROBLEMS.get(chapter_name, {})
    
    for i in range(1, count + 1):
        if i in chapter_real_data:
            # 실제 데이터가 있는 경우
            p = chapter_real_data[i]
            problem = {
                "id": i,
                "title": p["title"],
                "description": p["description"],
                "example_input": p["ex_in"],
                "example_output": p["ex_out"],
                "default_code": p["code"]
            }
        else:
            # 데이터가 없는 경우 템플릿 생성
            problem = {
                "id": i,
                "title": f"[{chapter_name}] 문제 {i}",
                "description": f"이 문제는 '{chapter_name}' 단원의 {i}번째 문제입니다.\n\n문제를 풀어보세요!",
                "example_input": "입력 예시 없음",
                "example_output": "출력 예시 없음",
                "default_code": f"# {i}번 문제 풀이\n"
            }
        problems_list.append(problem)
    
    # JSON 구조 생성
    data = {
        "chapter_name": chapter_name,
        "problems": problems_list
    }
    
    # 파일 저장 (예: 01_출력.json)
    filename = f"{idx+1:02d}_{chapter_name}.json"
    filepath = os.path.join(PROBLEMS_DIR, filename)
    
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"- 생성 완료: {filename} (총 {count}문제)")

print("\n모든 문제 파일이 생성되었습니다!")

