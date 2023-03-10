import glob
import polars as pl
import numpy as np
from tqdm.notebook import tqdm
from pathlib import Path
import os
from dataclasses import dataclass
from dataclasses_tensor import dataclass_tensor, config
from enum import Enum

class Message():
    ERROR = "502"
    ERROR_PROCESSING = "503"
    SUCCESS = "200"
    NOT_FOUND = "404"

class Activity(Enum):
    SITZEN = 1
    STEHEN = 2
    LAUFEN = 3
    RENNEN = 4
    FAHRRAD = 5
    TREPPENGEHEN = 6

class User(Enum):
    ETIENNE = 1
    BEN = 2
    LEA = 3
    FLORIN = 4
    GABRIEL = 5
    MANJAVY = 6
    OGNJEN = 7
    TOBIAS = 8
    WEIPING = 9
    YVO = 10

@dataclass_tensor
@dataclass
class State:
    user: User
    activity: Activity
    
    

class SensorData:
    __data: pl.DataFrame = None
    
    def __init__(self, path):
        self.path = path
    
    def get_data(self):
        return self.__data

    def set_data(self):
        glob_path = os.path.join(self.path, "**", "*.json")
        files = glob.glob(glob_path, recursive=True)
        files.sort()

        data = None
        for file in tqdm(
            files,
            desc="Read Files",
            unit="files",
        ):
            try:
                bootstraping = pl.read_json(file)
                bootstraping = bootstraping.fill_null(value=np.nan)
                bootstraping = bootstraping.melt(id_vars=["time", "sensor"])
                bootstraping = bootstraping.drop_nulls()
                bootstraping = bootstraping.with_columns(
                    (pl.col("sensor") + "_" + pl.col("variable")).alias("variable")
                )
                bootstraping = bootstraping.drop(["sensor"])
                bootstraping = bootstraping.with_columns(pl.from_epoch("time", unit="ns").alias("time"))
                bootstraping = bootstraping.with_columns(pl.from_epoch("time", unit="ms").alias("time"))
                bootstraping = bootstraping.with_columns(
                    pl.col("value").cast(pl.Float64, strict=False).alias("value")
                )
                bootstraping = bootstraping.pivot(
                    index="time",
                    columns="variable",
                    values="value",
                )
                cols = [
                    "time",
                    "Accelerometer_x",
                    "Accelerometer_y",
                    "Accelerometer_z",
                    "Gyroscope_x",
                    "Gyroscope_y",
                    "Gyroscope_z",
                    "Magnetometer_x",
                    "Magnetometer_y",
                    "Magnetometer_z",
                    "Orientation_qx",
                    "Orientation_qy",
                    "Orientation_qz",
                ]
                bootstraping = bootstraping[cols]
                bootstraping = bootstraping.filter(pl.all(set(cols) - {"time"}).is_not_null())
                if os.name == 'nt':
                    bootstraping = bootstraping.with_columns(
                        pl.lit(file.split("\\")[-1].split(".")[0]).alias("id")
                    )
                    bootstraping = bootstraping.with_columns(pl.lit(file.split("\\")[-2]).alias("user"))
                    bootstraping = bootstraping.with_columns(pl.lit(file.split("\\")[-3]).alias("class"))
                    
                else:
                    bootstraping = bootstraping.with_columns(
                        pl.lit(file.split("/")[-1].split(".")[0]).alias("id")
                    )
                    bootstraping = bootstraping.with_columns(pl.lit(file.split("/")[-2]).alias("user"))
                    bootstraping = bootstraping.with_columns(pl.lit(file.split("/")[-3]).alias("class"))   
                if type(self.__data) == type(None):
                    self.__data = bootstraping
                else:
                    self.__data = pl.concat([self.__data, bootstraping], how="diagonal")

            except Exception as e:
                print(f"{Message.ERROR_PROCESSING} {file}: {e}")
        
        return Message.SUCCESS
