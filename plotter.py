import glob
import matplotlib.pyplot as plt
import pandas as pd
import datetime
import os
import numpy as np

schedule = "ph_ma3"
line_formats = ["-", "--", "-."]
colors = plt.cm.turbo(np.linspace(0.0, 0.9, 5)) # ["gold", "chartreuse", "navy", "crimson"]
markers = ["o", "s", "d", "x", "+"]

def map_range(x, x1, x2, y1, y2):
    return (x - x1) * (y2 - y1) / (x2 - x1) + y1

# Get all files in the directory
files = glob.glob("./schedules/" + schedule + "/*.csv")
df = None
for file in files:
    df_ = pd.read_csv(file, sep=";", encoding="utf-8")
    try:
        date = datetime.datetime.strptime(os.path.basename(file).split(".")[0], "%Y-%m-%d").date()
    except ValueError:
        continue
    df_["date"] = date
    if df is None:
        df = df_.copy()
    else:
        df = pd.concat([df, df_])

# print(df.head(3).to_markdown(tablefmt="row"))
lessons = df["name"].unique()
for i, lesson in enumerate(lessons):
    df_ = df.query("name == @lesson").sort_values("date")
    progression = df_["level"].values
    dates = df_["date"].values
    delta_progression = np.array([0] + list(np.diff(progression)))
    first_nonzero_index = np.where(delta_progression != 0)[0]
    delta_progression[first_nonzero_index - 1] = 1
    progression = progression[delta_progression != 0]
    dates = dates[delta_progression != 0]
    if progression.sum() == 0:
        continue
    plt.plot(
        dates,
        progression,
        label=lesson,
        linestyle=line_formats[i % len(line_formats)],
        color=colors[i % len(colors)],
        linewidth=map_range(i, 0, len(lessons), 3, 1),
        marker=markers[i % len(markers)],
        markersize=map_range(i, 0, len(lessons), 10, 5),
    )
plt.legend()
plt.xlabel("Date")
plt.ylabel("Progression")
plt.xticks(rotation=90)
plt.show()