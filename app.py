import streamlit as st
import json
import random
from auth import signup, login

# ---------------- PAGE CONFIG ----------------
st.set_page_config(page_title="Career Recommendation App", layout="wide")


# ---------------- LOAD JSON DATA ----------------
def load_json(file_name):
    try:
        with open(file_name, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        st.error(f"Error loading {file_name}: {e}")
        return {}


# ---------------- MAIN APP FUNCTION ----------------
def main_app():
    st.title(" Personal Skill Gap Analyzer")
    st.write("Discover suitable careers, companies, skill gaps, free learning resources, and mock tests.")

    jobs_data = load_json("jobs.json")
    companies_data = load_json("companies.json")
    courses_data = load_json("courses.json")
    mock_tests_data = load_json("mock_tests.json")

    # ---------------- USER INPUT ----------------
    st.header(" Enter Your Skills")
    user_input = st.text_area(
        "Type your skills separated by commas (example: Python, SQL, Communication, Creativity)"
    )

    if user_input:
        user_skills = [skill.strip().lower() for skill in user_input.split(",")]

        # ---------------- CAREER MATCHING ----------------
        st.header(" Best Career Matches")

        career_scores = {}

        for career, details in jobs_data.items():
            required_skills = [skill.lower() for skill in details["required_skills"]]

            matched_skills = [skill for skill in user_skills if skill in required_skills]

            score = len(matched_skills)

            if score > 0:
                career_scores[career] = {
                    "score": score,
                    "matched_skills": matched_skills,
                    "missing_skills": [
                        skill for skill in required_skills if skill not in user_skills
                    ],
                }

        if career_scores:
            sorted_careers = sorted(
                career_scores.items(),
                key=lambda x: x[1]["score"],
                reverse=True,
            )

            for career, info in sorted_careers[:5]:
                st.subheader(f" {career}")
                st.success(f"Matched Skills: {', '.join(info['matched_skills'])}")
                st.warning(f"Skills to Improve: {', '.join(info['missing_skills'])}")

                # ---------------- COMPANIES ----------------
                if career in companies_data:
                    st.markdown("###  Top Companies")
                    for company in companies_data[career]:
                        st.write(f"**{company['name']}**")
                        st.write(f"Level: {company['level']}")
                        st.write(f"Roles: {', '.join(company['roles'])}")
                        st.write(f"Required Skills: {', '.join(company['required_skills'])}")
                        st.markdown(f"[Visit Careers Page]({company['website']})")
                        st.markdown("---")

                # ---------------- COURSES ----------------
                if career in courses_data:
                    st.markdown("###  Free Skill Gap Learning Resources")

                    shown_courses = set()

                    for missing_skill in info["missing_skills"]:
                        for course_skill, course_details in courses_data[career].items():
                            if (
                                missing_skill.lower() in course_skill.lower()
                                and course_skill not in shown_courses
                            ):
                                shown_courses.add(course_skill)

                                st.write(f"**{course_skill}**")
                                st.markdown(
                                    f"[{course_details['course_name']}]({course_details['link']})"
                                )

                st.markdown("-----")

        else:
            st.error("No strong career match found. Try adding more skills.")

    # ---------------- MOCK TEST SECTION ----------------
    st.header(" Practice Mock Tests")

    if mock_tests_data:
        test_category = st.selectbox(
            "Choose Mock Test Category",
            list(mock_tests_data.keys()),
        )

        questions = mock_tests_data[test_category]

        user_answers = []

        for i, q in enumerate(questions):
            st.subheader(f"Q{i+1}: {q['question']}")

            user_answer = st.radio(
                f"Choose answer for Q{i+1}",
                q["options"],
                index=None,
                key=f"q_{test_category}_{i}",
            )

            user_answers.append(user_answer)

        if st.button("Submit Test"):
            score = 0

            for i, q in enumerate(questions):
                if user_answers[i] == q["answer"]:
                    score += 1

            total_questions = len(questions)
            percentage = (score / total_questions) * 100

            st.success(f" Your Score: {score}/{total_questions} ({percentage:.1f}%)")

            if percentage >= 80:
                st.balloons()
                st.success("Excellent! You're highly prepared.")
            elif percentage >= 50:
                st.info("Good job! Keep improving.")
            else:
                st.warning("Needs improvement. Focus on skill-building.")

            with st.expander(" Review Answers"):
                for i, q in enumerate(questions):
                    st.write(f"**Q{i+1}: {q['question']}**")
                    st.write(f"Your Answer: {user_answers[i]}")
                    st.write(f"Correct Answer: {q['answer']}")

                    if user_answers[i] == q["answer"]:
                        st.success("Correct ")
                    else:
                        st.error("Incorrect ")

                    st.markdown("---")

    # ---------------- RANDOM CAREER EXPLORER ----------------
    st.header("Explore Random Career Paths")

    if st.button("Suggest Random Careers"):
        random_careers = random.sample(
            list(jobs_data.keys()),
            min(5, len(jobs_data)),
        )

        for career in random_careers:
            st.write(f" {career}")

    # ---------------- LOGOUT ----------------
    st.sidebar.success(f"Logged in as: {st.session_state.username}")

    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.session_state.username = ""
        st.rerun()

    # ---------------- FOOTER ----------------
    st.markdown("---")
    st.caption("Built using Streamlit | Career Recommendation System")


# ---------------- LOGIN / SIGNUP SYSTEM ----------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "username" not in st.session_state:
    st.session_state.username = ""

if not st.session_state.logged_in:
    st.title(" Welcome to Personal Skill Gap Analyzer")

    menu = ["Login", "Signup"]
    choice = st.sidebar.selectbox("Menu", menu)

    if choice == "Signup":
        st.subheader(" Create New Account")
        new_user = st.text_input("Username")
        new_password = st.text_input("Password", type="password")

        if st.button("Signup"):
            if new_user and new_password:
                success, message = signup(new_user, new_password)

                if success:
                    st.success(message)
                    st.info("Go to Login to access your account.")
                else:
                    st.error(message)
            else:
                st.warning("Please enter both username and password.")

    elif choice == "Login":
        st.subheader(" Login to Your Account")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")

        if st.button("Login"):
            if username and password:
                success, message = login(username, password)

                if success:
                    st.session_state.logged_in = True
                    st.session_state.username = username
                    st.success(message)
                    st.rerun()
                else:
                    st.error(message)
            else:
                st.warning("Please enter both username and password.")

else:
    main_app()