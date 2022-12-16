#state (flow_count, byte_count, packet_count)

def get_diff(state, prev_state):
    return (state[0]-prev_state[0]),(state[1]-prev_state[1]),(state[2]-prev_state[2])

def get_ratio(state, prev_state):
    bcfc = (state[1]-prev_state[1])/(state[0]-prev_state[0])
    pcfc = (state[2]-prev_state[2])/(state[0]-prev_state[0])
    return bcfc, pcfc