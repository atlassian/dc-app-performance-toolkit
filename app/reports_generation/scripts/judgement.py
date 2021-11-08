import decimal
import os
from dataclasses import dataclass
from decimal import Decimal, getcontext
from statistics import median
import typing

import pandas
from prettytable import PrettyTable
from scipy.stats import mannwhitneyu

from util.data_preparation.dataframe_converter import files_to_dataframe, group_data_by_column
from reports_generation import constants
from reports_generation.scripts.utils import save_results

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
		        self.p_value, self.tolerance, self.baseline_size, self.tested_size]


class ActionTolerance(dict):

	def get_tolerance_range(self, action):
		tolerance = self.get(action)
		if not tolerance:
			return None
		return Decimal(tolerance)

	def set_tolerance_range(self, action, tolerance):
		setattr(self, action, tolerance)


class SampleObject:
	def __init__(self, values, cast_type='float64'):
		pandas.set_option("precision", 20)
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


def judgement_test_measuring(dataframe_baseline: pandas.DataFrame, dataframe_tested: pandas.DataFrame, measurement_by_column: str):
	judgement_results = []
	# TODO: get tolerance from config for every of actions
	tolerances = ActionTolerance(constants.DC_APPS_CONFLUENCE_TOLERANCE_RANGES)

	for group in dataframe_baseline.groups:
		tolerance = tolerances.get_tolerance_range(action=group)
		if not tolerance:
			print(f"Warning: no tolerance for action {group}")
			continue

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


def group_dataframe_by_action(filepath):
	raw_dataframe = files_to_dataframe(filepath)
	# Map timelines to each of action appropriately
	return group_data_by_column(raw_dataframe, columns=('label', ))


def judge_baseline_and_tested(baseline_result_dir, tested_result_dir):
	# jmeter actions test
	df_baseline = group_dataframe_by_action(os.path.join(baseline_result_dir, 'kpi.jtl'))
	df_tested = group_dataframe_by_action(os.path.join(tested_result_dir, 'kpi.jtl'))
	results = judgement_test_measuring(df_baseline, df_tested, measurement_by_column='elapsed')

	results_representation = [judgement_result.values() for judgement_result in results]
	judgement_table = PrettyTable(results[0].head())
	judgement_table.add_rows(results_representation)
	save_results([results[0].head()] + results_representation,
	             filepath=os.path.join(tested_result_dir, 'kpi_judged.csv'))

	# selenium actions test
	df_baseline = group_dataframe_by_action(os.path.join(baseline_result_dir, 'selenium.jtl'))
	df_tested = group_dataframe_by_action(os.path.join(tested_result_dir, 'selenium.jtl'))
	results = judgement_test_measuring(df_baseline, df_tested, measurement_by_column='elapsed')

	results_representation = [judgement_result.values() for judgement_result in results]
	judgement_table.add_rows(results_representation)
	save_results([results[0].head()] + results_representation,
	             filepath=os.path.join(tested_result_dir, 'selenium_judged.csv'))

	print("Results of judgement has been saved:")
	print(judgement_table)


def judge(baseline_dir, tested_dirs):
	for directory in tested_dirs:
		judge_baseline_and_tested(baseline_dir, directory)

	
def __get_judgement_kwargs(config):
	baseline_result_dir = next((run for run in config['runs']
	                            if run['runType'] == constants.DCAPTRunType.baseline))['fullPath']
	tested_result_dirs = [run['fullPath'] for run in config['runs']
	                      if run['runType'] == constants.DCAPTRunType.experiment]

	return {'baseline_dir': baseline_result_dir, 'tested_dirs': tested_result_dirs}
