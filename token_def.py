class TokDef:
    all_tok_defs = []

    @staticmethod
    def FindTokDef(name):
        for tok_def in TokDef.all_tok_defs:
            if tok_def.name == name:
                return tok_def
        return None

    def __init__(self, name, definition):
        self.name = name
        self.definition = definition
        TokDef.all_tok_defs.append(self)

    def destroy(self):
        TokDef.all_tok_defs.remove(self)
        del self
