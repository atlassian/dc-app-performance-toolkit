import decimal
import os
from dataclasses import dataclass
from decimal import Decimal, getcontext
from statistics import median
import typing

import pandas
from prettytable import PrettyTable
from scipy.stats import mannwhitneyu

import constants
from scripts.dataframe_converter import (concatenate_dataframes_from_multiple_paths,
                                         group_data_by_column)
from scripts.utils import save_results
from tolerances import get_tolerances, ActionTolerance


getcontext().prec = 20


@dataclass
class JudgementResult:
    action: str
    passed: bool
    baseline_size: int
    tested_size: int
    tolerance: float
    p_value: typing.Optional[float]
    failure_reason: str = None

    def head(self):
        return ["Action", "Judgement passed",
                "Failure reason", "p_value", "Tolerance",
                "Baseline size", "Tested size"]

    def values(self):
        return [self.action, self.passed, self.failure_reason,
                self.p_value, self.tolerance, self.baseline_size,
                self.tested_size]


class SampleObject:
    def __init__(self, values, cast_type='float64'):
        pandas.set_option("display.precision", 20)
        self.values = values.astype(cast_type)

    def shift(self, shift_value):
        self.values = self.values.add(
            pandas.to_numeric(shift_value, downcast='float'))

    def median(self):
        return median(self.values)


def mannwhitney_test(base_sample, tested_sample, tolerance=Decimal(0.03)):
    baseline_sample = SampleObject(base_sample)
    # First we shift tested sample a little bit back likely closer to baseline.
    # This will be acceptance ratio: if tested one is slower at less or equal than 3% - we do accept this
    mu = - tolerance * Decimal(base_sample.median())

    tested_shifted_sample = SampleObject(tested_sample)
    tested_shifted_sample.shift(mu)

    # TODO: 2/ check the hypothesis in comments of question
    # TODO: https://stats.stackexchange.com/questions/439611/am-i-doing-it-right-conducting-mann-whitney-test-in-scipy
    # TODO: play with mannwhitney, or wilcoxon signed rank test

    u_statistic_less, pvalue_sided_less = mannwhitneyu(
        baseline_sample.values,
        tested_shifted_sample.values,
        alternative='less', use_continuity=False)

    mw_alpha = Decimal(0.05)  # critical value for mann whitney test (significance level)

    # NOTE: if p_value less than critical value,
    # then algorithm can reject hypothesis 'tested result is slower than baseline'
    # in opposite, if p_value is more or equal, there is not enough evidence to reject tested sample
    hypothesis_rejected = pvalue_sided_less < mw_alpha
    test_passed = not hypothesis_rejected
    return test_passed, pvalue_sided_less


def judgement_test_measuring(dataframe_baseline: pandas.DataFrame, dataframe_tested: pandas.DataFrame,
                             measurement_by_column: str, tolerances: ActionTolerance):
    judgement_results = []

    for group in dataframe_baseline.groups:
        tolerance = tolerances.get_tolerance_range(action=group)
        if tolerance is None:
            continue
        tolerance = Decimal(tolerance)

        sample_base = dataframe_baseline.get_group(group)[measurement_by_column]
        sample_tested = dataframe_tested.get_group(group)[measurement_by_column]
        try:
            test_passed, p_value = mannwhitney_test(sample_base, sample_tested, tolerance)
            # TODO: later we may define many failure reasons
            failure_reason = 'Results deviation is not accepted' if not test_passed else None
            judgement_results.append(
                JudgementResult(action=group, passed=test_passed, failure_reason=failure_reason, p_value=p_value,
                                baseline_size=len(sample_base), tested_size=len(sample_tested),
                                tolerance=float(round(tolerance, 2)))
            )
        except decimal.InvalidOperation as e:
            judgement_results.append(JudgementResult(
                action=group, passed=False, baseline_size=len(sample_base), tested_size=len(sample_tested),
                failure_reason=f'Failed to evaluate results by Mann Whitney: Error: {e}.'
                               f'Check results for this group.',
                p_value=None, tolerance=float(tolerances.get_tolerance_range(action=group)))
            )
            print(f" No tolerance found for action {group}. Action timelines is {sample_base.values}")

    return judgement_results


def group_dataframe_by_action(filepaths: list, fields=None):
    raw_dataframe = concatenate_dataframes_from_multiple_paths(filepaths, fields=fields)
    # Map timelines to each of action appropriately
    return group_data_by_column(raw_dataframe, columns=('label',))


def judge_baseline_and_tested(baseline_result_dir: str, tested_result_dir: str):
    action_tolerances = get_tolerances(tested_result_dir)

    # jmeter actions test
    # df_jmeter_baseline = group_dataframe_by_action(os.path.join(baseline_result_dir, 'kpi*.jtl'))
    # df_selenium_baseline = group_dataframe_by_action(os.path.join(baseline_result_dir, 'selenium*.jtl'))
    fields = ('label', 'elapsed', )
    # gather all needed dataframes with specific fields
    df_baseline = group_dataframe_by_action([os.path.join(baseline_result_dir, 'kpi*.jtl'),
                                             os.path.join(baseline_result_dir, 'selenium*.jtl')], fields)
    df_tested = group_dataframe_by_action([os.path.join(baseline_result_dir, 'kpi*.jtl'),
                                           os.path.join(baseline_result_dir, 'selenium*.jtl')], fields)
    results = judgement_test_measuring(df_baseline, df_tested,
                                       measurement_by_column='elapsed',
                                       tolerances=action_tolerances)

    results_representation = [judgement_result.values() for judgement_result in results]
    judgement_table = PrettyTable(results[0].head())
    judgement_table.add_rows(results_representation)
    print("Results of judgement")
    print(judgement_table)
    return [results[0].head()] + results_representation


def judge(baseline_dir, tested_dirs, output_dir):
    for directory in tested_dirs:
        results = judge_baseline_and_tested(baseline_dir, directory)
        judgement_filename = os.path.join(
            output_dir,
            f'judged_baseline_{os.path.basename(baseline_dir)}_experiment_{os.path.basename(directory)}.csv')
        save_results(results,
                     filepath=os.path.join(output_dir, judgement_filename))


def __get_judgement_kwargs(config):
    baseline_result_dir = next((run for run in config['runs']
                               if run['runType'] == constants.DCAPTRunType.baseline))['fullPath']
    tested_result_dirs = [run['fullPath'] for run in config['runs']
                          if run['runType'] == constants.DCAPTRunType.experiment]

    return {
        'baseline_dir': baseline_result_dir,
        'tested_dirs': tested_result_dirs}
