from pydantic import BaseModel

import fipiran


class StrictModel(BaseModel, extra='forbid'):
    pass


fipiran._LooseModel = StrictModel
