##########chat_sql_ui.py########

'''

cd /code/
streamlit run chat_sql_ui.py --server.port 3412 –-server.address=0.0.0.0

localhost:3412


'''

import os
import re
import requests
import numpy as np
import pandas as pd
import streamlit as st
from streamlit_chat import message
from streamlit.components.v1 import html

import streamlit as st
import plotly.express as px

from chat_api_api import question_to_answer
from chat_sql_figure_api import *

st.set_page_config(
	page_title='Chat with Database', 
	layout = 'centered', 
	page_icon = 'logo.png', 
	initial_sidebar_state = 'collapsed')

st.title("Chat with Database")

##

if "messages" not in st.session_state:
	st.session_state.messages = []

for message in st.session_state.messages:
	with st.chat_message(message["role"]):
		st.markdown(message["content"])

##

# React to user input
if prompt := st.chat_input():

	with st.chat_message("user"):
		st.markdown(prompt)

	st.session_state.messages.append({"role": "user", "content": prompt})

	# question to sql and dataframe
	df, sql = question_to_dataframe(prompt)

	sql_response = f"""
Querying the database by SQL query:
~~~sql
{sql}
~~~
"""
	
	# show the sql
	with st.chat_message("assistant"):
		st.markdown(sql_response)
		st.dataframe(df, use_container_width=True)


	# show the figure

	if len(df) > 1:

		code = df_to_python_code(df)

		code += '\nst.plotly_chart(fig, key="iris", on_select="rerun")'

		with st.chat_message("assistant"):
			st.markdown(f"""
Generating the figure of the data by Python code:
~~~python
{code}
~~~
""")
			exec(code)	

	# generate answer
	answer = df_to_answer(
		df = df, 
		quetion = prompt,
		sql = sql,
		)

	with st.chat_message("assistant"):
		st.markdown(answer)

	st.session_state.messages.append({"role": "assistant", "content": answer})






##########chat_sql_ui.py########