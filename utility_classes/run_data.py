from utility_classes import utility_class


class RunData(utility_class.UtilityClass):
    default_values = [False, False]

    def __init__(self, looping: bool, original: bool):
        self.looping: bool = looping
        self.original: bool = original


utility_class.initialize_class(RunData)
