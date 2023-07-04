class MatchingAlerts:
    def __init__(self, previous_alert, current_alerts):
        self.alert_filename_clean = previous_alert.filename_clean
        self.alert_test_name = previous_alert.test_name
        self.alert_test_id = previous_alert.test_id
        self.alert_issue_severity = previous_alert.issue_severity
        self.alert_issue_confidence = previous_alert.issue_confidence
        self.alert_issue_text = previous_alert.issue_text
        self.alert_context = previous_alert.context
        self.current_alerts = current_alerts

        self.resolved_alert = self.find_matching_alerts()

    def find_matching_alerts(self):
        matched_alert = self.current_alerts.query(f'filename_clean == "{self.alert_filename_clean}" and '
                                                  f'test_name == "{self.alert_test_name}" and '
                                                  f'test_id == "{self.alert_test_id}" and '
                                                  f'issue_severity == "{self.alert_issue_severity}" and '
                                                  f'issue_confidence == "{self.alert_issue_confidence}" and '
                                                  f'issue_text == "{self.alert_issue_text}" and '
                                                  f'context == "{self.alert_context}"')

        if len(matched_alert) > 0:
            return False
        else:
            return True


class MatchingAlertsCodeQLPython:
    """
    Set resolved alerts for CodeQL data
    Should work for both Python and Java since data structures are the same
    """
    def __init__(self, previous_alert, current_alerts):
        self.alert_filename_clean = previous_alert.filename_clean
        self.alert_name = previous_alert["name"]
        self.alert_description = previous_alert.description
        self.alert_severity = previous_alert.severity
        self.alert_message = previous_alert.message
        self.alert_context = previous_alert.context
        self.current_alerts = current_alerts
        self.start_line = previous_alert.start_line

        try:
            self.resolved_alert = self.find_matching_alerts()
        except:
            print("error")
            self.resolved_alert = self.find_matching_alerts()

    def find_matching_alerts(self):
        """Do a little text cleaning before the query"""
        self.current_alerts["description"] = self.current_alerts.apply(lambda x: x["description"].replace('"', "").replace("'", ""),
                                                                       axis=1)
        self.current_alerts["description"] = self.current_alerts.apply(
            lambda x: x["description"].replace('"', "").replace("'", ""),
            axis=1)
        self.current_alerts["name"] = self.current_alerts.apply(
            lambda x: x["name"].replace('"', "").replace("'", ""),
            axis=1)

        self.alert_description = self.alert_description.replace('"', "").replace("'", "")
        self.alert_name = self.alert_name.replace('"', "").replace("'", "")

        # semantic test

        matched_alert = self.current_alerts.query(f'filename_clean == "{self.alert_filename_clean}" and '
                                                 f'name == "{self.alert_name}" and '
                                                 f'description == "{self.alert_description}" and '
                                                 f'severity == "{self.alert_severity}" and '
                                                 f'context == "{self.alert_context}"')

        test = self.current_alerts[self.current_alerts["context"] == "script_upload"]
        if len(matched_alert) > 0:
            return False
        else:
            return True


class MatchingAlertsCodeQL:
    """
    Set resolved alerts for CodeQL data
    Should work for both Python and Java since data structures are the same
    """
    def __init__(self, previous_alert, current_alerts):
        self.alert_filename_clean = previous_alert.source_filepath
        self.alert_name = previous_alert["name"]
        self.alert_description = previous_alert.description
        self.alert_severity = previous_alert.severity
        self.alert_message = previous_alert.message
        self.alert_context = previous_alert.context
        self.alert_start_line = previous_alert.start_line
        self.current_alerts = current_alerts


        try:
            self.resolved_alert = self.find_matching_alerts()
        except:
            print("wait")
            self.resolved_alert = self.find_matching_alerts()

    def find_matching_alerts(self):
        """Do a little text cleaning before the query"""
        self.current_alerts["description"] = self.current_alerts.apply(
            lambda x: x["description"].replace('"', "").replace("'", ""),
            axis=1)
        self.current_alerts["description"] = self.current_alerts.apply(
            lambda x: x["description"].replace('"', "").replace("'", ""),
            axis=1)
        self.current_alerts["name"] = self.current_alerts.apply(
            lambda x: x["name"].replace('"', "").replace("'", ""),
            axis=1)

        self.alert_description = self.alert_description.replace('"', "").replace("'", "")
        self.alert_name = self.alert_name.replace('"', "").replace("'", "")

        """Package granularity"""
        matched_alert = self.current_alerts.query(f'name == "{self.alert_name}" and '
                                                  f'description == "{self.alert_description}" and '
                                                  f'severity == "{self.alert_severity}"')

        if len(matched_alert) > 0:
            return False
        else:
            return True


class MatchingAlertsSpotBugs:
    """
    Set resolved alerts for Spotbugs Java Data
    """
    def __init__(self, previous_alert, current_alerts):
        self.alert_filename_clean = previous_alert.source_filepath
        self.alert_category = previous_alert.category
        self.alert_severity = previous_alert.severity
        self.alert_message = previous_alert.message
        self.alert_context = previous_alert.context
        self.current_alerts = current_alerts

        try:
            self.resolved_alert = self.find_matching_alerts()
        except:
            print("wait")
            self.resolved_alert = self.find_matching_alerts()

    def find_matching_alerts(self):
        """Do a little text cleaning before the query"""
        self.current_alerts["message"] = self.current_alerts.apply(
            lambda x: x["message"].replace('"', "").replace("'", ""),
            axis=1)

        self.alert_message = self.alert_message.replace('"', "").replace("'", "")

        matched_alert = self.current_alerts.query(f'source_filepath == "{self.alert_filename_clean}" and '
                                                  f'category == "{self.alert_category}" and '
                                                  f'message == "{self.alert_message}" and '
                                                  f'severity == "{self.alert_severity}" and '
                                                  f'context == "{self.alert_context}"')

        if len(matched_alert) > 0:
            return False
        else:
            return True


class HierarchyAlerts:
    def __init__(self, previous_alert, previous_alerts, current_alerts, current_package_structure):
        self.alert_filename_clean = previous_alert.filename_clean
        self.alert_test_name = previous_alert.test_name
        self.alert_test_id = previous_alert.test_id
        self.alert_issue_severity = previous_alert.issue_severity
        self.alert_issue_confidence = previous_alert.issue_confidence
        self.alert_issue_text = previous_alert.issue_text
        self.alert_context = previous_alert.context
        self.previous_alerts = previous_alerts
        self.current_alerts = current_alerts

        # current package structure
        self.current_package_structure = current_package_structure

        # hierarchy level count of alerts
        # PACKAGE
        self.package_alerts = self.package_level_alerts()
        # FILE
        self.file_alerts = self.file_level_alerts()
        # CONTEXT
        self.context_alerts = self.context_level_alerts()

    def package_level_alerts(self):
        # get total package count for current package alert type
        current_package_alert = self.current_alerts.query(f'test_name == "{self.alert_test_name}" and '
                                                  f'test_id == "{self.alert_test_id}" and '
                                                  f'issue_severity == "{self.alert_issue_severity}" and '
                                                  f'issue_confidence == "{self.alert_issue_confidence}" and '
                                                  f'issue_text == "{self.alert_issue_text}"')

        # get total package count for previous package alert type
        previous_package_alert = self.previous_alerts.query(f'test_name == "{self.alert_test_name}" and '
                                                  f'test_id == "{self.alert_test_id}" and '
                                                  f'issue_severity == "{self.alert_issue_severity}" and '
                                                  f'issue_confidence == "{self.alert_issue_confidence}" and '
                                                  f'issue_text == "{self.alert_issue_text}"')

        # if more alert type count in previous version package than current version package then alert resolved
        if len(previous_package_alert) > len(current_package_alert):
            return [True, len(previous_package_alert) - len(current_package_alert)]
        else:
            return [False, 0]

    def check_file_still_exists(self):
        # check if context still exists in the current package
        if self.alert_filename_clean in self.current_package_structure["filename_clean"].values.tolist():
            return True
        else:
            return False

    def file_level_alerts(self):
        # check if file still exists in the current package
        if self.check_file_still_exists():
            # get total file count for current package alert type
            current_file_alert = self.current_alerts.query(f'filename_clean == "{self.alert_filename_clean}" and '
                                                      f'test_name == "{self.alert_test_name}" and '
                                                      f'test_id == "{self.alert_test_id}" and '
                                                      f'issue_severity == "{self.alert_issue_severity}" and '
                                                      f'issue_confidence == "{self.alert_issue_confidence}" and '
                                                      f'issue_text == "{self.alert_issue_text}"')
            # get total file count for previous package alert type
            previous_file_alert = self.previous_alerts.query(f'filename_clean == "{self.alert_filename_clean}" and '
                                                      f'test_name == "{self.alert_test_name}" and '
                                                      f'test_id == "{self.alert_test_id}" and '
                                                      f'issue_severity == "{self.alert_issue_severity}" and '
                                                      f'issue_confidence == "{self.alert_issue_confidence}" and '
                                                      f'issue_text == "{self.alert_issue_text}"')
            # if more alert type count in previous version package than current version package then alert resolved
            if len(previous_file_alert) > len(current_file_alert):
                return [True, len(previous_file_alert) - len(current_file_alert)]
            else:
                return [False, 0]
        else:
            # represents the file doesn't exist in current package
            return [None, None]

    def check_context_still_exists(self):
        # check if context still exists in the current package
        context_exists = self.alert_context in self.current_package_structure["context"].values.tolist()
        file_exists = self.alert_filename_clean in self.current_package_structure["filename_clean"].values.tolist()
        if (context_exists & file_exists) | (self.alert_context == self.alert_filename_clean):
            return True
        else:
            return False

    def context_level_alerts(self):
        # get total context count for current package alert type
        if self.check_context_still_exists():
            current_context_alert = self.current_alerts.query(f'filename_clean == "{self.alert_filename_clean}" and '
                                                      f'test_name == "{self.alert_test_name}" and '
                                                      f'test_id == "{self.alert_test_id}" and '
                                                      f'issue_severity == "{self.alert_issue_severity}" and '
                                                      f'issue_confidence == "{self.alert_issue_confidence}" and '
                                                      f'issue_text == "{self.alert_issue_text}" and '
                                                      f'context == "{self.alert_context}"')

            # get total context count for previous package alert type
            previous_context_alert = self.previous_alerts.query(f'filename_clean == "{self.alert_filename_clean}" and '
                                                      f'test_name == "{self.alert_test_name}" and '
                                                      f'test_id == "{self.alert_test_id}" and '
                                                      f'issue_severity == "{self.alert_issue_severity}" and '
                                                      f'issue_confidence == "{self.alert_issue_confidence}" and '
                                                      f'issue_text == "{self.alert_issue_text}" and '
                                                      f'context == "{self.alert_context}"')

            # if more alert type count in previous version package than current version package then alert resolved
            if len(previous_context_alert) > len(current_context_alert):
                return [True, len(previous_context_alert) - len(current_context_alert)]
            else:
                return [False, 0]
        else:
            # represents the context doesn't exist in current package
            return [None, None]