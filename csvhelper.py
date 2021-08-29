import csv
from datetime import datetime


def read_file(filename):
    with open(filename, mode='r') as csv_file:
        reader = csv.DictReader(csv_file)
        response = [reader.fieldnames]
        for row in reader:
            response.append(row)
        return response


def read_raw(filename):
    with open(filename, mode='r') as csv_file:
        response = []
        reader = csv.reader(csv_file, delimiter=',')
        for row in reader:
            response.append(row)
        return response


def dump_string(curr_file):
    headers = curr_file[0]
    response = ','.join(headers) + '\n'
    for x in range(1, len(curr_file)):
        response += ','.join(curr_file[x]) + '\n'
    return response


def write_file(dict_to_write, filename):
    with open (filename, mode='w', newline='') as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames = dict_to_write[0])
        writer.writeheader()
        dict_to_write.pop(0)
        for row in dict_to_write:
            writer.writerow(row)


def add_column(curr_dict, column_name):
    if column_name in curr_dict[0]:
        raise ValueError
    curr_dict[0].append(column_name)
    for x in range(1, len(curr_dict)):
        curr_dict[x].update({column_name:'N/A'})
    return curr_dict


def delete_column(curr_dict, column_name):
    if column_name not in curr_dict[0]:
        raise ValueError
    for x in range(1, len(curr_dict)):
        curr_dict[x].pop(column_name)
    curr_dict[0].remove(column_name)
    return curr_dict


def mark_paid(curr_dict, payer, time, paid):
    withoutheader = curr_dict[1:len(curr_dict):1]
    people = curr_dict[0]
    if payer not in people:
        raise ValueError

    try:
        month = next(x for x in withoutheader if x[''] == time)
        month[payer] = 'Y' if paid else 'N'
    except StopIteration:
        newmonth = { '': time }
        people = curr_dict[0]
        for person in people:
            if person == '':
                continue
            if person == payer:
                newmonth.update({person: 'Y'})
            else:
                newmonth.update({person: 'N'})
        curr_dict.append(newmonth)


def hasntpaid(curr_dict, time):
    withoutheader = curr_dict[1:len(curr_dict):1]
    month = next(x for x in withoutheader if x[''] == time)
    people = []
    for person in month:
        if person == '':
            continue
        if month[person] != 'Y':
            people.append(person)
    return people


def main():
    print('Wrong place')

if __name__ == "__main__":
    main()