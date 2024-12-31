# 레시피북
import pickle
import os
import json
import streamlit as st
from chatbot import ChatBot
from streamlit_option_menu import option_menu

system_message="""
[지시사항]
당신은 자취요리 같은 간단한 요리를 전문으로 하는 인플루언서입니다.
사용자는 초보라고 생각하고, 쉽고 자세하게 알려줄 것.
사용자가 보유한 재료를 최대한 활용하되, 필요한 재료는 추가하여 1인분 기준의 레시피를 제공할 것.
필요한 재료의 양은 단위와 함께 정확하게 제시할 것.
반드시 출력 형식에서 제시한 것과 같이 JSON형식으로 제시할 것.

[제약사항]
난이도는 상, 중, 하로 각각 나뉩니다.
-상: 필요한 재료가 10가지 이상이거나, 요리 과정이 10단계를 초과. 또는 요리 시간이 30분을 초과하여 소요 예상.
-중: 보유한 재료에서 1~3가지만 추가 하면 만들 수 있으며, 요리 과정이 7~10단계. 그리고, 요리 시간이 30분 이하로 예상.
-하: 보유한 재료들로만 만들 수 있으며, 요리 과정이 7단계 미만. 그리고 요리 시간이 10분 내외로 예상.

[출력 형식]
"메뉴" : "오므라이스",
"난이도" : "하",
"예상 시간": "15분",
"재료" : "당근 1/4개, 양파 1/2개, 쌀밥 150g, 계란 2개, 케첩 2T, 소금 약간, 후추 약간, 식용유 1.5T",

"요리 방법":[
"1. 당근과 양파를 작은 큐브 모양으로 잘게 썰어 준비합니다.",
"2. 팬에 식용유를 1.5T 두르고 중불로 달군 뒤, 썰어둔 당근과 양파를 넣고 약불에서 볶습니다.",
"3. 당근이 부드러워지고 양파가 투명해지면 쌀밥 150g을 넣고 골고루 섞습니다.",
...
"8. 불을 끄고 마무리합니다."  
]
"""


# 재료 저장 및 불러오기 함수
grocery = []
def load_grocery():
    try:
        if os.path.exists("grocery.pkl"):
            with open("grocery.pkl", "rb") as file:
                return pickle.load(file)
    except (EOFError, pickle.UnpicklingError):
        pass
    return []

def save_grocery(grocery_list):
    try:
        with open("grocery.pkl", "wb") as file:
            pickle.dump(grocery_list, file)
    except Exception as e:
        print(f"Error saving grocery list: {e}")


# 챗봇 생성
chatbot = ChatBot("gpt-4o", system_message)

def generate_recipe():
    ingredients = load_grocery()
    if not ingredients:
        return False
    
    user_input = f"{', '.join(ingredients)}."
    try:
        response = chatbot.get_response(user_input)
        return response
    except Exception as e:
        return f"ChatBot 요청 중 오류가 발생했습니다: {e}"

# 레시피 저장 및 로드
def save_recipe(response):
    try:
        if isinstance(response, str):
            parsed_response = json.loads(response)
        elif isinstance(response, dict):
            parsed_response = response
        else:
            raise ValueError("response는 문자열이나 딕셔너리 형식이어야 합니다.")
    except json.JSONDecodeError as e:
        print("JSON 변환 오류:", e)
        return None
    except Exception as e:
        print("알 수 없는 오류:", e)
        return None
    
    try:
        menu_name = parsed_response.get("메뉴")
        with open(f"{menu_name}.txt", "w") as txt_file:
            txt_file.write(response)
    except Exception as e:
        print(f"파일 저장 중 오류가 발생했습니다: {e}")

def load_recipe(recipe):
    st.session_state.recipe = recipe
    try:
        if isinstance(recipe, str):
            data = json.loads(recipe)
        elif isinstance(recipe, dict):
            data = recipe
        else:
            raise ValueError("response는 문자열이나 딕셔너리 형식이어야 합니다.")
        
        dish = data.get("메뉴")
        level = data.get("난이도")
        time = data.get("예상 시간")
        ingredient = data.get("재료")
        process = data["요리 방법"]

        if dish:
            st.markdown(f"### 🍽️메뉴: *{dish}*")
        if level:
            st.markdown(f"### 🎯난이도: *{level}*")
        if time:
            st.markdown(f"### ⌛예상 시간: *{time}*")
        if ingredient:
            st.markdown(f"### 🍅재료: *{ingredient}*")
        if process:
            st.markdown("### *📖요리 방법*")
            for step in process:
                st.markdown(f"#### {step}")

    except:
        st.error("오류가 발생했습니다. 다시 시도해주세요.")

# 저장한 레시피 파일
def list_files():
    return [f for f in os.listdir(".") if os.path.isfile(f) and f.endswith(".txt")]


# 페이지 설정
st.set_page_config(
    page_title="CookClear",
    page_icon="😊",
    layout="wide"
)

# 기본 제목 설정
st.title("🤗CookClear")
st.caption("냉장고를 털어보자.")
st.markdown("---")

# 사이드 바
st.sidebar.markdown("## 메뉴")
st.sidebar.image("cook.webp")

with st.sidebar:
    menu = option_menu("", ["식사 레시피", "간식 레시피", "찜한 레시피", "나의 재료"],
        icons=["egg-fried", "cake", "heart", "box2"],
        default_index=0)
    
if menu == "식사 레시피":   # 나의 재료 메뉴에서 입력한 재료를 바탕으로 AI가 레시피를 제공.
    st.subheader("🍚식사에 적합한 요리를 추천해요!")
    st.markdown("다른 메뉴를 원하시면 '레시피 생성' 버튼을 눌러주세요!")
    st.markdown("---")
    if st.button("레시피 생성"):
        with st.spinner("사용자의 재료를 바탕으로 레시피를 생성중..."):
            recipe = generate_recipe()
            st.session_state.recipe = recipe
            print(recipe)
            if recipe:
                load_recipe(recipe)
            else:
                st.error("재료가 없습니다. 재료를 추가해주세요.")

        if st.session_state.recipe:
            if st.button("레시피 저장"):
                save_recipe(st.session_state.recipe)           
        
    else:
        st.warning("레시피를 생성하려면 재료를 추가하세요!")

    

elif menu == "간식 레시피": 
    st.subheader("🍪간식으로 괜찮은 요리를 추천해요!")
    st.markdown("다른 메뉴를 원하시면 '레시피 생성' 버튼을 눌러주세요!")
    st.markdown("---")
    if "recipe_1" not in st.session_state:
        st.session_state.recipe_1 = None

    # 사용자 입력
    user_input = st.text_input("어떤 간식을 만들고 싶은지 말해주세요!")
    st.session_state.user_input = user_input
    # 레시피 생성 버튼
    if st.button("레시피 생성"):
        with st.spinner("간식 레시피 생성중..."):
            try:  
                recipe_1 = chatbot.get_response(st.session_state.user_input)  # Chatbot에서 응답 생성
                st.session_state.recipe_1 = recipe_1  # 세션 상태에 저장
                print(recipe_1)
                st.markdown("### 생성된 레시피")
                load_recipe(recipe_1)
            except Exception as e:
                st.error(f"레시피 생성 중 오류가 발생했습니다: {e}")

    # 레시피 저장 버튼
    if st.session_state.recipe_1:
        if st.button("레시피 저장"):
            try:
                save_recipe(st.session_state.recipe_1)  # 레시피 저장
            except Exception as e:
                st.error(f"레시피 저장 중 오류가 발생했습니다: {e}")
    else:
        st.info("레시피를 생성한 후 저장할 수 있습니다.")
    

elif menu == "찜한 레시피": # 찜한 레시피를 리스트에 저장하고, 그 api에서 reset시킴.
    st.subheader("📝내가 찜한 레시피에요!")
    st.markdown("---")
    files = list_files()
    if files:
        selected_file = st.selectbox("## 선택한 레시피", files)

        # 파일 불러오기
        if st.button("레시피 불러오기"):
            try:
                with open(selected_file, "r") as file:
                    file_content = file.read()
                load_recipe(file_content)
            except Exception as e:
                st.error(f"An error occurred while reading the file: {e}")

        # 파일 삭제
        if st.button("레시피 삭제"):
            try:
                os.remove(selected_file)
                st.success(f" `{selected_file}`가 삭제되었습니다.")
            except Exception as e:
                st.error(f"An error occurred while deleting the file: {e}")



elif menu == "나의 재료":   # 내가 입력한 재료를 리스트에 저장.
    st.subheader("🥩내가 보유한 재료에요!")
    st.markdown("---")
    if 'grocery' not in st.session_state:
        st.session_state['grocery'] = load_grocery()

    grocery_input = st.text_input(" 재료를 등록하세요!(','와 '공백'으로 구분해주세요.)  재료를 삭제하시려면 한 번 더 입력해주세요!")
    if grocery_input:
        split_values = [item.strip() for item in grocery_input.replace(",", " ").split() if item.strip()]
        for item in split_values:
            if item in st.session_state['grocery']:
                st.session_state['grocery'].remove(item)
            else:
                st.session_state['grocery'].append(item)

        save_grocery(st.session_state['grocery'])

    st.markdown("### 현재 보유한 재료: " + ", ".join(st.session_state['grocery']))

                    
    



    