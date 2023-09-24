import datetime
import math
import pandas as pd
import argparse
import glob
import os


class Schedule:

    def __init__(self):
        self.lessons = []

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
            new_level = min(1.0, max(0.0,  + progression))
            print(f"Your level progressed from {old_level:.0%} to {new_level:.0%}.")
            lesson["level"] = new_level
            lesson["last_date"] = datetime.date.today()
            print(f"You will next be tested on {self.get_next_training_date(lesson['last_date'], lesson['level']).strftime('%d %b')}.")
            print("-" * 80)
        print("You have finished studying for today!")

    def save_lessons(self, name: str) -> None:
        df = pd.DataFrame(self.lessons)
        df.to_csv(f"./schedules/{name}.csv", index=False, sep=";", encoding="utf-8")

    def load_lessons(self, name: str) -> None:
        df = pd.read_csv(f"./schedules/{name}.csv", sep=";", encoding="utf-8")
        df['last_date'] = pd.to_datetime(df['last_date']).dt.date
        self.lessons = df.to_dict("records")

def add_lesson() -> None:
    add_another = "y"
    while add_another == "y":
        name = input("Please enter the name of the lesson to add (for example: Physics): ")
        date_start = input("Please enter the date of the first time you'll have this lesson to add (YYYY-MM-DD): ")
        date_end = input("Please enter the end date of the last time you'll have this lesson to add (YYYY-MM-DD): ")
        weekdays = input("Please enter the weekday(s) you'll have this lesson to add (for example: monday friday): ")
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
args = parser.parse_args()

if args.create:
    s = Schedule()
    add_lesson()
    s.save_lessons(args.create)

if args.study:
    s = Schedule()
    s.load_lessons(args.study)
    s.study()
    s.save_lessons(args.study)

if args.list:
    print("List of schedules:")
    for filename in glob.glob("./schedules/*.csv"):
        name = os.path.basename(filename).split(".")[0]
        s = Schedule()
        s.load_lessons(name)
        lessons_pending = s.get_todays_lessons()
        if len(lessons_pending) > 0:
            print(f"* '{name}' ({len(lessons_pending)} lessons pending)")
        else:
            print(f"* '{name}' (up to date)")
