import csv


def insert_new_gauge(gauge_id, min_angle, max_angle, min_value, max_value, unit):
    row = [gauge_id, min_angle, max_angle, min_value, max_value, unit]

    with open('../Gauge_calibrations.csv', 'a') as csvFile:
        writer = csv.writer(csvFile)
        writer.writerow(row)

    csvFile.close()


def retrieve_gauge_calibrations (gauge_id):
    with open('../Gauge_calibrations.csv', 'r') as csvFile:
        reader = csv.reader(csvFile)
        for row in reader:
            if row != [] and gauge_id == row[0]:
                csvFile.close()
                return row[1:]
    return -1
