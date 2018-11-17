

def check_critical_condition(sensor_data, states):
    """
    Check critical condition of the sensor data
    :parameter: sensor_data (dict) - sensor_data to check critical condition
    :parameter: states  (States()) - states object to get critical limits
    :return: report (dict)
    """
    temperature = sensor_data["temperature"]
    humidity = sensor_data["humidity"]
    waterlevel = sensor_data["waterlevel"]
    ph = sensor_data["ph"]
    ec = sensor_data["ec"]

    checklist = []

    # check temperature condition
    if states.tempUL > temperature > states.tempLL:
        checklist.append("OK")
    else:
        if temperature > states.tempUL:
            checklist.append("UP")
        else:
            checklist.append("LOW")

    # check humidity condition
    if states.humidityUL > humidity > states.humidityLL:
        checklist.append("OK")
    else:
        if humidity > states.humidityUL:
            checklist.append("UP")
        else:
            checklist.append("LOW")

    # check waterlevel condition
    if states.waterlevelUL > waterlevel > states.waterlevelLL:
        checklist.append("OK")
    else:
        if waterlevel > states.tempUL:
            checklist.append("UP")
        else:
            checklist.append("LOW")

    # check Ph condition
    if states.phUL > ph > states.phLL:
        checklist.append("OK")
    else:
        if ph > states.phUL:
            checklist.append("UP")
        else:
            checklist.append("LOW")

    # check EC condition
    if states.ecUL > ec > states.ecLL:
        checklist.append("OK")
    else:
        if ec > states.ecUL:
            checklist.append("UP")
        else:
            checklist.append("LOW")

    return checklist


def track_critical_condition(cc_checklist):
    """
    Track a critical condition
    :parameter cc_checklist (string) : checklist of the critical sensor data
    :return: ret(boolean)
    """

    return
