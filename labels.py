class Label:
    all_labels = []

    def __init__(self, name, line, chunk, is_def_label=False):
        self.name = name
        self.line = line
        self.chunk = chunk
        self.is_def_label = is_def_label
        Label.all_labels.append(self)

    def execute_label(self, run_command):
        run_command(self.chunk)

    @property
    def is_null(self):
        return self.name == "" and self.line == 0 and self.chunk == ""

    def __repr__(self):
        return str(self.chunk)


def find_label(label_name):
    for label in Label.all_labels:
        if label.name == label_name:
            return label
    return Label("", 0, "")
