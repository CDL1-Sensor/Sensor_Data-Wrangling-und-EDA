from . import utilities


class PipelineRunner:
    __origin: str = None
    __pipeline: str = None
    
    def __init__(self, path):
        self.path = path
    
    def set_path(self, path):
        self.path = path
    
    def set_origin(self, origin):
        self.__origin = origin
        
    def set_pipeline(self, pipeline):
        self.__pipeline = pipeline

    def run(self):
        if self.__origin == "SensorLogger":
            utility = utilities.SensorData(self.path)
            status = utility.set_data()
            data = utility.get_data()

        # return data
        return data
