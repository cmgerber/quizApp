from random import randint
import csv

student_id_list = []
while len(student_id_list) != 60:
    sid = randint(10000,99999)
    if sid not in student_id_list:
        student_id_list.append(sid)

with open('student_id_list.csv', 'wb') as csvfile:
    spamwriter = csv.writer(csvfile, delimiter=',',
                            quotechar='|', quoting=csv.QUOTE_MINIMAL)
    spamwriter.writerow(student_id_list)
