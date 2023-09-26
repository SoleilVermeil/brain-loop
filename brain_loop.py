import datetime
import math
import pandas as pd
import argparse
import glob
import os
import re
from tqdm import tqdm


class Schedule:

    def __init__(self, name: str):
        self.lessons = []
        self.name = name

    def add_lessons(self: list[dict], name: str, date_start: datetime.date, date_end: datetime.date, weekdays: list[str]):
        for i in range((date_end - date_start).days):
            date = date_start + datetime.timedelta(days=i)
            weekday_index = date.weekday()
            if ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"][weekday_index] in weekdays:
                self.lessons.append({
                    "name": f"{name} ({date.strftime('%d %b')})",
                    "last_date": date,
                    "level": 0.0,
                })

    def get_next_training_date(self, last_date: datetime.date, level: float) -> datetime.date:
        def fibonacci(x: float) -> float:
            phi = (1 + math.sqrt(5)) / 2
            y = 10 * x + 2
            return (phi**y - math.cos(math.pi * y) * phi**(-y)) / math.sqrt(5)
        delta_day = round(fibonacci(level))
        return last_date + datetime.timedelta(days=delta_day)

    def get_specific_day_lessons(self, date: datetime.date) -> list[dict]:
        lessons = []
        for delta_level in range(0, 10):
            lessons += [lesson for lesson in self.lessons if self.get_next_training_date(lesson["last_date"], lesson["level"] + 0.1 * delta_level) == date]
        return lessons

    def get_todays_lessons(self) -> list[dict]:
        lessons = [lesson for lesson in self.lessons if self.get_next_training_date(lesson["last_date"], lesson["level"]) <= datetime.date.today()]
        return lessons

    def study(self) -> None:
        lessons = self.get_todays_lessons()
        if len(lessons) == 0:
            print("No lessons to study today.")
            return
        for i, lesson in enumerate(lessons):
            print(f"Lesson {(i + 1)}/{len(lessons)}.")
            print(f"Now studying {lesson['name']}.")
            number_of_days_late = (datetime.date.today() - self.get_next_training_date(lesson["last_date"], lesson["level"])).days
            if number_of_days_late > 0:
                print(f"NOTE: You are {number_of_days_late} days late. Therefore a penalty will be applied to your today's progression.")
            output = input(f"Do you understand well today's topic (y/n)? ")
            if output == "y":
                progression = 0.1 - 0.01 * number_of_days_late
            elif output == "n":
                progression -= 0.1
            old_level = lesson["level"]
            new_level = min(1.0, max(0.0, lesson["level"] + progression))
            print(f"Your level progressed from {old_level:.0%} to {new_level:.0%}.")
            lesson["level"] = new_level
            lesson["last_date"] = datetime.date.today()
            print(f"You will next be tested on {self.get_next_training_date(lesson['last_date'], lesson['level']).strftime('%d %b')}.")
            print("-" * 80)
        print("You have finished studying for today!")

    def save_lessons(self) -> None:
        df = pd.DataFrame(self.lessons)
        if not os.path.exists(f"./schedules/{self.name}"):
            os.makedirs(f"./schedules/{self.name}")
            filename = f"./schedules/{self.name}/root.csv"
        else:
            filename = f"./schedules/{self.name}/{datetime.datetime.today().strftime('%Y-%m-%d')}.csv"
        df.to_csv(filename, index=False, sep=";", encoding="utf-8")

    def load_lessons(self) -> None:
        filenames = glob.glob(f"./schedules/{self.name}/*.csv")
        filenames.sort()
        if len(filenames) == 0:
            raise Exception(f"Schedule '{self.name}' do not exist.")
        elif len(filenames) == 1:
            filename = filenames[0]
        else:
            filename = filenames[-2]
        df = pd.read_csv(filename, sep=";", encoding="utf-8")
        df['last_date'] = pd.to_datetime(df['last_date']).dt.date
        self.lessons = df.to_dict("records")

    def edit_lesson(self, lesson_name: str, new_date: datetime.date):
        filenames = glob.glob(f"./schedules/{self.name}/*.csv")
        for filename in filenames:
            df = pd.read_csv(filename, sep=";", encoding="utf-8")
            df['last_date'] = pd.to_datetime(df['last_date']).dt.date
            lessons = df.to_dict("records")
            for i in range(len(lessons)):
                if lessons[i]["name"] == lesson_name:
                    lessons[i]["name"] = f"{extract_name(lesson['name'])} ({new_date.strftime('%d %b')})"
                    lessons[i]["last_date"] = new_date
            df = pd.DataFrame(lessons)
            df.to_csv(filename, index=False, sep=";", encoding="utf-8")
        self.load_lessons() # Reload lessons from the last file to ensure stability


def extract_date(s: str) -> datetime.date:
    pattern = r"\((\d{1,2}\s[A-Z]?[a-z]*)\)"
    match = re.search(pattern, s)
    if match:
        return datetime.datetime.strptime(match.group(1) + " " + str(datetime.date.today().year), "%d %b %Y").date()
    else:
        raise Exception(f"ERROR: Could not extract date from '{s}'.")

def extract_name(s: str) -> str:
    pattern = r"(.*) \((?:\d{1,2}\s[A-Z]?[a-z]*)\)"
    match = re.search(pattern, s)
    if match:
        return match.group(1)
    else:
        raise Exception(f"ERROR: Could not extract name from '{s}'.")

def add_lesson() -> None:
    add_another = "y"
    while add_another == "y":
        name = input("Please enter the name of the lesson to add (for example: Physics): ")
        valid = False
        while not valid:
            date_start = input("Please enter the date of the first time you'll have this lesson to add (YYYY-MM-DD): ")
            try:
                datetime.datetime.strptime(date_start, "%Y-%m-%d")
                valid = True
            except ValueError:
                print("ERROR: Incorrect date format.")
        valid = False
        while not valid:
            date_end = input("Please enter the end date of the last time you'll have this lesson to add (YYYY-MM-DD): ")
            try:
                datetime.datetime.strptime(date_end, "%Y-%m-%d")
                valid = True
            except ValueError:
                print("ERROR: Incorrect date format.")
        valid = False
        while not valid:
            weekdays = input("Please enter the weekday(s) you'll have this lesson to add (for example: monday friday): ")
            for weekday in weekdays.split(" "):
                if weekday not in ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]:
                    print(f"ERROR: {weekday} is not a valid weekday. Valid weekdays are: monday, tuesday, wednesday, thursday, friday, saturday, sunday.")
                    break
            else:
                valid = True
        s.add_lessons(
            name=name,
            date_start=datetime.datetime.strptime(date_start, "%Y-%m-%d").date(),
            date_end=datetime.datetime.strptime(date_end, "%Y-%m-%d").date(),
            weekdays=weekdays.split(" ")
        )
        add_another = input(f"There are currently {len(s.lessons)} lessons. Do you want to add another lesson (y/n)? ")


parser = argparse.ArgumentParser(description='A spaced repetition tool for optimal learning and memory retention.')
group = parser.add_mutually_exclusive_group()
group.add_argument('--create', type=str, help='create a new schedule', metavar='NAME')
group.add_argument('--study', type=str, help='study from an existing schedule', metavar='NAME')
group.add_argument('--list', action='store_true', help='list all schedules')
group.add_argument('--edit', type=str, help='edit an existing schedule', metavar='NAME')
args = parser.parse_args()

if args.create:
    s = Schedule(args.create)
    add_lesson()
    s.save_lessons()

if args.study:
    s = Schedule(args.study)
    s.load_lessons()
    s.study()
    s.save_lessons()

if args.edit:
    s = Schedule(args.edit)
    s.load_lessons()
    name = input("Please enter the name of the lesson to edit (for example: Physics): ")
    today_lessons_to_edit = [lesson for lesson in s.lessons if name.lower() in lesson["name"].lower() and extract_date(lesson["name"]) == datetime.date.today()]
    future_lessons_to_edit = [lesson for lesson in s.lessons if name.lower() in lesson["name"].lower() and extract_date(lesson["name"]) > datetime.date.today()]
    if len(today_lessons_to_edit) == 0 and len(future_lessons_to_edit) == 0:
        print(f"ERROR: Could not find any lesson with name containing '{name}'.")
        exit(1)
    lessons_to_edit = future_lessons_to_edit
    if len(today_lessons_to_edit) > 0:
        print("NOTE: Some of the lessons to edit are today's lessons:")
        for lesson in today_lessons_to_edit:
            print(f"* {lesson['name']}")
        shift_today_lessons_too = input(f"Edit them too (y/n)? ")
        if shift_today_lessons_too == "y":
            for i, lesson in enumerate(today_lessons_to_edit):
                lessons_to_edit.insert(i, lesson)
    print("The following lessons have been selected:")
    for lesson in lessons_to_edit:
        print(f"* {lesson['name']}")
    delta_days = input(f"Please enter the number of days to shift them (<0 to shift them to the past): ")
    if not((delta_days.isdigit()) or (delta_days[0] == "-" and delta_days[1:].isdigit())):
        print(f"ERROR: {delta_days} is not a valid number.")
        exit(1)
    print("The following modifications will be applied:")
    for lesson in lessons_to_edit:
        print(f"* {lesson['name']} -> {extract_name(lesson['name'])} ({(extract_date(lesson['name']) + datetime.timedelta(days=int(delta_days))).strftime('%d %b')})")
    confirm = input("Do you confirm (y/n)? ")
    if confirm == "y":
        for lesson in tqdm(lessons_to_edit):
            s.edit_lesson(lesson["name"], extract_date(lesson["name"]) + datetime.timedelta(days=int(delta_days)))


if args.list:
    print("List of schedules:")
    for foldername in glob.glob("./schedules/*"):
        name = os.path.basename(foldername)
        s = Schedule(name)
        s.load_lessons()
        print(f"* {name}")
        for delta_days in range(0, 7):
            weekday = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"][(datetime.date.today() + datetime.timedelta(days=delta_days)).weekday()]
            if delta_days == 0:
                weekday = "today"
                lessons_pending = s.get_todays_lessons()
            else:
                lessons_pending = s.get_specific_day_lessons(datetime.date.today() + datetime.timedelta(days=delta_days))
            print(f"  * {weekday:<10}: {len(lessons_pending):>2} lessons to study")