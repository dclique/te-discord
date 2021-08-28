import csv
from datetime import datetime

def read_file():
    with open('dues.csv', mode='r') as csv_file:
        reader = csv.DictReader(csv_file)
        response = [reader.fieldnames]
        for row in reader:
            response.append(row)

        return response

def write_file(dict_to_write):
    with open ('dues.csv', mode='w') as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames = dict_to_write[0])
        writer.writeheader()
        dict_to_write.pop(0)
        for row in dict_to_write:
            writer.writerow(row)

def add_column(curr_dict, column_name):
    curr_dict[0].append(column_name)

    for x in range(1, len(curr_dict)):
        curr_dict[x].update({column_name:'N/A'})
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
    print(month)
    people = []
    for person in month:
        if person == '':
            continue
        if month[person] != 'Y':
            people.append(person)
    return people



def main():
    thefile = read_file()
    #add_column(thefile,'Blaine')
    #filewithoutheader = thefile[1:len(thefile):1]
    mark_paid(thefile, 'Alex', datetime.now().strftime('%B') + str(datetime.today().year), True)
    print(thefile)
    #write_file(thefile)

if __name__ == "__main__":
    main()
        
#write = csv.DictWriter(csv_file, dict_to_write)