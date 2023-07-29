from collections import defaultdict

def generateClimbGraph(climb_file):
    v_success = defaultdict(lambda: int())
    v_attempts = defaultdict(lambda: int())
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
            