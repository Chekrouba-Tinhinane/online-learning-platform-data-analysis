
import unicodecsv
from datetime import datetime as dt
import seaborn as sns
import numpy as np
from collections import defaultdict
import matplotlib.pyplot as plt

def read_csv(filename):
    with open(filename, 'rb') as f:
        csv_reader = unicodecsv.DictReader(f)
        return list(csv_reader)

def datetime_type(strr):
    if strr == '':
        return None
    else:
        return dt.strptime(strr, '%Y-%m-%d')

def int_paresing(strr):
    if strr == '':
        return None
    else:
        return int(strr)

def enrollments_type_fixing(my_list):
    for item in my_list:
        item['account_key'] = int_paresing(item['account_key'])
        item['join_date'] = datetime_type(item['join_date'])
        item['cancel_date'] = datetime_type(item['cancel_date'])
        item['days_to_cancel'] = int_paresing(item['days_to_cancel'])
        item['is_canceled'] = item['is_canceled'] == "True"
        item['is_udacity'] = item['is_udacity'] == "True"
    return my_list

def daily_engagement_type_fixing(my_list):
    for item in my_list:
        item['acct'] = int_paresing(item['acct'])
        item['utc_date'] = datetime_type(item['utc_date'])
        item['num_courses_visited'] = int(float(item['num_courses_visited']))
        item['total_minutes_visited'] = float(item['total_minutes_visited'])
        item['lessons_completed'] = int(float(item['lessons_completed']))
        item['projects_completed'] = int(float(item['projects_completed']))
    return my_list

def project_submissions_type_fixing(my_list):
    for item in my_list:
        item['creation_date'] = datetime_type(item['creation_date'])
        item['completion_date'] = datetime_type(item['completion_date'])
        item['account_key'] = int_paresing(item['account_key'])
        item['lesson_key'] = int_paresing(item['lesson_key'])
    return my_list

def remove_udacity_accounts(my_list, udacity_accounts_keys):
    non_udacity_dictt = []
    for dictt in my_list:
        if dictt['account_key'] not in udacity_accounts_keys:
            non_udacity_dictt.append(dictt)
    return non_udacity_dictt

def paid_students_dict(enrollment_list):
    paid_students = {}
    for dictt in enrollment_list:
        if dictt['days_to_cancel'] is None and dictt['is_canceled'] == False:
            if dictt['account_key'] not in paid_students or dictt['join_date'] < paid_students[dictt['account_key']]:
                paid_students[dictt['account_key']] = dictt['join_date']
        elif dictt['days_to_cancel'] > 7:
            if dictt['account_key'] not in paid_students or dictt['join_date'] < paid_students[dictt['account_key']]:
                paid_students[dictt['account_key']] = dictt['join_date']
    return paid_students

def within_one_week_test(join_date, engagement_date):
    days_inbetween = engagement_date - join_date
    return days_inbetween.days < 7 and days_inbetween.days >= 0

def remove_free_trial_cancels(data, paid_students):
    new_data = []
    for item in data:
        if item['account_key'] in paid_students:
            new_data.append(item)
    return new_data

def group_data(data, key_name):
    grouped_data = defaultdict(list)
    for data_point in data:
        grouped_data[data_point[key_name]].append(data_point)
    return grouped_data

def sum_grouped_items(grouped_data, field_name):
    summed_data = {}
    for key, data_points in grouped_data.items():
        total = 0
        for data_point in data_points:
            total += data_point[field_name]
        summed_data[key] = total
    return summed_data

def visit_days_flags_by_account_number_of_visits(grouped_data, field_name):
    not_zero_flags = defaultdict(list)
    number_of_visits = {}
    for key, data_points in grouped_data.items():
        total = 0
        for data_point in data_points:
            if data_point[field_name] > 0:
                total = total + 1
                not_zero_flags[data_point['account_key']].append(1)
            elif data_point[field_name] == 0:
                not_zero_flags[data_point['account_key']].append(0)
        number_of_visits[key] = total
    return not_zero_flags, number_of_visits

def describe_data(data, data_title=None):
    if data_title is not None: 
        print(data_title, " :")
    data = list(data)
    print("arithmetic mean ", np.mean(data))
    print("standard deviation : ", np.std(data))
    print("minimum : ", np.min(data))
    print("maximum : ", np.max(data))
    print("\n")

def main():
    daily_engagement = read_csv('dataset/daily_engagement.csv')
    project_submissions = read_csv('dataset/project_submissions.csv')
    enrollments = read_csv('dataset/enrollments.csv')

    enrollments = enrollments_type_fixing(enrollments)
    daily_engagement = daily_engagement_type_fixing(daily_engagement)
    project_submissions = project_submissions_type_fixing(project_submissions)

    for item in daily_engagement:
        item['account_key'] = item.pop('acct')

    udacity_accounts_keys = set()
    for dictt in enrollments:
        if dictt['is_udacity']:
            udacity_accounts_keys.add(dictt['account_key'])

    enrollments = remove_udacity_accounts(enrollments, udacity_accounts_keys)
    daily_engagement = remove_udacity_accounts(daily_engagement, udacity_accounts_keys)
    project_submissions = remove_udacity_accounts(project_submissions, udacity_accounts_keys)

    paid_students = paid_students_dict(enrollments)

    paid_students_engagement_first_week_list = []
    for dictt in daily_engagement:
        account_key = dictt['account_key']
        join_date = paid_students[account_key]
        engagement_date = dictt['utc_date']
        if within_one_week_test(join_date, engagement_date):
            paid_students_engagement_first_week_list.append(dictt)

    engagement_by_account = group_data(paid_students_engagement_first_week_list, 'account_key')
    total_minutes_by_account = sum_grouped_items(engagement_by_account, 'total_minutes_visited')
    lessons_by_account = sum_grouped_items(engagement_by_account, 'lessons_completed')
    visiting_flags_by_account, number_of_visits_by_account = visit_days_flags_by_account_number_of_visits(engagement_by_account, 'num_courses_visited')

    describe_data(lessons_by_account.values(), "lessons_by_account.values stat")
    describe_data(total_minutes_by_account.values(), "total_minutes_by_account.values stat")
    describe_data(number_of_visits_by_account.values(), "number_of_visits.values stat")

    pass_subway_project_set = set()
    for data_point in project_submissions:
        if (data_point['lesson_key'] in [746169184, 3176718735] and
                (data_point['assigned_rating'] == 'PASSED' or data_point['assigned_rating'] == 'DISTINCTION')):
            pass_subway_project_set.add(data_point['account_key'])

    passing_engagements = [dictt for dictt in paid_students_engagement_first_week_list if dictt['account_key'] in pass_subway_project_set]
    non_passing_engagements = [dictt for dictt in paid_students_engagement_first_week_list if dictt['account_key'] not in pass_subway_project_set]

    engagement_by_passing_account = group_data(passing_engagements, 'account_key')
    total_minutes_by_passing_account = sum_grouped_items(engagement_by_passing_account, 'total_minutes_visited')
    lessons_by_passing_account = sum_grouped_items(engagement_by_passing_account, 'lessons_completed')
    visiting_flags_by_passing_account, number_of_visits_by_passing_account = visit_days_flags_by_account_number_of_visits(engagement_by_passing_account, 'num_courses_visited')

    describe_data(lessons_by_passing_account.values(), "lessons_by_passing_account.values stat")
    describe_data(total_minutes_by_passing_account.values(), "total_minutes_by_passing_account.values stat")
    describe_data(number_of_visits_by_passing_account.values(), "number_of_visits_by_passing_account.values stat")

    engagement_by_non_passing_account = group_data(non_passing_engagements, 'account_key')
    total_minutes_by_non_passing_account = sum_grouped_items(engagement_by_non_passing_account, 'total_minutes_visited')
    lessons_by_non_passing_account = sum_grouped_items(engagement_by_non_passing_account, 'lessons_completed')
    visiting_flags_by_non_passing_account, number_of_visits_by_non_passing_account = visit_days_flags_by_account_number_of_visits(engagement_by_non_passing_account, 'num_courses_visited')

    describe_data(lessons_by_non_passing_account.values(), "lessons_by_non_passing_account.values stat")
    describe_data(total_minutes_by_non_passing_account.values(), "total_minutes_by_non_passing_account.values stat")
    describe_data(number_of_visits_by_non_passing_account.values(), "number_of_visits_by_non_passing_account.values stat")

    data_title = "total_minutes_by_passing_account"
    data = list(total_minutes_by_passing_account.values())
    sns.histplot(data).set_title(data_title)
    plt.show()

    data_title = "total_minutes_by_non_passing_account"
    data = list(total_minutes_by_non_passing_account.values())
    sns.histplot(data).set_title(data_title)
    plt.show()

if __name__ == '__main__':
    main()

      
           
           
           
           
           
           
           
           
           
           
           
           
           
           
           
           
           
           
           
           
           
           
           
           
           
           
           
           
           