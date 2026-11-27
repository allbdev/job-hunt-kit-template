# Your job search settings. The scanner in scan/ reads this file.
#
# Filled in during setup, from the interview in SETUP.md, based on the role
# you want and where you can legally work from. Nothing here is role-specific
# by default: this file matches nothing until you (or Claude, during setup)
# fill it in.
#
# Regexes are plain strings. The scanner compiles them case-insensitive.
# Test a change with:  python3 scan/rejudge.py --dry

# Your name, as the report and the notification show it.
NAME = ""

# Your time zone (IANA name, e.g. "Europe/Lisbon", "America/Sao_Paulo").
# Sets "today" for harvest files and the report.
TIMEZONE = ""

# Local port for the report server (scan/serve.py).
PORT = 8777

# Short name of the job you want. Used in labels: "not a ROLE_NOUN".
ROLE_NOUN = ""

# Short name of the level you want. Used in labels.
TARGET_LABEL = ""

# Short name of where you can work from. Used in labels and filter buttons.
HOME_LABEL = ""

# The gate. A title that matches none of these is not your kind of job.
# It is still shown, in its own list, never dropped. Keep this broad: every
# word that could plausibly describe your kind of role.
ROLE_GATE = r""

# The right job at the right level. A title that passes ROLE_GATE but not
# this one goes to "One level down".
TARGET_TITLE = r""

# Optional: a different target level per kind of role, e.g. Senior for
# frontend but Mid for backend. Leave TRACKS empty and TARGET_TITLE alone
# decides the level. When set, TRACKS decides it instead.
#   LEVELS: name -> regex, checked in order; no match means level "none".
#   TRACKS: checked in order, first title match wins. "body" words decide a
#     generic title ("Software Engineer") when one track clearly leads.
#     "levels" maps each level to ok (Clean), glance (Worth a glance) or
#     down (One level down).
#   GENERIC_LEVELS: the same map, for a generic title whose ad is unclear.
# Example:
#   LEVELS = {"lower": r"\bjunior\b", "senior": r"\bsenior\b", "mid": r"\bmid\b"}
#   TRACKS = [{"name": "frontend", "title": r"front[- ]?end", "body": r"\breact\b|\bcss\b",
#              "levels": {"senior": "ok", "none": "ok", "mid": "down"}}]
LEVELS = {}
TRACKS = []
GENERIC_LEVELS = {}

# Titles that match the gate words but are the wrong kind of work: adjacent
# roles that share your keywords but are not your job.
EXCLUDE_TITLES = r""

# Right kind of work, a level lower than you want. Role-agnostic default.
LOWER_LEVEL = r"\bjunior\b|\bjr\.?\b|mid[- ]level|intermediate|graduate|trainee"

# Places you can work from. A posting must name one of these, or say
# "remote" with no country, or say "anywhere / worldwide".
HOME_PLACES = r""

# A remote role limited to a country you cannot work from ("Remote (United
# States)", "Anywhere in France"). False: Worth a glance, since some of these
# hire contractors elsewhere anyway. True: Wrong country.
SCOPED_REMOTE_IS_WRONG_COUNTRY = False

# ISO country codes the boards may return, that you can work in.
HOME_COUNTRY_CODES = []

# False skips the Google step in the daily run. It needs Claude in Chrome
# (see scan/README.md). Turn it on only once a test run works.
GOOGLE_ENABLED = True

# Google queries the daily agent runs. Each one is combined with the
# site: filter for Lever, Greenhouse and Ashby (see scan/harvest-google.js).
GOOGLE_QUERIES = []
