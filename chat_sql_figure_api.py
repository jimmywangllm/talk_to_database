from langchain_openai import ChatOpenAI

import getpass
import os

llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)


from langchain_community.utilities import SQLDatabase

db = SQLDatabase.from_uri("sqlite:///Chinook.db")


from langchain.chains import create_sql_query_chain

chain = create_sql_query_chain(llm, db)


import pandas as pd
import sqlite3

con = sqlite3.connect("Chinook.db", check_same_thread=False)

def question_to_dataframe(
    question:str,
)->pd.DataFrame:
    
    sql_commend = chain.invoke({"question": question})   
    sql_commend = sql_commend.split(';')[0]

    df = pd.read_sql_query(sql_commend, con)
    
    return df, sql_commend

from openai import OpenAI
client = OpenAI()

def df_to_python_code(df):

	prompt = f"""
	Given a pandas data frame named "df" with the following columns: {list(df.columns)}, generate the code <code> for plotting the data of this dataframe in plotly, in the format requested. The solution should be given using plotly and only plotly. Do not use matplotlib. At the end of the code, just return the generated figure to a variable name as "fig", no need to show it.
	Return the code <code> in the following 
	format ```python <code>```
	"""

	completion = client.chat.completions.create(
	  model="gpt-3.5-turbo",
	  messages=[
	    {"role": "user", "content": prompt}
	  ]
	)


	import re
	response = completion.choices[0].message.content

	# code extracted from the src.llm_utils module
	def extract_python_code(text):
	    pattern = r'```python\s(.*?)```'
	    matches = re.findall(pattern, text, re.DOTALL)
	    if not matches:
	        return None
	    else:
	        return matches[0]

	python_code = extract_python_code(response)

	return python_code


def df_to_answer(
	df, 
	quetion,
	sql,
	):

	data = df.to_dict('records')

	if len(data) > 5:
		data = data[0:5]

	answer_prompt = f"""Given the following user question, corresponding SQL query, and SQL result in JSON format, answer the user question.

	Question: {quetion}
	SQL Query: {sql}
	SQL Result: {data}
	Answer: """

	completion = client.chat.completions.create(
	  model="gpt-3.5-turbo",
	  messages=[
	    {"role": "user", "content": answer_prompt}
	  ]
	)

	return 	completion.choices[0].message.content