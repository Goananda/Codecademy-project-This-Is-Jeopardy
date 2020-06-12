import pandas as pd
import re
import random
import os

pd.set_option("display.max_colwidth", None)
pd.set_option("display.max_columns", None)
pd.set_option("display.max_rows", None)

jeopardy = pd.read_csv("jeopardy.csv")
jeopardy.columns = ["show_number", "air_date", "jround", "category", "value", "question", "answer"]
jeopardy.fillna({"answer": "Null"}, inplace=True)
to_float = lambda x: float(re.sub("[\D]", "", x)) if x != "None" else 0
jeopardy["value"] = jeopardy.value.apply(to_float)

def jeopardy_analytics():
    print("Welcome to Jeopardy Analytics!")
    jeopardy_list = ["Set categories",
                     "Categories statistics",
                     "Find data by words in columns",
                     "Find unique answers for words in questions",
                     "Play Game",
                     "Quit"]
    while True:
        menu_list = list(jeopardy_list)
        if not categories:
            menu_list.remove("Categories statistics")
        title = "\n".join(categories) if categories else "All categories"
        choice = choose_menu(menu_list, title)
        if choice == "Set categories":
            set_categories()
        elif choice == "Categories statistics":
            categories_statistics()
        elif choice == "Find data by words in columns":
            find_data()
        elif choice == "Find unique answers for words in questions":
            find_unique_answers()
        elif choice == "Play Game":
            play_game()
        elif choice == "Quit":
            break

def set_categories():
    full_menu = ["Add category", "Remove category", "Remove all categories", "Return"]
    while True:
        menu_list = list(full_menu)
        if not categories:
            menu_list.remove("Remove category")
            menu_list.remove("Remove all categories")
        title = "\n".join(categories) if categories else "No categories"
        choice = choose_menu(menu_list, title)
        if choice == "Add category":
            word = input("Category: ")
            for category in jeopardy.category.unique():
                if word.lower() == category.lower():
                    categories.append(category)
                    break
            else:
                print("No such category")
        elif choice == "Remove category":
            categories.remove(choose_menu(categories, "Categories:"))
        elif choice == "Remove all categories":
            categories.clear()
        elif choice == "Return":
            break

def categories_statistics():
    print("\nCategory frequency in rounds:\n")
    frequency(jeopardy, "category", categories, "jround")
    for category in categories:
        print(f"\nCategory: {category}")
        avg_value(jeopardy[jeopardy.category == category])

def find_data():
    df = cat_filter()
    result = get_data_by_words(df)
    length = len(result)
    print(f"\n{length} questions are found")
    if length > 0:
        avg_value(result)
        compare_decade(df, result)
        data_to_csv(result)

def find_unique_answers():
    df = get_data_by_words(cat_filter(), only_questions=True)
    result = df["answer"].value_counts().reset_index()
    result.rename(columns={"index": "answer", "answer": "total"}, inplace=True)
    length = len(result)
    print(f"\n{length} unique answers are found")
    if length > 0:
        print("Most popular answers:")
        print(result[:10].to_string(index=False))
        data_to_csv(result)

def play_game():
    print('\nJeopardy Game\nEnter "q" to quit\n')
    df = cat_filter().reset_index()
    while True:
        number = random.randrange(len(df))
        print(df.question[number])
        answer = input()
        if answer.lower() == "q":
            break
        elif answer.lower() == df.answer[number].lower():
            print("RIGHT!\n")
        else:
            print(f"Right answer: {df.answer[number]}\n")

def cat_filter():
    df = jeopardy
    if categories:
        df = df[df.category.isin(categories)]
    return df

def frequency(df, index, index_list, columns):
    tab = pd.crosstab(index=df[index], columns=df[columns], margins=True, margins_name="Total",
                      normalize="columns").reset_index()
    tab = tab[tab[index].isin(index_list)]
    for column in [column for column in tab.columns if column != index]:
        tab[column] = tab[column].apply(lambda x: "{:.6f}".format(x))
    total = pd.crosstab(index="", columns=df[columns], margins=True, margins_name="Total").iloc[-1]
    total[index] = "Total"
    tab = tab.append(total)
    print(tab.to_string(index=False))

def avg_value(df):
    print(f"Average value of questions: ${'{:.2f}'.format(df.value.mean())}")

def get_data_by_words(df, only_questions=False):
    df = df.copy()
    if only_questions == False:
        df["question_answer"] = df["question"] + " " + df["answer"]
    col_dict = {"Question": "question", "Answer": "answer", "Question & Answer": "question_answer"}
    items = []
    title = []
    while True:
        if len(items) > 0:
            menu_list = ["Add word", "Find data"]
            choice = choose_menu(menu_list, "\n".join(title))
            if choice == "Find data":
                fil = lambda row: all(re.search(word, row[column]) for (word, column) in items)
                df = df[df.apply(fil, axis=1)]
                if "question_answer" in df.columns:
                    del df["question_answer"]
                return df
        word = input("Word: ")
        if word != "":
            word_title = f'"{word}"'
            choice = choose_menu(["Include", "Exclude"], "Substrings:")
            if choice == "Exclude":
                word = rf"\b{word}\b"
            word_title += f": {choice} substrings"
            choice = choose_menu(["Sensitive", "Insensitive"], "Case:")
            if choice == "Insensitive":
                word = f"(?i){word}"
            word_title += f", {choice} case"
            if only_questions:
                column = "question"
            else:
                choice = choose_menu(["Question", "Answer", "Question & Answer"], "Column:")
                column = col_dict[choice]
                word_title += f", {choice} column"
            title.append(word_title)
            items.append((word, column))

def compare_decade(df, result):
    decade = lambda base, date: base[base.air_date.str[2] == date]
    prop = lambda date: 100*(len(decade(result, date))/len(decade(df, date)))
    for dec in ["9", "0"]:
        if len(decade(df, dec)) > 0:
            print(f"Proportion of questions in {dec}0s: {'{:.4f}'.format(prop(dec))}%")
        else:
            print(f"No such categories in {dec}0s")

def data_to_csv(df):
    path = "jeo_data.csv"
    i = 0
    while os.path.isfile(path):
        i += 1
        path = f"jeo_data{i}.csv"
    choice = choose_menu(["NO", "YES"], f'Write data to "{path}?"')
    if choice == "YES":
        df.to_csv(path)

def choose_menu(lst, title):
    print(f"\n{title}")
    for item in enumerate(lst):
        print(f"{item[0]} - {item[1]}")
    while True:
        choice = input("Number of your choice: ")
        if choice in map(str, range(len(lst))):
            return lst[int(choice)]

categories = []
jeopardy_analytics()