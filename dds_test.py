#!/usr/bin/python

from dataclasses import dataclass
from cyclonedds.domain import DomainParticipant
from cyclonedds.core import Qos, Policy
from cyclonedds.pub import DataWriter
from cyclonedds.sub import DataReader
from cyclonedds.topic import Topic
from cyclonedds.idl import IdlStruct
from cyclonedds.idl.annotations import key
from time import sleep
import numpy as np

import os
name = f"{os.getpid()}"

@dataclass
class Chatter(IdlStruct, typename="Chatter"):
    name: str
    key("name")
    message: str
    count: int

rng = np.random.default_rng()
dp = DomainParticipant()
tp = Topic(dp, "Hello", Chatter, qos=Qos(Policy.Reliability.Reliable(0)))
dw = DataWriter(dp, tp)
dr = DataReader(dp, tp)
count = 0
while True:
    sample = Chatter(name=name, message="Hello, World!", count=count)
    count = count + 1
    print("Writing ", sample)
    dw.write(sample)
    for sample in dr.take(10):
        print("Read ", sample)
    sleep(rng.exponential())

#Extra Import:
'''
try:
    from names import get_full_name
    name = get_full_name()
except:
'''
