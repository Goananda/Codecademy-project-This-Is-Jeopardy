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
  decade_database = database[database.air_date.str[0:3] == date]
  return str(round(100*len(find_words(decade_database, column, word_list, sensitive, separated))/len(decade_database), 2))+"%"

def category_propotions(database, categories):
  j_round_counts = database.groupby('j_round')['show_number'].count().reset_index()
  j_round_counts_dict = {}
  for i in range(len(j_round_counts)):
    j_round_counts_dict[j_round_counts.j_round[i]] = j_round_counts.show_number[i]
  category_database = database[database.category.isin(categories)]
  count_database = category_database.groupby(['j_round', 'category'])['show_number'].count().reset_index()
  count_pivot = count_database.pivot(columns='category', index='j_round', values='show_number').reset_index()
  count_pivot['total'] = count_pivot.j_round.apply(lambda x: j_round_counts_dict[x])
  for category in categories:
    count_pivot[category] = count_pivot.apply(lambda row: str(round(100*row[category]/row.total, 2))+'%', axis=1)
  return count_pivot

jeopardy = pd.read_csv('jeopardy.csv')
jeopardy.columns = ['show_number', 'air_date', 'j_round', 'category', 'value', 'question', 'answer']
jeopardy['category'] = jeopardy.category.str.lower()
jeopardy['float_value'] = pd.to_numeric(jeopardy.value.apply(lambda x: re.sub("[\D]", "", x)\
                                                             if x != "None" else 0))

result_1 = find_words(jeopardy, 'question', ["King", "England"], separated=True)
result_2 = find_words(jeopardy, 'question', ["King"], separated=True)
print(f'Average value of questions containing word "King": ${round(result_2.float_value.mean(), 2)}')
print(f'\nUnique answers to questions containing word "King":\n{count_words(result_2, "answer")}')

jeopardy_90s_computer = decade_proportion(jeopardy, 'question', ['Computer'], "199", separated=True)
jeopardy_00s_computer = decade_proportion(jeopardy, 'question', ['Computer'], "200", separated=True)
print(f'\nProportion of questions containing word "Computer" in 90s: {jeopardy_90s_computer}')
print(f'Proportion of questions containing word "Computer" in 00s: {jeopardy_00s_computer}')

print("\nProportion of categories in rounds:")
print(category_propotions(jeopardy, ['literature', 'science']))

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
