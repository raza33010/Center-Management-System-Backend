def ArrayChallenge(strArr):
    No_of_gas_station = int(strArr[0])
    gas_stations = [tuple(map(int, station.split(":"))) for station in strArr[1:]]

    amount_of_gas_avaiable_at_station = 0
    start_station = 0
    total_gas = 0

    for i in range(No_of_gas_station):
        gas, cost = gas_stations[i]
        total_gas += gas
        total_gas -= cost
        amount_of_gas_avaiable_at_station += gas
        amount_of_gas_avaiable_at_station -= cost

        if amount_of_gas_avaiable_at_station < 0:
            amount_of_gas_avaiable_at_station = 0
            start_station = i + 1

    if total_gas < 0 or No_of_gas_station == 0:
        return "impossible"
    else:
        return str(start_station + 1)

print(ArrayChallenge(input()))
