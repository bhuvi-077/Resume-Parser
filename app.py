import streamlit as st
from itertools import permutations

def cryptarithmetic_solver(puzzle):
    left, right = puzzle.split('=')
    left_operands = [term.strip() for term in left.split('+')]
    right_operand = right.strip()
    unique_letters = set(''.join(left_operands + [right_operand]))

    if len(unique_letters) > 10:
        st.error("Too many unique letters.")
        return

    for perm in permutations('0123456789', len(unique_letters)):
        mapping = dict(zip(unique_letters, perm))
        if any(mapping[word[0]] == '0' for word in left_operands + [right_operand]):
            continue

        left_values = [int(''.join(mapping[ch] for ch in word)) for word in left_operands]
        right_value = int(''.join(mapping[ch] for ch in right_operand))
        if sum(left_values) == right_value:
            st.success(f"Solution: {dict(zip(unique_letters, [int(mapping[ch]) for ch in unique_letters]))}")
            return

    st.warning("No solution found.")

# Streamlit UI
st.title("Cryptarithmetic Puzzle Solver")
puzzle = st.text_input("Enter puzzle (e.g., SEND + MORE = MONEY):", "SEND + MORE = MONEY")
if st.button("Solve"):
    cryptarithmetic_solver(puzzle)
st.subheader("Project by G. Jitheshwaran")
st.write("Completed a project at AIDS Easwari Engineering College, Ramapuram.")
st.subheader("Follow me on Instagram:")
st.markdown(
    '<a href="https://www.instagram.com/jithu_wwm/" target="_blank">'
    '<img src="https://upload.wikimedia.org/wikipedia/commons/a/a5/Instagram_icon.png" width="50"/>'
    '</a>',
    unsafe_allow_html=True
)