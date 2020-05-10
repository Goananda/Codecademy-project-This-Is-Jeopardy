import pandas as pd
import re
import random

pd.set_option('display.max_colwidth', -1)

def find_words(database, column, word_list, sensitive=False, separated=False):
  if_sens = lambda x: x if sensitive == True else x.lower()
  if_sep = lambda x: "\\b"+x+"\\b" if separated == True else x
  filter = lambda x: all(re.search(if_sep(if_sens(word)), if_sens(x)) for word in word_list)
  return database[database[column].apply(filter)]

def count_words(database, column):
  return database[column].value_counts()

def decade_proportion(database, column, word_list, date, sensitive=False, separated=False):
  decade_data = database[database.air_date.str[0:3] == date]
  word_data = find_words(decade_data, column, word_list, sensitive, separated)
  return str(round(100*len(word_data)/len(decade_data), 2))+"%"

def category_propotions(database, categories):
  category_base = database[database.category.isin(categories)].reset_index()
  count_base = category_base.groupby(['round', 'category'])['show_number'].count().reset_index()
  pivot = count_base.pivot(columns='category', index='round', values='show_number').reset_index()
  round_counts = database.groupby('round')['show_number'].count().reset_index()
  round_counts.rename(columns={'show_number': 'total'}, inplace=True)
  pivot = pivot.merge(round_counts, how='left')
  category_format = lambda row: str(round(100*row[category]/row.total, 2))+'%'
  for category in categories:
    pivot[category] = pivot.apply(category_format, axis=1)
  return pivot

jeopardy = pd.read_csv('jeopardy.csv')
jeopardy.columns = ['show_number', 'air_date', 'round', 'category', 'value', 'question', 'answer']
to_float = lambda x: re.sub("[\D]", "", x) if x != "None" else 0
jeopardy['float_value'] = pd.to_numeric(jeopardy.value.apply(to_float))

result_1 = find_words(jeopardy, 'question', ["King", "England"], separated=True)
result_2 = find_words(jeopardy, 'question', ["King"], separated=True)
avg_value_king = round(result_2.float_value.mean(), 2)
print(f'Average value of questions containing word "King": ${avg_value_king}')
uniq_answers_king = count_words(result_2, "answer")
print(f'\nUnique answers to questions containing word "King":\n{uniq_answers_king}')

jeo_90s_computer = decade_proportion(jeopardy, 'question', ['Computer'], "199", separated=True)
jeo_00s_computer = decade_proportion(jeopardy, 'question', ['Computer'], "200", separated=True)
print(f'\nProportion of questions containing word "Computer" in 90s: {jeo_90s_computer}')
print(f'Proportion of questions containing word "Computer" in 00s: {jeo_00s_computer}')

print("\nProportion of categories in rounds:")
print(category_propotions(jeopardy, ['LITERATURE', 'SCIENCE']))

answer = None
print("\nQuiz yourself. Enter 'q' to exit")
while True:
  number = random.randrange(len(jeopardy))
  print(jeopardy.question[number])
  answer = input()
  if answer.lower() == "q":
    break
  elif answer.lower() == jeopardy.answer[number].lower():
    print("RIGHT!\n")
  else:
    print(f"WRONG! Right answer: {jeopardy.answer[number]}\n")
