# Brain Loop

Brain Loop is a spaced repetition tool designed to help you optimize your learning process by intelligently scheduling and managing your study sessions. Whether you're learning a new language, studying for exams, or simply trying to retain information efficiently, Brain Loop can assist you in the journey towards mastery.

## What is Spaced Repetition?

Spaced repetition is a proven technique for enhancing memory and long-term retention of information. It involves reviewing and revising material at increasing intervals over time. Brain Loop automates this process, ensuring that you revisit and reinforce what you've learned at the most optimal times.

## How to use?

1. Install the required packages:
   ```
   pip install -r requirements.txt
   ```
2. Create a schedule:
   ```
   python brain_loop.py --create [schedule name]
   ```
3. Start studying:
   ```
   python brain_loop.py --study [schedule name]
   ```

For more informations, you can use `python brain_loop.py --help` to see all available commands. Note that all the schedules are stored inside the `./schedules` folder. Each study day a new file is created with the current progression. This will in the future allow to track the progress over time.
