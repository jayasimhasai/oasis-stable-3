

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

    checklist = {'temperature': None,
                 'humidity': None,
                 'waterlevel': None,
                 'ph': None,
                 'ec': None}

    # check temperature condition
    if states.tempUL > temperature > states.tempLL:
        checklist['temperature'] = "OK"
    else:
        if temperature > states.tempUL:
            checklist['temperature'] = "UP"
        else:
            checklist['temperature'] = "LOW"

    # check humidity condition
    if states.humidityUL > humidity > states.humidityLL:
        checklist['humidity'] = "OK"
    else:
        if humidity > states.humidityUL:
            checklist['humidity'] = "UP"
        else:
            checklist['humidity'] = "LOW"

    # check waterlevel condition
    if states.waterlevelUL > waterlevel > states.waterlevelLL:
        checklist['waterlevel'] = "OK"
    else:
        if waterlevel > states.tempUL:
            checklist['waterlevel'] = "UP"
        else:
            checklist['waterlevel'] = "LOW"

    # check Ph condition
    if states.phUL > ph > states.phLL:
        checklist['ph'] ="OK"
    else:
        if ph > states.phUL:
            checklist['ph'] ="UP"
        else:
            checklist['ph'] ="LOW"

    # check EC condition
    if states.ecUL > ec > states.ecLL:
        checklist['ec'] ="OK"
    else:
        if ec > states.ecUL:
            checklist['ec'] ="UP"
        else:
            checklist['ec'] ="LOW"

    return checklist


def track_critical_condition(cc_checklist):
    """
    Track a critical condition
    :parameter cc_checklist (string) : checklist of the critical sensor data
    :return: ret(boolean)
    """

    return
