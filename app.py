import functools
import re
from typing import Callable
import pandas as pd


DATA_PATH = './calories.txt'
DATE_FORMAT = r'%Y%m%d'
DATE_FORMAT_OUT = r'%Y/%m/%d'
DAY_PATTERN = r'^\d{8}$'
MEAL_DELIMITER = r'^\.$'
ITEM_DELIMITER = r'\n'
FLAGS = re.MULTILINE | re.DOTALL
SPREADSHEET_COLUMNS = ['food', 'date', 'meal']
SUBSTITUTIONS = {
    r'\bbs\b': 'brown sugar',
    r'\bmed\b': 'medium',
    r'\bpop\b': 'popcorn',
    r'\bl\b': 'large',
    r'\b[^\']s\b': 'small',
    r'\bgf\b': 'gluten free',
    'g banana': 'g banana peeled',
}

format_functions = ['trim', 'lowercase', 'empty']


def format(f: Callable) -> Callable:
    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        data, *a = args
        data = f(data, *a, **kwargs)
        data = empty(data)
        data = trim(data)
        data = list(map(lambda x: substitute(x), data))
        return data
    return wrapper


def empty(data: list) -> list:
    return list(filter(lambda x: x != '', data))


def trim(data: list[str]) -> list[str]:
    return list(map(lambda text: text.strip(), data))


def lowercase(text: str) -> str:
    return text.lower()


def substitute(text: str) -> str:
    for key, value in SUBSTITUTIONS.items():
        text = re.sub(key, value, text)
    return text


def extract_dates(text: str) -> list:
    return re.findall(DAY_PATTERN, text, flags=FLAGS)


@format
def split(text: str, delim: str) -> list:
    return re.split(delim, text, flags=FLAGS)


def split_days(data: list[str], dates: list[str]) -> dict[str, list[str]]:
    d = {}
    for day, date in zip(data, dates):
        d[date] = {}
        meals = split(day, MEAL_DELIMITER)
        for ix, meal in enumerate(meals):
            d[date][ix+1] = split(meal, ITEM_DELIMITER)
    return d


def to_table(data: dict) -> list[list]:
    table = []
    for date, meals in data.items():
        for meal, items in meals.items():
            for item in items:
                table.append([item, date, meal])
    return table


def read_file(filename: str) -> str:
    with open(filename, 'r', encoding='utf-8') as f:
        contents = f.read()
    return contents


def to_df(data: list[list]) -> pd.DataFrame:
    df = pd.DataFrame(data, columns=SPREADSHEET_COLUMNS)
    df['date'] = pd.to_datetime(df['date'], format=DATE_FORMAT)
    return df


def out_csv(data: pd.DataFrame, filename: str = 'out.csv') -> None:
    data.to_csv(filename, index=False, date_format=DATE_FORMAT_OUT)


def main() -> None:
    data = read_file(DATA_PATH)
    data = lowercase(data)
    dates = extract_dates(data)
    days = split(data, DAY_PATTERN)
    data = split_days(days, dates)
    table = to_table(data)
    df = to_df(table)
    out_csv(df, 'calories.csv')
    df.to_clipboard(index=False, header=False)
    print('Copied to clipboard and ready to paste into Excel.')


if __name__ == '__main__':
    main()