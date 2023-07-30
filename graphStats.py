from collections import defaultdict
from time import gmtime
from time import strftime

def generateClimbGraph(climb_file):
    v_success = defaultdict(int)
    v_attempts = defaultdict(int)
    max_v = 0
    for climb in climb_file['grades']:
        if climb['grade'] > max_v:
            max_v = climb['grade']

        if climb['status'] == 'Completed':
            v_success[climb['grade']] += 1
        else:
            v_attempts[climb['grade']] += 1
    labels = ['V' + str(i) for i in range(max_v+1)]
    success_data = [v_success[i] for i in range(max_v+1)]
    attempts_data = [v_attempts[i] for i in range(max_v+1)]
    return labels, success_data, attempts_data

def generateTimelineGraph(climb_file):
    timeline_datasets = []
    for climb in climb_file['grades']:
        success = climb['status'] == 'Completed'
        dataset = {
            'label': f"V{climb['grade']} " + ('success' if success else 'attempt'),
            'data': [climb['time']],
            'backgroundColor': 'rgba(104, 255, 0, 0.5)' if success else 'rgba(226, 96, 96, 0.5)',
            'borderColor': 'black',
            'borderWidth': {
            'bottom': 0,
            'top': 0,
            'left': 3,
            'right': 3
            }
        }
        
        timeline_datasets.append(dataset)
    return timeline_datasets


def generateCardData(climb_file):
    highest_grade = {True:-1, False:-1}
    total_time = {True: 0, False: 0}
    num_climbs = {True: 0, False: 0}
    total_grade = {True:0, False:0}
    total_hr = {True:0, False:0}

    for climb in climb_file['grades']:
        success = climb['status'] == 'Completed'
        total_time[success] += climb['time']
        num_climbs[success] += 1
        total_grade[success] += climb['grade']
        total_hr[success] += climb['hr_avg']
        if climb['grade'] > highest_grade[success]:
            highest_grade[success] = climb['grade']
    
    total_climbs =  sum(num_climbs.values())
    climb_stats = {
        'avg_hr': round(sum(total_hr.values()) / total_climbs, 1),
        'avg_time': strftime("%M:%S", gmtime(round(sum(total_time.values()) / total_climbs))),
        'total_time': strftime("%M:%S", gmtime(round(sum(total_time.values())))),
        'avg_grade': round(sum(total_grade.values()) / total_climbs),
        'highest_grade': max(highest_grade.values()),
        'avg_s_hr': round(total_hr[True] / num_climbs[True], 1),
        'avg_s_time': strftime("%M:%S", gmtime(round(total_time[True] / num_climbs[True]))),
        'total_s_time': strftime("%M:%S", gmtime(round(total_time[True]))),
        'avg_s_grade': round(total_grade[True] / num_climbs[True]),
        'highest_s_grade': highest_grade[True],
        'avg_a_hr': round(total_hr[False] / num_climbs[False], 1),
        'avg_a_time': strftime("%M:%S", gmtime(round(total_time[False] / num_climbs[False]))),
        'total_a_time': strftime("%M:%S", gmtime(round(total_time[False]))),
        'avg_a_grade': round(total_grade[False] / num_climbs[False]),
        'highest_a_grade': highest_grade[False]
    }
    return climb_stats


        