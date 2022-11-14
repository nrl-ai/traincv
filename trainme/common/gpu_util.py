import math
import os
import platform
import random
import time
from distutils import spawn
from subprocess import PIPE, Popen


class GPU:
    def __init__(
        self,
        id,
        uuid,
        load,
        memory_total,
        memory_used,
        memory_free,
        driver,
        gpu_name,
        serial,
        display_mode,
        display_active,
        temp_gpu,
    ):
        self.id = id
        self.uuid = uuid
        self.load = load
        self.memory_util = float(memory_used) / float(memory_total)
        self.memory_total = memory_total
        self.memory_used = memory_used
        self.memory_free = memory_free
        self.driver = driver
        self.name = gpu_name
        self.serial = serial
        self.display_mode = display_mode
        self.display_active = display_active
        self.temperature = temp_gpu

    def to_dict(self):
        return {
            "id": self.id,
            "uuid": self.uuid,
            "load": self.load,
            "memory_util": self.memory_util,
            "memory_total": self.memory_total,
            "memory_used": self.memory_used,
            "memory_free": self.memory_free,
            "driver": self.driver,
            "name": self.name,
            "serial": self.serial,
            "display_mode": self.display_mode,
            "display_active": self.display_active,
            "temperature": self.temperature,
        }


def safe_float_cast(str_number):
    try:
        number = float(str_number)
    except ValueError:
        number = float("nan")
    return number


def get_gp_us():
    if platform.system() == "Windows":
        # If the platform is Windows and nvidia-smi
        # could not be found from the environment path,
        # try to find it from system drive with default installation path
        nvidia_smi = spawn.find_executable("nvidia-smi")
        if nvidia_smi is None:
            nvidia_smi = (
                f"{os.environ['systemdrive']}\\Program Files\\"
                "NVIDIA Corporation\\NVSMI\\nvidia-smi.exe"
            )
    else:
        nvidia_smi = "nvidia-smi"

    # Get ID, processing and memory utilization for all gp_us
    try:
        with Popen(
            [
                nvidia_smi,
                "--query-gpu=index,uuid,utilization.gpu,memory.total,memory.used,memory.free,"
                "driver_version,name,gpu_serial,display_active,display_mode,temperature.gpu",
                "--format=csv,noheader,nounits",
            ],
            stdout=PIPE,
        ) as p:
            stdout, _ = p.communicate()
    except BaseException:
        return []
    output = stdout.decode("UTF-8")
    lines = output.split(os.linesep)
    num_devices = len(lines) - 1
    gp_us = []
    for g in range(num_devices):
        line = lines[g]
        vals = line.split(", ")
        for i in range(12):
            if i == 0:
                try:
                    device_ids = int(vals[i])
                except BaseException:
                    return []
            elif i == 1:
                uuid = vals[i]
            elif i == 2:
                gpu_util = safe_float_cast(vals[i]) / 100
            elif i == 3:
                mem_total = safe_float_cast(vals[i])
            elif i == 4:
                mem_used = safe_float_cast(vals[i])
            elif i == 5:
                mem_free = safe_float_cast(vals[i])
            elif i == 6:
                driver = vals[i]
            elif i == 7:
                gpu_name = vals[i]
            elif i == 8:
                serial = vals[i]
            elif i == 9:
                display_active = vals[i]
            elif i == 10:
                display_mode = vals[i]
            elif i == 11:
                temp_gpu = safe_float_cast(vals[i])
        gp_us.append(
            GPU(
                device_ids,
                uuid,
                gpu_util,
                mem_total,
                mem_used,
                mem_free,
                driver,
                gpu_name,
                serial,
                display_mode,
                display_active,
                temp_gpu,
            )
        )
    return gp_us  # (deviceIds, gpuUtil, memUtil)


def get_available(
    order="first",
    limit=1,
    max_load=0.5,
    max_memory=0.5,
    memory_free=0,
    include_nan=False,
    exclude_id=None,
    exclude_uuid=None,
):

    if exclude_id is None:
        exclude_id = []
    if exclude_uuid is None:
        exclude_uuid = []

    # order = first | last | random | load | memory
    #    first --> select the GPU with the lowest ID (DEFAULT)
    #    last --> select the GPU with the highest ID
    #    random --> select a random available GPU
    #    load --> select the GPU with the lowest load
    #    memory --> select the GPU with the most memory available
    # limit = 1 (DEFAULT), 2, ..., Inf
    # Limit sets the upper limit for the number of gp_us to return. E.g. if
    # limit = 2, but only one is available, only one is returned.

    # Get device IDs, load and memory usage
    gp_us = get_gp_us()

    # Determine, which gp_us are available
    gp_uavailability = get_availability(
        gp_us,
        max_load=max_load,
        max_memory=max_memory,
        memory_free=memory_free,
        include_nan=include_nan,
        exclude_id=exclude_id,
        exclude_uuid=exclude_uuid,
    )
    avail_able_gp_uindex = [
        idx
        for idx in range(0, len(gp_uavailability))
        if gp_uavailability[idx] == 1
    ]
    # Discard unavailable gp_us
    gp_us = [gp_us[g] for g in avail_able_gp_uindex]

    # Sort available gp_us according to the order argument
    if order == "first":
        gp_us.sort(
            key=lambda x: float("inf") if math.isnan(x.id) else x.id,
            reverse=False,
        )
    elif order == "last":
        gp_us.sort(
            key=lambda x: float("-inf") if math.isnan(x.id) else x.id,
            reverse=True,
        )
    elif order == "random":
        gp_us = [
            gp_us[g] for g in random.sample(range(0, len(gp_us)), len(gp_us))
        ]
    elif order == "load":
        gp_us.sort(
            key=lambda x: float("inf") if math.isnan(x.load) else x.load,
            reverse=False,
        )
    elif order == "memory":
        gp_us.sort(
            key=lambda x: float("inf")
            if math.isnan(x.memory_util)
            else x.memory_util,
            reverse=False,
        )

    # Extract the number of desired gp_us, but limited to the total number of
    # available gp_us
    gp_us = gp_us[0 : min(limit, len(gp_us))]

    # Extract the device IDs from the gp_us and return them
    device_ids = [gpu.id for gpu in gp_us]

    return device_ids


def get_availability(
    gp_us,
    max_load=0.5,
    max_memory=0.5,
    memory_free=0,
    include_nan=False,
    exclude_id=None,
    exclude_uuid=None,
):
    if exclude_id is None:
        exclude_id = []
    if exclude_uuid is None:
        exclude_uuid = []
    # Determine, which gp_us are available
    gp_uavailability = [
        1
        if (gpu.memory_free >= memory_free)
        and (gpu.load < max_load or (include_nan and math.isnan(gpu.load)))
        and (
            gpu.memory_util < max_memory
            or (include_nan and math.isnan(gpu.memory_util))
        )
        and ((gpu.id not in exclude_id) and (gpu.uuid not in exclude_uuid))
        else 0
        for gpu in gp_us
    ]
    return gp_uavailability


def get_first_available(
    order="first",
    max_load=0.5,
    max_memory=0.5,
    attempts=1,
    interval=900,
    verbose=False,
    include_nan=False,
    exclude_id=None,
    exclude_uuid=None,
):

    if exclude_id is None:
        exclude_id = []
    if exclude_uuid is None:
        exclude_uuid = []

    for i in range(attempts):
        if verbose:
            print(
                "Attempting ("
                + str(i + 1)
                + "/"
                + str(attempts)
                + ") to locate available GPU."
            )
        # Get first available GPU
        available = get_available(
            order=order,
            limit=1,
            max_load=max_load,
            max_memory=max_memory,
            include_nan=include_nan,
            exclude_id=exclude_id,
            exclude_uuid=exclude_uuid,
        )
        # If an available GPU was found, break for loop.
        if available:
            if verbose:
                print("GPU " + str(available) + " located!")
            break
        # If this is not the last attempt, sleep for 'interval' seconds
        if i != attempts - 1:
            time.sleep(interval)
    # Check if an GPU was found, or if the attempts simply ran out. Throw
    # error, if no GPU was found
    if not available:
        raise RuntimeError(
            "Could not find an available GPU after "
            + str(attempts)
            + " attempts with "
            + str(interval)
            + " seconds interval."
        )

    # Return found GPU
    return available


def show_utilization(show_all=False, attr_list=None, use_old_code=False):
    gp_us = get_gp_us()
    if show_all:
        if use_old_code:
            print(
                " ID | Name | Serial | UUID || GPU util. | Memory util. ||"
                " Memory total | Memory used | Memory free || Display mode |"
                " Display active |"
            )
            for gpu in gp_us:
                print(
                    " {0:2d} | {1:s}  | {2:s} | {3:s} || {4:3.0f}% | {5:3.0f}%"
                    " || {6:.0f}MB | {7:.0f}MB | {8:.0f}MB || {9:s} | {10:s}"
                    .format(
                        gpu.id,
                        gpu.name,
                        gpu.serial,
                        gpu.uuid,
                        gpu.load * 100,
                        gpu.memory_util * 100,
                        gpu.memory_total,
                        gpu.memory_used,
                        gpu.memory_free,
                        gpu.display_mode,
                        gpu.display_active,
                    )
                )
        else:
            attr_list = [
                [
                    {"attr": "id", "name": "ID"},
                    {"attr": "name", "name": "Name"},
                    {"attr": "serial", "name": "Serial"},
                    {"attr": "uuid", "name": "UUID"},
                ],
                [
                    {
                        "attr": "temperature",
                        "name": "GPU temperature",
                        "suffix": "C",
                        "transform": lambda x: x,
                        "precision": 0,
                    },
                    {
                        "attr": "load",
                        "name": "GPU util.",
                        "suffix": "%",
                        "transform": lambda x: x * 100,
                        "precision": 0,
                    },
                    {
                        "attr": "memory_util",
                        "name": "Memory util.",
                        "suffix": "%",
                        "transform": lambda x: x * 100,
                        "precision": 0,
                    },
                ],
                [
                    {
                        "attr": "memory_total",
                        "name": "Memory total",
                        "suffix": "MB",
                        "precision": 0,
                    },
                    {
                        "attr": "memory_used",
                        "name": "Memory used",
                        "suffix": "MB",
                        "precision": 0,
                    },
                    {
                        "attr": "memory_free",
                        "name": "Memory free",
                        "suffix": "MB",
                        "precision": 0,
                    },
                ],
                [
                    {"attr": "display_mode", "name": "Display mode"},
                    {"attr": "display_active", "name": "Display active"},
                ],
            ]

    else:
        if use_old_code:
            print(" ID  GPU  MEM")
            print("--------------")
            for gpu in gp_us:
                print(
                    " {0:2d} {1:3.0f}% {2:3.0f}%".format(
                        gpu.id, gpu.load * 100, gpu.memory_util * 100
                    )
                )
        elif attr_list is None:
            # if `attr_list` was not specified, use the default one
            attr_list = [
                [
                    {"attr": "id", "name": "ID"},
                    {
                        "attr": "load",
                        "name": "GPU",
                        "suffix": "%",
                        "transform": lambda x: x * 100,
                        "precision": 0,
                    },
                    {
                        "attr": "memory_util",
                        "name": "MEM",
                        "suffix": "%",
                        "transform": lambda x: x * 100,
                        "precision": 0,
                    },
                ],
            ]

    if not use_old_code:
        if attr_list is not None:
            header_string = ""
            gp_ustrings = [""] * len(gp_us)
            for attr_group in attr_list:
                for attr_dict in attr_group:
                    header_string = (
                        header_string + "| " + attr_dict["name"] + " "
                    )
                    header_width = len(attr_dict["name"])
                    min_width = len(attr_dict["name"])

                    attr_precision = (
                        "." + str(attr_dict["precision"])
                        if ("precision" in attr_dict)
                        else ""
                    )
                    attr_suffix = (
                        str(attr_dict["suffix"])
                        if ("suffix" in attr_dict)
                        else ""
                    )
                    attr_transform = (
                        attr_dict["transform"]
                        if ("transform" in attr_dict)
                        else lambda x: x
                    )
                    for gpu in gp_us:
                        attr = getattr(gpu, attr_dict["attr"])

                        attr = attr_transform(attr)

                        if isinstance(attr, float):
                            attr_str = ("{0:" + attr_precision + "f}").format(
                                attr
                            )
                        elif isinstance(attr, int):
                            attr_str = f"{attr:d}"
                        elif isinstance(attr, str):
                            attr_str = attr
                        else:
                            raise TypeError(
                                "Unhandled object type ("
                                + str(type(attr))
                                + ") for attribute '"
                                + attr_dict["name"]
                                + "'"
                            )

                        attr_str += attr_suffix

                        min_width = max(min_width, len(attr_str))

                    header_string += " " * max(0, min_width - header_width)

                    min_width_str = str(min_width - len(attr_suffix))

                    for gpu_idx, gpu in enumerate(gp_us):
                        attr = getattr(gpu, attr_dict["attr"])

                        attr = attr_transform(attr)

                        if isinstance(attr, float):
                            attr_str = (
                                "{0:" + min_width_str + attr_precision + "f}"
                            ).format(attr)
                        elif isinstance(attr, int):
                            attr_str = ("{0:" + min_width_str + "d}").format(
                                attr
                            )
                        elif isinstance(attr, str):
                            attr_str = ("{0:" + min_width_str + "s}").format(
                                attr
                            )
                        else:
                            raise TypeError(
                                "Unhandled object type ("
                                + str(type(attr))
                                + ") for attribute '"
                                + attr_dict["name"]
                                + "'"
                            )

                        attr_str += attr_suffix

                        gp_ustrings[gpu_idx] += "| " + attr_str + " "

                header_string = header_string + "|"
                for gpu_idx, gpu in enumerate(gp_us):
                    gp_ustrings[gpu_idx] += "|"

            header_spacing_string = "-" * len(header_string)
            print(header_string)
            print(header_spacing_string)
            for gp_ustring in gp_ustrings:
                print(gp_ustring)
