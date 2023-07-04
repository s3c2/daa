"""
The purpose of this module is to test the hiearchy approach of DAA
Hiearchy: Package, File, Function, Line
"""
import os
import pandas as pd
from daa.algos import matching_alerts as ma, find_code_context as fcc
from daa.github import github_info


class DAA:
    def __init__(self, previous_package_path, current_package_path):
        self.previous_package_path = previous_package_path
        self.current_package_path = current_package_path
        self.previous_package_name = self.previous_package_path.split("/")[-2]
        self.current_package_name = self.current_package_path.split("/")[-2]
        self.cve = self.current_package_path.cve
        self.repo_owner = current_package_path.repo_owner
        self.repo_name = current_package_path.repo_name
        self.commit_sha = current_package_path.commit_sha
        self.previous_base_directory = f"./repos/{self.repo_owner}/{self.repo_name}/"

        # set working directories
        working_directory = os.getcwd()

        # Read outputs of SAST tool
        alerts_previous = pd.read_csv(previous_package_path, header=0, names=['name', 'description',
                                                                              'severity', 'message',
                                                                              'path', 'start_line',
                                                                              'start_column', 'end_line',
                                                                              'end_column'])

        alerts_current = pd.read_csv(current_package_path, header=0, names=['name', 'description',
                                                                            'severity', 'message',
                                                                            'path', 'start_line',
                                                                            'start_column', 'end_line',
                                                                            'end_column'])

        print("====================================================\n"
              "====================================================\n"
              "====================================================\n")
        print(f"Total Alerts in {self.repo_owner}/{self.repo_name}: {len(alerts_previous)}")

        # create filepath for CodeQL alerts
        alerts_previous["filename"] = alerts_previous.apply(
            lambda row: f"{self.previous_base_directory[:-1]}{row['path']}",
            axis=1)

        if len(alerts_current.index) > 0:
            alerts_current["filename"] = alerts_current.apply(
                lambda row: f"{self.previous_base_directory[:-1]}{row['path']}",
                axis=1)
        else:
            alerts_current["filename"] = ""

        # clean filenames
        alerts_previous["filename_clean"] = alerts_previous.apply(
            lambda row: row["filename"].split(self.previous_package_path)[-1],
            axis=1)

        if len(alerts_current.index) > 0:
            alerts_current["filename_clean"] = alerts_current.apply(
                lambda row: row["filename"].split(self.current_package_path)[-1],
                axis=1)
        else:
            alerts_current["filename_clean"] = ""

        # Find code context for each alert
        """PREVIOUS ALERT FILE CONTEXT"""
        # get overall file structures for the package
        github_info.git_checkout_parent(self.repo_owner, self.repo_name, df_row.commit_sha,
                                        clone_path=self.previous_base_directory)

        print("Finding Previous Complete Context")
        # alerts_previous_context = fcc.CompleteContext(self.previous_base_directory)

        alerts_previous["context"] = alerts_previous.apply(
            lambda row: fcc.FindCodeContext(row["filename"],
                                            row["line_number"]).context,
            axis=1)

        """Current ALERT FILE CONTEXT"""
        print("Finding Current File Context")
        # get overall file structures for the package
        github_info.git_checkout_target(self.repo_owner, self.repo_name, df_row.commit_sha,
                                        clone_path=self.previous_base_directory)
        if len(alerts_current.index) > 0:
            """FindCodeContext is Slow, will not work for emperical study"""
            print("Finding Current Complete Context")
            alerts_current_context = fcc.CompleteContext(self.previous_base_directory)

            alerts_current["context"] = alerts_current.apply(
                lambda row: fcc.FindCodeContext(row["filename"],
                                                row["line_number"]).context,
                axis=1)
        else:
            alerts_current["context"] = ""

        """Replace nan values in context with filename"""
        alerts_previous["context"] = alerts_previous.apply(
            lambda x: x["filename"].split("/")[-1] if pd.isna(x["context"]) else x["context"],
            axis=1)

        alerts_current["context"] = alerts_current.apply(
            lambda x: x["filename"].split("/")[-1] if pd.isna(x["context"]) else x["context"],
            axis=1)

        # find resolved alerts
        alerts_previous["resolved"] = alerts_previous.apply(
            lambda row: ma.MatchingAlertsCodeQLPython(row, alerts_current).resolved_alert,
            axis=1)

        """"CLEAN CodeQL INFO"""
        alerts_current["description"] = alerts_current.apply(
            lambda x: x["description"].replace('"', "").replace("'", ""),
            axis=1)
        alerts_previous["description"] = alerts_previous.apply(
            lambda x: x["description"].replace('"', "").replace("'", ""),
            axis=1)
        alerts_current["name"] = alerts_current.apply(
            lambda x: x["name"].replace('"', "").replace("'", ""),
            axis=1)
        alerts_previous["name"] = alerts_previous.apply(
            lambda x: x["name"].replace('"', "").replace("'", ""),
            axis=1)

        """=========================================================================================================="""
        """=========================================================================================================="""
        """=========================================================================================================="""
        """PACKAGE HIERARCHY"""
        hierarchy_package_columns = ['name', 'description', 'severity']

        """Create groupings for hierarchy_columns"""
        package_previous_group = alerts_previous.groupby(hierarchy_package_columns).size().reset_index(
            name='package_pc')
        package_current_group = alerts_current.groupby(hierarchy_package_columns).size().reset_index(
            name='package_cc')

        """Merge groups together"""
        diff_package = pd.merge(package_previous_group, package_current_group,
                                on=hierarchy_package_columns,
                                how="left")

        """Fill nan's with 0"""
        diff_package["package_pc"] = diff_package["package_pc"].fillna(0)
        diff_package["package_cc"] = diff_package["package_cc"].fillna(0)

        """Compare value counts"""
        diff_package["package_resolved"] = diff_package.apply(
            lambda x: True if int(x['package_cc']) < int(x['package_pc']) else False,
            axis=1)

        """=========================================================================================================="""
        """=========================================================================================================="""
        """=========================================================================================================="""
        """FILE HIERARCHY"""
        hierarchy_file_columns = ['name', 'description', 'severity', 'path']

        """Create groupings for hierarchy_columns"""
        file_previous_group = alerts_previous.groupby(hierarchy_file_columns).size().reset_index(
            name='file_pc')
        file_current_group = alerts_current.groupby(hierarchy_file_columns).size().reset_index(
            name='file_cc')

        """Merge groups together"""
        diff_file = pd.merge(file_previous_group, file_current_group,
                             on=hierarchy_file_columns,
                             how="left")

        """Fill nan's with 0"""
        diff_file["file_pc"] = diff_file["file_pc"].fillna(0)
        diff_file["file_cc"] = diff_file["file_cc"].fillna(0)

        """Compare value counts"""
        diff_file["file_resolved"] = diff_file.apply(
            lambda x: True if int(x['file_cc']) < int(x['file_pc']) else False,
            axis=1)
        """=========================================================================================================="""
        """=========================================================================================================="""
        """=========================================================================================================="""
        """FUNCTION HIERARCHY"""
        hierarchy_function_columns = ['name', 'description', 'severity', 'path', 'context']

        """Create groupings for hierarchy_columns"""
        function_previous_group = alerts_previous.groupby(hierarchy_function_columns).size().reset_index(
            name='function_pc')
        function_current_group = alerts_current.groupby(hierarchy_function_columns).size().reset_index(
            name='function_cc')

        """Merge groups together"""
        diff_function = pd.merge(function_previous_group, function_current_group,
                                 on=hierarchy_function_columns,
                                 how="left")

        """Fill nan's with 0"""
        diff_function["function_pc"] = diff_function["function_pc"].fillna(0)
        diff_function["function_cc"] = diff_function["function_cc"].fillna(0)

        """Compare value counts"""
        diff_function["function_resolved"] = diff_function.apply(
            lambda x: True if int(x['function_cc']) < int(x['function_pc']) else False,
            axis=1)

        """=========================================================================================================="""
        """=========================================================================================================="""
        """=========================================================================================================="""
        """LINE HIERARCHY"""
        hierarchy_line_columns = ['name', 'description', 'severity', 'path', 'context', 'start_line']

        """Create groupings for hierarchy_columns"""
        line_previous_group = alerts_previous.groupby(hierarchy_line_columns).size().reset_index(
            name='line_pc')
        line_current_group = alerts_current.groupby(hierarchy_line_columns).size().reset_index(
            name='line_cc')

        """Merge groups together"""
        diff_line = pd.merge(line_previous_group, line_current_group,
                             on=hierarchy_line_columns,
                             how="left")

        """Fill nan's with 0"""
        diff_line["line_pc"] = diff_line["line_pc"].fillna(0)
        diff_line["line_cc"] = diff_line["line_cc"].fillna(0)

        """Compare value counts"""
        diff_line["line_resolved"] = diff_line.apply(
            lambda x: True if int(x['line_cc']) < int(x['line_pc']) else False,
            axis=1)

        """=========================================================================================================="""
        """=========================================================================================================="""
        """=========================================================================================================="""
        """COMBINE HIERARCHY DF'S"""
        """Start with lowest granularity first and merge of the higher columns"""
        diff_combined = pd.merge(diff_line, diff_function,
                                 on=hierarchy_function_columns,
                                 how="left")

        diff_combined = diff_combined.merge(diff_file,
                                            on=hierarchy_file_columns,
                                            how="left")

        diff_combined = diff_combined.merge(diff_package,
                                            on=hierarchy_package_columns,
                                            how="left")

        """Fill NA values with False"""
        diff_combined = diff_combined.fillna(False)

        """Set alerts to return - Raw alerts"""
        # raw alerts from Bandit
        self.alerts_previous = alerts_previous
        self.alerts_current = alerts_current
        self.diff_combined = diff_combined

        """Set resolved alerts"""
        self.resolved_original = alerts_previous.query(f'resolved == True').reset_index(drop=True)
        self.resolved_package = diff_package[diff_package["package_resolved"] == True]
        self.resolved_file = diff_file[diff_file["file_resolved"] == True]
        self.resolved_function = diff_function[diff_function["function_resolved"] == True]
        self.resolved_line = diff_line[diff_line["line_resolved"] == True]

        """Count the levels DAA"""
        diff_combined["daa_resolved"] = diff_combined.apply(
            lambda x: True if (x["package_resolved"] == True
                               and x["file_resolved"] == True
                               and x["function_resolved"] == True
                               and x["line_resolved"] == True)
            else False,
            axis=1)

        self.daa_resolved = diff_combined[diff_combined["daa_resolved"] == True]