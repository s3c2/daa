import ast
import pandas as pd
import os
import javalang


class FindCodeContext:
    def __init__(self, filename, line_number):
        self.info = pd.DataFrame(columns=["filepath", "type", "name", "lineno", "end_lineno", "parent_class"])
        self.filepath = filename
        self.line_number = line_number

        # parse AST for source file
        with open(filename, "r") as source:
            self.tree = ast.parse(source.read(), mode='exec')

        # create an object with code context (classes, methods, and functions) of a file
        self.get_file_structure()

        # match alert line number to code context within file
        try:
            self.context = self.get_code_context()
        except:
            print("error")

    def get_file_structure(self):
        for node in ast.iter_child_nodes(self.tree):
            # find Functions within File
            if isinstance(node, ast.FunctionDef):
                function_info = [[self.filepath, "function", node.name,
                                  node.lineno, node.end_lineno, None]]
                function_info = pd.DataFrame(function_info, columns=self.info.columns)
                self.info = self.info.append(function_info)

            # find Classes within File
            if isinstance(node, ast.ClassDef):
                class_info = [[self.filepath, "class", node.name,
                               node.lineno, node.end_lineno, None]]
                class_info = pd.DataFrame(class_info, columns=self.info.columns)
                self.info = self.info.append(class_info)

                # find Methods within File
                for child in ast.iter_child_nodes(node):
                    if isinstance(child, ast.FunctionDef):
                        method_info = [[self.filepath, "method", child.name,
                                        child.lineno, child.end_lineno, node.name]]
                        method_info = pd.DataFrame(method_info, columns=self.info.columns)
                        self.info = self.info.append(method_info)

        return self.info

    def get_code_context(self):
        # find the context range based off of alert line number
        context_candidate = self.info.query(f'lineno <= {self.line_number} and '
                                            f'end_lineno >= {self.line_number}')

        # return function, class, method
        if len(context_candidate) == 1:  # will be a function or a class with no methods
            name = context_candidate["name"][0]
            return name
        elif len(context_candidate) > 1:  # returns methods in a full context: Class.method
            context_method = context_candidate.query(f'type == "method"')["name"][0]
            context_class = context_candidate.query(f'type == "class"')["name"][0]
            full_context = f"{context_class}.{context_method}"
            return full_context
        else:  # returns name of file if alert isn't with a code context
            return self.filepath.split("/")[-1]


# get the entire code context
class CompleteContext:
    def __init__(self, package):
        self.package_context = pd.DataFrame(columns=["filepath", "type",
                                                     "context", "lineno",
                                                     "end_lineno", "parent_class"])
        self.package = package

        # get python files in package
        self.filepaths = self.get_package_files()

        print(f"Python files in {self.package}: {len(self.filepaths)}")

        for file in self.filepaths:
            self.filepath = file
            try:
                # parse AST for source file
                with open(file, "r") as source:
                    self.tree = ast.parse(source.read(), mode='exec')

                # create an object with code context (classes, methods, and functions) of a file
                self.get_file_structure()
            except:
                print("Error Parse AST")

        self.package_context["filename_clean"] = self.package_context.apply(
            lambda row: row["filepath"].split(self.package)[-1],
            axis=1)

    def get_package_files(self):
        python_files = []
        for dir_path, sub_dirs, files in os.walk(self.package):
            for x in files:
                if x.endswith(".py"):
                    python_files.append(os.path.join(dir_path, x))

        return python_files

    def get_file_structure(self):
        module_info = pd.DataFrame(columns=self.package_context.columns)
        for node in ast.iter_child_nodes(self.tree):
            # find Functions within File
            if isinstance(node, ast.FunctionDef):
                function_info = [[self.filepath, "function", node.name,
                                  node.lineno, node.end_lineno, None]]
                function_info = pd.DataFrame(function_info, columns=self.package_context.columns)
                module_info = module_info.append(function_info)  # add to global module count for check
                self.package_context = self.package_context.append(function_info)

            # find Classes within File
            if isinstance(node, ast.ClassDef):
                class_info = [[self.filepath, "class", node.name,
                               node.lineno, node.end_lineno, None]]
                class_info = pd.DataFrame(class_info, columns=self.package_context.columns)
                module_info = module_info.append(class_info)  # add to global module count for check
                self.package_context = self.package_context.append(class_info)

                # find Methods within File
                for child in ast.iter_child_nodes(node):
                    if isinstance(child, ast.FunctionDef):
                        method_info = [[self.filepath, "method", child.name,
                                        child.lineno, child.end_lineno, node.name]]
                        method_info = pd.DataFrame(method_info, columns=self.package_context.columns)
                        module_info = module_info.append(method_info)  # add to global module count for check
                        self.package_context = self.package_context.append(method_info)

        if len(module_info) == 0:
            module_info_data = [[self.filepath, "module", None,
                                 0, sum(1 for line in open(self.filepath)), None]]
            module_info_data = pd.DataFrame(module_info_data, columns=self.package_context.columns)
            module_info = module_info.append(module_info_data)
            self.package_context = self.package_context.append(module_info)

        return self.package_context


class FindCodeContextFast:
    def __init__(self, filepath, line_number, package_structure, status, context_path):
        self.info = pd.DataFrame(columns=["filepath", "type", "name", "lineno", "end_lineno", "parent_class"])
        self.filepath = filepath
        self.line_number = line_number
        self.package_structure = package_structure
        self.info = self.package_structure[self.package_structure["filepath"] == filepath]

        if self.line_number == 4876:
            print("wait")

        # match alert line number to code context within file
        try:
            self.context = self.get_code_context()
        except:
            print("Error")
            self.context = self.get_code_context()

    def get_code_context(self):
        # find the context range based off of alert line number
        context_candidate = self.info.query(f'lineno <= {self.line_number} and '
                                            f'end_lineno >= {self.line_number}')

        # return function, class, method
        if len(context_candidate) == 1:  # will be a function or a class with no methods
            name = context_candidate["context"].values.tolist()[0]
            return name
        elif len(context_candidate) > 1:  # returns methods in a full context: Class.method
            context_method = context_candidate.query(f'type == "method"')["context"].values.tolist()[0]
            context_class = context_candidate.query(f'type == "class"')["context"].values.tolist()[0]
            full_context = f"{context_class}.{context_method}"
            return full_context
        else:  # returns name of file if alert isn't with a code context
            return self.filepath.split("/")[-1]


# get the entire code context and save CSV output
class PythonCompleteContextSaveFile:
    def __init__(self, package, output_path):
        self.package_context = pd.DataFrame(columns=["filepath", "type",
                                                     "context", "lineno",
                                                     "end_lineno", "parent_class"])
        self.package = package

        # get python files in package
        self.filepaths = self.get_package_files()

        print(f"Python files in {self.package}: {len(self.filepaths)}")

        for file in self.filepaths:
            self.filepath = file
            try:
                # parse AST for source file
                with open(file, "r") as source:
                    self.tree = ast.parse(source.read(), mode='exec')

                # create an object with code context (classes, methods, and functions) of a file
                self.get_file_structure()
            except:
                print("Error Parse AST")

        self.package_context["filename_clean"] = self.package_context.apply(
            lambda row: row["filepath"].split(self.package)[-1],
            axis=1)

        """Save package_context to a CSV file in desired output_path"""
        self.package_context.to_csv(output_path,
                                    encoding='utf-8',
                                    index=False)

    def get_package_files(self):
        python_files = []
        for dir_path, sub_dirs, files in os.walk(self.package):
            for x in files:
                if x.endswith(".py"):
                    python_files.append(os.path.join(dir_path, x))

        return python_files

    def get_file_structure(self):
        module_info = pd.DataFrame(columns=self.package_context.columns)
        for node in ast.iter_child_nodes(self.tree):
            # find Functions within File
            if isinstance(node, ast.FunctionDef):
                function_info = [[self.filepath, "function", node.name,
                                  node.lineno, node.end_lineno, None]]
                function_info = pd.DataFrame(function_info, columns=self.package_context.columns)
                module_info = module_info.append(function_info)  # add to global module count for check
                self.package_context = self.package_context.append(function_info)

            # find Classes within File
            if isinstance(node, ast.ClassDef):
                class_info = [[self.filepath, "class", node.name,
                               node.lineno, node.end_lineno, None]]
                class_info = pd.DataFrame(class_info, columns=self.package_context.columns)
                module_info = module_info.append(class_info)  # add to global module count for check
                self.package_context = self.package_context.append(class_info)

                # find Methods within File
                for child in ast.iter_child_nodes(node):
                    if isinstance(child, ast.FunctionDef):
                        method_info = [[self.filepath, "method", child.name,
                                        child.lineno, child.end_lineno, node.name]]
                        method_info = pd.DataFrame(method_info, columns=self.package_context.columns)
                        module_info = module_info.append(method_info)  # add to global module count for check
                        self.package_context = self.package_context.append(method_info)

        if len(module_info) == 0:
            module_info_data = [[self.filepath, "module", None,
                                 0, sum(1 for line in open(self.filepath)), None]]
            module_info_data = pd.DataFrame(module_info_data, columns=self.package_context.columns)
            module_info = module_info.append(module_info_data)
            self.package_context = self.package_context.append(module_info)

        return self.package_context


"""=================================================================================================================="""
"""=====================================================JAVA========================================================="""
"""=================================================================================================================="""


def get_project_structure(base_directory):
    """
    The file structure of the built Java do not match the original structure location
    Validation command: find ./ -type f -name '*.java' | wc -l
    """
    project_files = []

    for r, d, f in os.walk(f"{base_directory}"):
        for file in f:
            if file.endswith(".java"):
                path = os.path.join(r, file)
                project_files.append(path)

    project_files = pd.DataFrame(project_files, columns=["java_file"])

    return project_files


class FindCodeContextJava:
    def __init__(self, filename, line_number):
        self.info = pd.DataFrame(columns=["filepath", "type", "name", "lineno", "end_lineno", "parent_class"])
        self.filepath = filename
        self.line_number = line_number
        self.project_files = pd.DataFrame(columns=["java_file"])

        try:
            # parse AST for source file
            with open(self.filepath, "r") as source:
                # parse java file
                self.tree = javalang.parse.parse(source.read())
                source.close()

            # count length of file
            self.file_line_count = sum(1 for line in open(self.filepath))
        except:
            print("Error with loading javalang.parse.parse(source.read()) in find_code_context.py")
            # parse AST for source file
            with open(self.filepath, "r") as source:
                # parse java file
                self.tree = javalang.parse.parse(source.read())
                source.close()
            self.file_line_count = sum(1 for line in open(self.filepath))

        # create an object with code context (classes, methods, and functions) of a file
        try:
            self.get_file_structure()
        except:
            print("Error with self.get_file_structure() in find_code_context.py")
            self.get_file_structure()

        # match alert line number to code context within file
        try:
            self.context = self.get_code_context()
        except:
            print("Error with self.get_code_context() in find_code_context.py")
            self.context = self.get_code_context()

    def get_file_structure(self):
        # list of Declration types to skip
        # FieldDeclaration = variable names
        # list is just a list not a context value

        for type_index in self.tree.types:
            # find Classes within File
            parent_type = type(type_index).__name__
            parent_name = type_index.name
            parent_line_start = type_index.position.line
            parent_info = [[self.filepath, parent_type, parent_name,
                            parent_line_start, None, None]]
            parent_info = pd.DataFrame(parent_info, columns=self.info.columns)
            self.info = self.info.append(parent_info)

            # find constructors/field declaration/methods
            errors = []
            try:
                """Try for a body.declarations"""
                for body_index in type_index.body.declarations:
                    if type(body_index).__name__ in ["ConstructorDeclaration", "MethodDeclaration", "ClassDeclaration"]:
                        declaration_name = body_index.name
                        declaration_line_start = body_index.position.line
                        body_info = [[self.filepath, type(body_index).__name__, declaration_name,
                                      declaration_line_start, None, parent_name]]
                        body_info = pd.DataFrame(body_info, columns=self.info.columns)
                        self.info = self.info.append(body_info)
                    else:
                        pass
            except:
                """Else run through the regular body"""
                for body_index in type_index.body:
                    if type(body_index).__name__ in ["ConstructorDeclaration", "MethodDeclaration", "ClassDeclaration"]:
                        declaration_name = body_index.name
                        declaration_line_start = body_index.position.line
                        body_info = [[self.filepath, type(body_index).__name__, declaration_name,
                                      declaration_line_start, None, parent_name]]
                        body_info = pd.DataFrame(body_info, columns=self.info.columns)
                        self.info = self.info.append(body_info)
                    else:
                        pass

        # reset index
        self.info = self.info.reset_index(drop=True)

        # set Classes end_lineno
        temp_classes = self.info[self.info["type"] == "ClassDeclaration"].reset_index(drop=True)
        if len(temp_classes) == 1:
            temp_classes["end_lineno"] = self.file_line_count
        else:
            for i in range(0, len(temp_classes)):
                if i == len(temp_classes) - 1:
                    temp_classes.iloc[i].end_lineno = self.file_line_count
                else:
                    temp_classes.iloc[i].end_lineno = temp_classes.iloc[i + 1].lineno - 1

        # set Methods end_lineno
        temp_methods = self.info[self.info["type"] != "ClassDeclaration"].reset_index(drop=True)
        if len(temp_methods) == 1:
            temp_methods["end_lineno"] = self.file_line_count
        else:
            for i in range(0, len(temp_methods)):
                if i == len(temp_methods) - 1:
                    temp_methods.iloc[i].end_lineno = self.file_line_count
                else:
                    temp_methods.iloc[i].end_lineno = temp_methods.iloc[i + 1].lineno - 1

        # make sure Method end_lineno's are not greater than the parent classes
        # this is needed because of the sort above
        # we don't seperate Classes for the end_lineno...kind of messy but it works
        temp_classes["end_lineno"] = pd.to_numeric(temp_classes["end_lineno"])
        temp_methods["end_lineno"] = pd.to_numeric(temp_methods["end_lineno"])

        if len(temp_classes) > 0 and len(temp_methods) > 0:
            temp_methods["end_lineno"] = temp_methods.apply(
                lambda x: temp_classes[temp_classes["name"] == x['parent_class']].iloc[0].end_lineno if (
                            x['end_lineno'] > temp_classes[temp_classes["name"] == x['parent_class']].iloc[
                        0].end_lineno) else x['end_lineno'],
                axis=1)

        # combine the two temp DFs for the self.info
        self.info = pd.concat([temp_classes, temp_methods])
        self.info = self.info.reset_index(drop=True)
        return self.info

    def get_code_context(self):
        # find the context range based off of alert line number
        context_candidate = self.info.query(f'lineno <= {self.line_number} and '
                                            f'end_lineno >= {self.line_number}')

        # return class or method
        if len(context_candidate) == 1:  # will be a function or a class with no methods
            name = context_candidate["name"].reset_index(drop=True)[0]
            return name
        elif len(context_candidate) > 1:  # returns methods in a full context: Class.method
            context_method = context_candidate.query(f'type != "ClassDeclaration"')["name"].reset_index(drop=True)[0]
            context_class = context_candidate.query(f'type == "ClassDeclaration"')["name"].reset_index(drop=True)[0]
            full_context = f"{context_class}.{context_method}"
            return full_context
        else:  # returns name of file if alert isn't within a code context
            return self.filepath.split("/")[-1]


class FindCodeContextJavaFast:
    def __init__(self, code_context, line_number, filename):
        self.info = code_context[code_context["filename_clean"] == filename]
        self.line_number = line_number
        self.filename = filename

        # match alert line number to code context within file
        try:
            self.context = self.get_code_context()
        except:
            print("Error with self.get_code_context() in find_code_context.py")
            self.context = self.get_code_context()

    def get_code_context(self):
        # find the context range based off of alert line number
        context_candidate = self.info.query(f'lineno <= {self.line_number} and '
                                            f'end_lineno >= {self.line_number}')

        # return class or method
        if len(context_candidate) == 1:  # will be a function or a class with no methods
            name = context_candidate["name"].reset_index(drop=True)[0]
            return name
        elif len(context_candidate) > 1:  # returns methods in a full context: Class.method
            context_method = context_candidate.query(f'type != "ClassDeclaration"')["name"].reset_index(drop=True)[0]
            context_class = context_candidate.query(f'type == "ClassDeclaration"')["name"].reset_index(drop=True)[0]
            full_context = f"{context_class}.{context_method}"
            return full_context
        else:  # returns name of file if alert isn't within a code context
            return self.filename.split("/")[-1]


def java_load_codeql_data(filepath):
    temp_eval = pd.read_csv(filepath, header=0, names=['name', 'description',
                                                       'severity', 'message',
                                                       'path', 'start_line',
                                                       'start_column', 'end_line',
                                                       'end_column'])
    if len(temp_eval) > 0:
        temp_eval["codeql_file"] = filepath
        temp_eval["cve"] = filepath.split("__")[1]
        temp_eval["commit_sha"] = filepath.split("__")[4]
        temp_eval["repo_owner"] = filepath.split("__")[2]
        temp_eval["repo_name"] = filepath.split("__")[3]
        temp_eval["file"] = temp_eval.apply(lambda x: x["path"].split("/")[-1],
                                            axis=1)
        return temp_eval

def java_load_spotbugs_data(filepath):
    """Function to load SpotBugs data properly"""
    temp_eval = pd.read_csv(filepath)
    temp_eval["spotbugs_file"] = filepath
    temp_eval["cve"] = filepath.split("__")[1]
    temp_eval["commit_sha"] = filepath.split("__")[4]
    temp_eval["repo_owner"] = filepath.split("__")[2]
    temp_eval["repo_name"] = filepath.split("__")[3]
    temp_eval["file"] = temp_eval.apply(lambda x: x["fileName"].split("/")[-1],
                                        axis=1)
    return temp_eval


class JavaCompleteContextSaveFile:
    def __init__(self, package, output_path, alerts_path):
        self.package = package
        self.complete_info = pd.DataFrame(columns=["filepath", "type", "name", "lineno", "end_lineno", "parent_class"])

        # get java files in package
        self.file_structure = pd.DataFrame(self.get_package_files(), columns=["java_file"])

        """Only find the code context for files that have alerts from CodeQL"""
        self.alerts = java_load_codeql_data(alerts_path)

        """Return if No Alerts in file exist"""
        if self.alerts is None:
            return

        self.file_structure["source_filepath"] = self.file_structure.apply(
            lambda x: x["java_file"].split(self.package)[-1],
            axis=1)

        self.alerts["source_filepath"] = self.alerts.apply(
            lambda x: x["path"].split("/build/")[-1],
            axis=1)

        self.filepaths = self.alerts.merge(self.file_structure,
                                                on=["source_filepath"],
                                                how="left")

        self.filepaths_review = self.filepaths["java_file"].drop_duplicates().dropna().values.tolist()

        print(f"Python files in {self.package}: {len(self.filepaths)}")

        errors = 1
        for index, file in enumerate(self.filepaths_review):
            print(f"{index}/{len(self.filepaths)}")
            self.filepath = file
            try:
                # parse AST for source file
                with open(file, "r") as source:
                    self.tree = javalang.parse.parse(source.read())
                    source.close()

                # count length of file
                self.file_line_count = sum(1 for line in open(self.filepath))

                # create an object with code context (classes, methods, and functions) of a file
                self.complete_info = self.complete_info.append(self.get_file_structure())
            except:
                print(f"Error Parse AST: {errors}")
                errors = errors + 1

        self.complete_info["filename_clean"] = self.complete_info.apply(
            lambda row: row["filepath"].split(self.package)[-1],
            axis=1)

        """Save package_context to a CSV file in desired output_path"""
        self.complete_info.to_csv(output_path,
                         encoding='utf-8',
                         index=False)

    def get_file_structure(self):
        # list of Declration types to skip
        # FieldDeclaration = variable names
        # list is just a list not a context value
        if len(self.tree.types) > 0:
            for type_index in self.tree.types:
                """Create a temporary info DF for file structure"""
                self.info = pd.DataFrame(columns=["filepath", "type", "name", "lineno", "end_lineno", "parent_class"])
                # find Classes within File
                parent_type = type(type_index).__name__
                parent_name = type_index.name
                parent_line_start = type_index.position.line
                parent_info = [[self.filepath, parent_type, parent_name,
                                parent_line_start, None, None]]
                parent_info = pd.DataFrame(parent_info, columns=self.info.columns)
                self.info = self.info.append(parent_info)

                # find constructors/field declaration/methods
                errors = []
                try:
                    """Try for a body.declarations"""
                    for body_index in type_index.body.declarations:
                        if type(body_index).__name__ in ["ConstructorDeclaration", "MethodDeclaration", "ClassDeclaration"]:
                            declaration_name = body_index.name
                            declaration_line_start = body_index.position.line
                            body_info = [[self.filepath, type(body_index).__name__, declaration_name,
                                          declaration_line_start, None, parent_name]]
                            body_info = pd.DataFrame(body_info, columns=self.info.columns)
                            self.info = self.info.append(body_info)
                        else:
                            pass
                except:
                    """Else run through the regular body"""
                    for body_index in type_index.body:
                        if type(body_index).__name__ in ["ConstructorDeclaration", "MethodDeclaration", "ClassDeclaration"]:
                            declaration_name = body_index.name
                            declaration_line_start = body_index.position.line
                            body_info = [[self.filepath, type(body_index).__name__, declaration_name,
                                          declaration_line_start, None, parent_name]]
                            body_info = pd.DataFrame(body_info, columns=self.info.columns)
                            self.info = self.info.append(body_info)
                        else:
                            pass

            # reset index
            self.info = self.info.reset_index(drop=True)

            # set Classes end_lineno
            temp_classes = self.info[self.info["type"] == "ClassDeclaration"].reset_index(drop=True)
            if len(temp_classes) == 1:
                temp_classes["end_lineno"] = self.file_line_count
            else:
                for i in range(0, len(temp_classes)):
                    if i == len(temp_classes) - 1:
                        temp_classes.iloc[i].end_lineno = self.file_line_count
                    else:
                        temp_classes.iloc[i].end_lineno = temp_classes.iloc[i + 1].lineno - 1

            # set Methods end_lineno
            temp_methods = self.info[self.info["type"] != "ClassDeclaration"].reset_index(drop=True)
            if len(temp_methods) == 1:
                temp_methods["end_lineno"] = self.file_line_count
            else:
                for i in range(0, len(temp_methods)):
                    if i == len(temp_methods) - 1:
                        temp_methods.iloc[i].end_lineno = self.file_line_count
                    else:
                        temp_methods.iloc[i].end_lineno = temp_methods.iloc[i + 1].lineno - 1

            # make sure Method end_lineno's are not greater than the parent classes
            # this is needed because of the sort above
            # we don't seperate Classes for the end_lineno...kind of messy but it works
            temp_classes["end_lineno"] = pd.to_numeric(temp_classes["end_lineno"])
            temp_methods["end_lineno"] = pd.to_numeric(temp_methods["end_lineno"])

            if len(temp_classes) > 0 and len(temp_methods) > 0:
                temp_methods["end_lineno"] = temp_methods.apply(
                    lambda x: self.validate_end_line(temp_classes, x["parent_class"], x["end_lineno"]),
                    axis=1)

            # combine the two temp DFs for the self.info
            self.info = pd.concat([temp_classes, temp_methods])
            self.info = self.info.reset_index(drop=True)
            return self.info
        else:
            """Return file length if no structure exist for the file"""
            self.info = pd.DataFrame([[None, None, None, None, None, None]],
                                     columns=["filepath", "type", "name", "lineno", "end_lineno", "parent_class"])
            self.info["filepath"] = self.filepath
            self.info["type"] = "File"
            self.info["name"] = self.filepath.split("/")[-1]
            self.info["lineno"] = 0
            self.info["end_lineno"] = self.file_line_count
            self.info["parent_class"] = None
            return self.info


    def validate_end_line(self, temp_classes, parent_class, end_line):
        """
        make sure Method end_lineno's are not greater than the parent classes
        :param temp_classes:
        :param parent_class:
        :param end_line:
        :return:
        """
        temp_classes_match = temp_classes[temp_classes["name"] == parent_class]
        if len(temp_classes_match) > 0:
            if end_line > temp_classes_match.iloc[0].end_lineno:
                return temp_classes_match.iloc[0].end_lineno
            else:
                return end_line
        else:
            return end_line


    def get_package_files(self):
        java_files = []
        for dir_path, sub_dirs, files in os.walk(self.package):
            for x in files:
                if x.endswith(".java"):
                    java_files.append(os.path.join(dir_path, x))

        return java_files


class JavaSpotBugsCompleteContextSaveFile:
    def __init__(self, package, output_path, alerts_path):
        self.package = package
        self.complete_info = pd.DataFrame(columns=["filepath", "type", "name", "lineno", "end_lineno", "parent_class"])

        # get java files in package
        self.file_structure = pd.DataFrame(self.get_package_files(), columns=["java_file"])

        """Only find the code context for files that have alerts from CodeQL"""
        try:
            self.alerts = java_load_spotbugs_data(alerts_path)
        except:
            self.alerts = java_load_spotbugs_data(alerts_path)

        self.file_structure["source_filepath"] = self.file_structure.apply(
            lambda x: x["java_file"].split(self.package)[-1],
            axis=1)

        self.alerts["source_filepath"] = self.alerts.apply(
            lambda x: x["fileName"].split("build/")[-1],
            axis=1)

        self.filepaths = self.alerts.merge(self.file_structure,
                                                on=["source_filepath"],
                                                how="left")

        self.filepaths_review = self.filepaths["java_file"].drop_duplicates().dropna().values.tolist()

        print(f"Python files in {self.package}: {len(self.filepaths_review)}")

        errors = 1
        for index, file in enumerate(self.filepaths_review):
            print(f"{index}/{len(self.filepaths_review)}")
            self.filepath = file
            try:
                # parse AST for source file
                with open(file, "r") as source:
                    self.tree = javalang.parse.parse(source.read())
                    source.close()

                # count length of file
                self.file_line_count = sum(1 for line in open(self.filepath))

                # create an object with code context (classes, methods, and functions) of a file
                self.complete_info = self.complete_info.append(self.get_file_structure())
            except:
                print(f"Error Parse AST: {errors}")
                errors = errors + 1

        self.complete_info["filename_clean"] = self.complete_info.apply(
            lambda row: row["filepath"].split(self.package)[-1],
            axis=1)

        """Save package_context to a CSV file in desired output_path"""
        self.complete_info.to_csv(output_path,
                         encoding='utf-8',
                         index=False)

    def get_file_structure(self):
        # list of Declration types to skip
        # FieldDeclaration = variable names
        # list is just a list not a context value
        if len(self.tree.types) > 0:
            for type_index in self.tree.types:
                """Create a temporary info DF for file structure"""
                self.info = pd.DataFrame(columns=["filepath", "type", "name", "lineno", "end_lineno", "parent_class"])
                # find Classes within File
                parent_type = type(type_index).__name__
                parent_name = type_index.name
                parent_line_start = type_index.position.line
                parent_info = [[self.filepath, parent_type, parent_name,
                                parent_line_start, None, None]]
                parent_info = pd.DataFrame(parent_info, columns=self.info.columns)
                self.info = self.info.append(parent_info)

                # find constructors/field declaration/methods
                errors = []
                try:
                    """Try for a body.declarations"""
                    for body_index in type_index.body.declarations:
                        if type(body_index).__name__ in ["ConstructorDeclaration", "MethodDeclaration", "ClassDeclaration"]:
                            declaration_name = body_index.name
                            declaration_line_start = body_index.position.line
                            body_info = [[self.filepath, type(body_index).__name__, declaration_name,
                                          declaration_line_start, None, parent_name]]
                            body_info = pd.DataFrame(body_info, columns=self.info.columns)
                            self.info = self.info.append(body_info)
                        else:
                            pass
                except:
                    """Else run through the regular body"""
                    for body_index in type_index.body:
                        if type(body_index).__name__ in ["ConstructorDeclaration", "MethodDeclaration", "ClassDeclaration"]:
                            declaration_name = body_index.name
                            declaration_line_start = body_index.position.line
                            body_info = [[self.filepath, type(body_index).__name__, declaration_name,
                                          declaration_line_start, None, parent_name]]
                            body_info = pd.DataFrame(body_info, columns=self.info.columns)
                            self.info = self.info.append(body_info)
                        else:
                            pass

            # reset index
            self.info = self.info.reset_index(drop=True)

            # set Classes end_lineno
            temp_classes = self.info[self.info["type"] == "ClassDeclaration"].reset_index(drop=True)
            if len(temp_classes) == 1:
                temp_classes["end_lineno"] = self.file_line_count
            else:
                for i in range(0, len(temp_classes)):
                    if i == len(temp_classes) - 1:
                        temp_classes.iloc[i].end_lineno = self.file_line_count
                    else:
                        temp_classes.iloc[i].end_lineno = temp_classes.iloc[i + 1].lineno - 1

            # set Methods end_lineno
            temp_methods = self.info[self.info["type"] != "ClassDeclaration"].reset_index(drop=True)
            if len(temp_methods) == 1:
                temp_methods["end_lineno"] = self.file_line_count
            else:
                for i in range(0, len(temp_methods)):
                    if i == len(temp_methods) - 1:
                        temp_methods.iloc[i].end_lineno = self.file_line_count
                    else:
                        temp_methods.iloc[i].end_lineno = temp_methods.iloc[i + 1].lineno - 1

            # make sure Method end_lineno's are not greater than the parent classes
            # this is needed because of the sort above
            # we don't seperate Classes for the end_lineno...kind of messy but it works
            temp_classes["end_lineno"] = pd.to_numeric(temp_classes["end_lineno"])
            temp_methods["end_lineno"] = pd.to_numeric(temp_methods["end_lineno"])

            if len(temp_classes) > 0 and len(temp_methods) > 0:
                temp_methods["end_lineno"] = temp_methods.apply(
                    lambda x: self.validate_end_line(temp_classes, x["parent_class"], x["end_lineno"]),
                    axis=1)

            # combine the two temp DFs for the self.info
            self.info = pd.concat([temp_classes, temp_methods])
            self.info = self.info.reset_index(drop=True)
            return self.info
        else:
            """Return file length if no structure exist for the file"""
            self.info = pd.DataFrame([[None, None, None, None, None, None]],
                                     columns=["filepath", "type", "name", "lineno", "end_lineno", "parent_class"])
            self.info["filepath"] = self.filepath
            self.info["type"] = "File"
            self.info["name"] = self.filepath.split("/")[-1]
            self.info["lineno"] = 0
            self.info["end_lineno"] = self.file_line_count
            self.info["parent_class"] = None
            return self.info


    def validate_end_line(self, temp_classes, parent_class, end_line):
        """
        make sure Method end_lineno's are not greater than the parent classes
        :param temp_classes:
        :param parent_class:
        :param end_line:
        :return:
        """
        temp_classes_match = temp_classes[temp_classes["name"] == parent_class]
        if len(temp_classes_match) > 0:
            if end_line > temp_classes_match.iloc[0].end_lineno:
                return temp_classes_match.iloc[0].end_lineno
            else:
                return end_line
        else:
            return end_line


    def get_package_files(self):
        java_files = []
        for dir_path, sub_dirs, files in os.walk(self.package):
            for x in files:
                if x.endswith(".java"):
                    java_files.append(os.path.join(dir_path, x))

        return java_files