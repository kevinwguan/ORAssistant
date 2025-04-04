import streamlit as st
from dotenv import load_dotenv
import os

from human_evaluation.utils.sheets import (
    read_questions_and_answers,
    write_responses,
    find_new_questions,
)
from human_evaluation.utils.api import fetch_endpoints, get_responses
from human_evaluation.utils.utils import (
    parse_custom_input,
    selected_questions,
    update_gform,
    read_question_and_description,
)


def main() -> None:
    load_dotenv()

    google_sheet_id = os.getenv("GOOGLE_SHEET_ID")
    google_form_id = os.getenv("GOOGLE_FORM_ID")

    if not google_sheet_id:
        st.error("GOOGLE_SHEET_ID is not set in the environment variables.")
        return

    if not google_form_id:
        st.error("GOOGLE_FORM_ID is not set in the environment variables.")
        return

    st.title("OR Assistant: Populate Human Evaluation Form")

    st.write(f"""
    Add questions to be tested by OR Assistant in this Google Sheet:
    [Google Sheet Link](https://docs.google.com/spreadsheets/d/{google_sheet_id}/edit)
    """)

    endpoints = fetch_endpoints()

    selected_endpoint = st.selectbox(
        "Select preferred architecture",
        options=endpoints,
        index=0,
        format_func=lambda x: x.split("/")[-1].capitalize(),
    )

    options = ["", "All", "All New Questions", "Custom"]
    selected_option = st.selectbox(
        "Choose which set of questions you want to be generated by the model:", options
    )

    questions: list[str] = []
    question_count: int = 0
    custom_input: str = ""
    parsed_values: list[int] = []
    valid_input: bool = True

    if selected_option:
        questions, question_count = read_questions_and_answers()

        if selected_option == "Custom":
            custom_input = st.text_input(
                "Specify the range or list of row numbers starting from 2:"
            )

            with st.expander("Instructions for Custom Input"):
                st.markdown("""
                - **Single values**: Enter individual row numbers separated by commas (e.g., `2,3,4`).
                - **Range of values**: Use a hyphen to specify a range (e.g., `2-5` translates to `2,3,4,5`).
                - **Mixed ranges and single values**: Combine both methods separated by commas (e.g., `2-3,4-6` translates to `2,3,4,5,6`).
                - **Open-ended ranges**: Use a hyphen without an ending number to specify all values starting from a number (e.g., `4-` translates to all values from `4` up to the maximum value in the dataset).
                - Note: Values starting from `1` are not allowed and will result in an error.
                """)

            if custom_input:
                try:
                    parsed_values = parse_custom_input(custom_input, question_count)
                    if 1 in parsed_values:
                        valid_input = False
                        st.error("Parsed values cannot include 1.")
                    else:
                        valid_input = True
                except ValueError:
                    valid_input = False
                    st.error("Please enter a valid range or list of row numbers.")

        elif selected_option == "All New Questions":
            parsed_values = find_new_questions(question_count)

        elif selected_option == "All":
            parsed_values = parse_custom_input("2-", question_count)

    button_disabled = (
        selected_option == ""
        or (
            selected_option == "Custom"
            and not (custom_input and parsed_values and valid_input)
        )
        or question_count == 0
    )

    if st.button(
        "Click this button to process (takes time depending on the number of questions)",
        disabled=button_disabled,
    ):
        if questions:
            progress = st.progress(0)
            status_text = st.empty()
            current_question_text = st.empty()

            with st.spinner("Processing..."):
                questions_descriptions = read_question_and_description()
                if not all(isinstance(qd, dict) for qd in questions_descriptions):
                    st.error(
                        "Invalid data format from Google Sheet. Ensure it has appropriate questions and descriptions."
                    )
                    questions_descriptions = []

                questions_to_process = selected_questions(questions, parsed_values)
                responses = get_responses(
                    questions_to_process,
                    progress,
                    status_text,
                    current_question_text,
                    selected_endpoint,  # type: ignore
                )
                updated_cells = write_responses(responses, parsed_values)
                st.success("Answers generated successfully")

                questions_descriptions = read_question_and_description()
                update_gform(questions_descriptions)
                st.success(
                    f"{updated_cells} cells updated successfully! Here is the Google Form: [Google Form Link](https://docs.google.com/forms/d/{google_form_id})"
                )
        else:
            st.error("No questions found in the Google Sheet.")


if __name__ == "__main__":
    main()
