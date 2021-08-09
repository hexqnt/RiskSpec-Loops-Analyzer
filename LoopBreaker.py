class LoopBreaker:
    _g = None
    _max_level: int
    _max_init_edges: int
    _max_second_edges: int
    _log_file_path: str
    _filt_file_path: str
    _filt_regex: str
    IsFiltInpEdges: bool

    def __init__(self, g):
        _g = g

    @property
    def MaxNestingLevel(self):
        return self._max_level

    @MaxNestingLevel.setter
    def MaxNestingLevel(self, level:int):
        if level>=0:
            self._max_level = level
        else:
            raise ValueError('level must not be negative')

    @property
    def MaxInitEdges(self):
        return self._max_init_edges

    @MaxInitEdges.setter
    def MaxInitEdges(self, count :int):
        if count>=0:
            self._max_init_edges = count
        else:
            raise ValueError('count must not be negative')

    @property
    def MaxSecondEdges(self):
        return self._max_second_edges

    @MaxSecondEdges.setter
    def MaxSecondEdges(self, count :int):
        if count>=0:
            self._max_second_edges = count
        else:
            raise ValueError('count must not be negative')

    @property
    def LogFilePath(self):
        return self._log_file_path

    @LogFilePath.setter
    def LogFilePath(self, filepath :str):
        if len(filepath)>0
            self._log_file_path = filepath
        else:
            raise ValueError('not availible log file path')

    @property
    def FiltFilePath(self):
        return self._filt_file_path

    @FiltFilePath.setter
    def FiltFilePath(self, filepath :str):
        if len(filepath)>0
            self._filt_file_path = filepath
        else:
            raise ValueError('not availible filt file path')



