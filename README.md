# Freetime

*Freetime* makes the difference between your working hours and your upcoming events to give your free time slots in the upcoming weeks.

## Configuration

The configuration file contains:

- `calendar_path`: the path of the directory where to look for `.ics` files containing the upcoming events; all the subdirectories are walked through.
- `time_slots`: the definition of the working hours: list of working intervals (day of the week, 0 for Monday and 4 for Friday, start time, end time). There can be several working intervals.
- `margin`: the time (in minutes) to save around each upcoming event. With a 15 minutes margin and an event starting at 9:30 and ending at 11, the interval 9:15-11:15 will be considered to be busy.

## Usage

Run `freetime.py -h` for help. The optional arguments are:

- `--nbweeks`, `-n`: number of weeks to look forward (default: 0).
- `--duration`, `-d`: minimal duration of the free time slots to return (default: 0).

## Possible developments

- Possibility to change language.
- Possibility to read *Freetime* output to exchange slots with other users.
- Possibility to propose slots for people working in another time zone.
- Possibility to distinguish between live or remote availabilities, for people who work remotely on the same day every week.