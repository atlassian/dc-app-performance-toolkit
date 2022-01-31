import typing
from decimal import Decimal, getcontext
import glob
import json
import os

import pandas
import pandas as pd

JSON_FILE_FORMATS = ('json', 'jpt',)
CSV_FILE_FORMATS = ('csv',)


def cast_to_decimal(value):
    getcontext().prec = 20
    return Decimal(value)


def jpt_to_python(input_file) -> list:
    data = []
    with open(input_file) as f:
        for line in f:
            row = json.loads(line.strip())
            # time format in jpt files is PT1.543S
            if 'duration' in row:
                row['duration'] = float(row['duration'].strip('PTS')) * 1000
            if 'duration_millis' in row:
                row['duration'] = float(row['duration_millis'])

            data.append(row)
    return data


def file_to_dataframe(input_file):
    # TODO: think about iterative reading when have huge data
    fileformat = os.path.splitext(input_file)[-1].strip('.')

    if fileformat in ('csv', 'jtl'):
        dataframe = pandas.read_csv(input_file)
    elif fileformat == 'json':
        dataframe = pandas.read_json(input_file)
    elif fileformat == 'jpt':
        data = jpt_to_python(input_file)
        dataframe = pandas.DataFrame(data)
    else:
        raise NotImplementedError(
            f"File format {fileformat} is not supported yet")

    return dataframe


def files_to_dataframe(path, fields: typing.Optional[list] = None):
    # TODO: think about iterative reading when have huge data
    files = glob.glob(path)
    if not files:
        raise FileNotFoundError(f"Files at path {path} are not found")
    dataframes = []
    for filename in files:
        dataframe = file_to_dataframe(filename)
        if fields is not None:
            dataframe = dataframe[list(fields)]

        dataframes.append(dataframe)

    return pd.concat(dataframes)


def concatenate_dataframes_from_multiple_paths(paths: list, fields: typing.Optional[list] = None):
    dataframes = []
    for path in paths:
        dataframes.append(files_to_dataframe(path, fields))
    return pd.concat(dataframes)


def group_data_by_column(dataframe, columns=('label',)):
    """
      Transform any dataframe to dataframe with groupped data by given fields
      :param dataframe: pandas dataframe
      :param columns: fields to group by
      :return:
    """
    return dataframe.groupby(list(columns))
