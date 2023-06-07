import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import time
from pylsl import resolve_byprop, StreamInlet
import math

wait_time = 0.04
scale = 150
x, y, y1, y2, y3 = [], [], [], [], []


def setup_gui():
    global scale
    st.title('XHRO LSL Viewer')
    selected_type = st.sidebar.selectbox('Type', ('ACC', 'BIOZ', 'EEG', 'OPT', 'TEMP'))
    scale = st.sidebar.number_input('Scale', min_value=0, max_value=15000, step=1, value=150)
    selected_filter = st.sidebar.selectbox('filter', ('Nofilter','BP2-30Hz', 'BP2-45Hz','BP5-45Hz','BP15-45Hz','BP7-13Hz'))
    ave_ref = st.sidebar.checkbox('Ave Ref')
    norm = st.sidebar.checkbox('Norm.')
    streams = resolve_stream(selected_type)

def resolve_stream(selected_type):
    global wait_time
    type_mapping = {
        'ACC': ('ACC',0.04),
        'BIOZ': ('BIOZ',60),
        'EEG': ('EEG',0.004),
        'OPT': ('OPT',0.02),
        'TEMP': ('TEMP',1)
    }
    stream_type,stream_time = type_mapping.get(selected_type, None)
    if stream_type:
        wait_time = stream_time
        if stream_type == 'ACC':
            setup_accgraph()
        elif stream_type == 'BIOZ':
            setup_biozgraph()
        elif stream_type == 'EEG':
            setup_eeggraph()
        elif stream_type == 'OPT':
            setup_optgraph()
        elif stream_type == 'TEMP':
            setup_tempgraph()
    
def convert_acc(y):
    converted = y * 6.1035 * 10**-2
    converted = math.floor(converted * 100) / 100
    return converted
def convert_bioz(y):
    converted = y * 180 // math.pi
    converted = math.floor(converted * 100) / 100
    return converted
def convert_eeg(y):
    converted = y * ((2*4.5 // 24) // 0x1000000) * 1000 * 1000
    converted = math.floor(converted * 100) / 100
    return converted
def convert_opt(y):
    y = math.floor(y * 100) / 100
    return y
def convert_temp(y):
    converted = y
    converted = math.floor(converted * 1000) / 1000
    return converted



def setup_graph(streams):
    if len(streams) > 0:
        inlet = StreamInlet(streams[0])
        graph = st.empty()
        fig, (ax,ax1) = plt.subplots(nrows=2,sharex=True)
        i = 0
        while True:
            update(i, graph, inlet, fig, ax, ax1)
            i += 1

def setup_accgraph():
    streams = resolve_byprop('type', 'ACC', timeout=2)
    if len(streams) > 0:
        inlet = StreamInlet(streams[0])
        graph = st.empty()
        fig, (ax2,ax1,ax) = plt.subplots(nrows=3,sharex=True)
        ax2.spines['bottom'].set_visible(False)
        ax1.spines['top'].set_visible(False)
        ax1.spines['bottom'].set_visible(False)
        ax.spines['top'].set_visible(False)
        plt.subplots_adjust(hspace=0)
        i = 0
        while True:
            update_acc(i, graph, inlet, fig, ax, ax1, ax2)
            i += 1
def setup_eeggraph():
    streams = resolve_byprop('type', 'EEG', timeout=2)
    if len(streams) > 0:
        inlet = StreamInlet(streams[0])
        graph = st.empty()
        fig, (ax1,ax) = plt.subplots(nrows=2,sharex=True)
        ax1.spines['bottom'].set_visible(False)
        ax.spines['top'].set_visible(False)
        plt.subplots_adjust(hspace=0)
        i = 0
        while True:
            update_eeg(i, graph, inlet, fig, ax, ax1)
            i += 1
def setup_biozgraph():
    streams = resolve_byprop('type', 'BIOZ', timeout=2)
    if len(streams) > 0:
        inlet = StreamInlet(streams[0])
        graph = st.empty()
        fig, (ax1,ax) = plt.subplots(nrows=2,sharex=True)
        ax1.spines['bottom'].set_visible(False)
        ax.spines['top'].set_visible(False)
        plt.subplots_adjust(hspace=0)
        i = 0
        while True:
            update_bioz(i, graph, inlet, fig, ax, ax1)
            i += 1
def setup_optgraph():
    streams = resolve_byprop('type', 'OPT', timeout=2)
    if len(streams) > 0:
        inlet = StreamInlet(streams[0])
        graph = st.empty()
        fig, (ax3,ax2,ax1,ax) = plt.subplots(nrows=4,sharex=True)
        ax3.spines['bottom'].set_visible(False)
        ax2.spines['top'].set_visible(False)
        ax2.spines['bottom'].set_visible(False)
        ax1.spines['top'].set_visible(False)
        ax1.spines['bottom'].set_visible(False)
        ax.spines['top'].set_visible(False)
        plt.subplots_adjust(hspace=0)
        i = 0
        while True:
            update_opt(i, graph, inlet, fig, ax, ax1, ax2, ax3)
            i += 1
def setup_tempgraph():
    streams = resolve_byprop('type', 'TEMP', timeout=2)
    if len(streams) > 0:
        inlet = StreamInlet(streams[0])
        graph = st.empty()
        fig, (ax) = plt.subplots(nrows=1,sharex=True)
        i = 0
        while True:
            update_temp(i, graph, inlet, fig, ax)
            i += 1

# アニメーションのフレーム更新関数
def update(i, graph, inlet, fig, ax, ax1):
    sample, timestamp = inlet.pull_sample()
    x.append(i*wait_time)
    y.append(sample[0])
    if len(sample) > 1:
        y1.append(sample[1])

    if x[-1] > 10:
        del x[0]
        del y[0]
        if len(sample) > 1:
            del y1[0]

    if x[-1] % 1 == 0:
        ax.cla()
        ax.set_xlim(x[-1]-10, x[-1])
        ax.plot(x, y)
        if len(sample) > 1:
            ax1.cla()
            ax1.set_xlim(x[-1]-10, x[-1])
            ax1.plot(x, y1)
        graph.pyplot(fig)

    
    time.sleep(wait_time)

def update_acc(i, graph, inlet, fig, ax, ax1, ax2):
    sample, timestamp = inlet.pull_sample()
    x.append(i*wait_time)
    y.append(convert_acc(sample[0]))
    y1.append(convert_acc(sample[1]))
    y2.append(convert_acc(sample[2]))

    if x[-1] > 10:
        del x[0]
        del y[0]
        del y1[0]
        del y2[0]

    if x[-1] % 1 == 0:
        ax.cla()
        ax.set_xlim(x[-1]-10, x[-1])
        tick_positions = [np.mean(y)]
        ax.set_ylim(np.mean(y) - scale/2, np.mean(y) + scale/2)
        ax.set_yticks(tick_positions)
        ax.yaxis.tick_right()
        ax.set_ylabel('ch1')
        ax.plot(x, y)
        ax1.cla()
        ax1.set_xlim(x[-1]-10, x[-1])
        ax1.set_ylim(np.mean(y1) - scale/2, np.mean(y1) + scale/2)
        ax1.yaxis.tick_right()
        ax1.set_ylabel('ch2')
        ax1.plot(x, y1)
        ax2.cla()
        ax2.set_xlim(x[-1]-10, x[-1])
        ax2.set_ylim(np.mean(y2) - scale/2, np.mean(y2) + scale/2)
        ax2.yaxis.tick_right()
        ax2.set_ylabel('ch3')
        ax2.plot(x, y2)
        graph.pyplot(fig)
    
    time.sleep(wait_time)
def update_eeg(i, graph, inlet, fig, ax, ax1):
    sample, timestamp = inlet.pull_sample()
    x.append(i*wait_time)
    y.append(convert_eeg(sample[0]))
    y1.append(convert_eeg(sample[1]))

    if x[-1] > 10:
        del x[0]
        del y[0]
        del y1[0]

    if x[-1] % 1 == 0:
        ax.cla()
        ax.set_xlim(x[-1]-10, x[-1])
        ax.set_ylim(np.mean(y) - scale/2, np.mean(y) + scale/2)
        ax.yaxis.tick_right()
        ax.set_ylabel('ch1')
        ax.plot(x, y)
        ax1.cla()
        ax1.set_xlim(x[-1]-10, x[-1])
        ax1.set_ylim(np.mean(y1) - scale/2, np.mean(y1) + scale/2)
        ax1.yaxis.tick_right()
        ax1.set_ylabel('ch2')
        ax1.plot(x, y1)
        graph.pyplot(fig)
    
    time.sleep(wait_time)
def update_bioz(i, graph, inlet, fig, ax, ax1):
    sample, timestamp = inlet.pull_sample()
    x.append(i*wait_time)
    y.append(convert_bioz(sample[0]))
    y1.append(convert_bioz(sample[1]))

    if x[-1] > 10:
        del x[0]
        del y[0]
        del y1[0]

    if x[-1] % 1 == 0:
        ax.cla()
        ax.set_xlim(x[-1]-10, x[-1])
        ax.set_ylim(np.mean(y) - scale/2, np.mean(y) + scale/2)
        ax.yaxis.tick_right()
        ax.set_ylabel('ch1')
        ax.plot(x, y)
        ax1.cla()
        ax1.set_xlim(x[-1]-10, x[-1])
        ax1.set_ylim(np.mean(y1) - scale/2, np.mean(y1) + scale/2)
        ax1.yaxis.tick_right()
        ax1.set_ylabel('ch2')
        ax1.plot(x, y1)
        graph.pyplot(fig)
    
    time.sleep(wait_time)
def update_opt(i, graph, inlet, fig, ax, ax1, ax2, ax3):
    sample, timestamp = inlet.pull_sample()
    x.append(i*wait_time)
    y.append(convert_opt(sample[0]))
    y1.append(convert_opt(sample[1]))
    y2.append(convert_opt(sample[2]))
    y3.append(convert_opt(sample[3]))

    if x[-1] > 10:
        del x[0]
        del y[0]
        del y1[0]
        del y2[0]
        del y3[0]

    if x[-1] % 1 == 0:
        ax.cla()
        ax.set_xlim(x[-1]-10, x[-1])
        ax.set_ylim(np.mean(y) - scale/2, np.mean(y) + scale/2)
        ax.yaxis.tick_right()
        ax.set_ylabel('ch1')
        ax.plot(x, y)
        ax1.cla()
        ax1.set_xlim(x[-1]-10, x[-1])
        ax1.set_ylim(np.mean(y1) - scale/2, np.mean(y1) + scale/2)
        ax1.yaxis.tick_right()
        ax1.set_ylabel('ch2')
        ax1.plot(x, y1)
        ax2.cla()
        ax2.set_xlim(x[-1]-10, x[-1])
        ax2.set_ylim(np.mean(y2) - scale/2, np.mean(y2) + scale/2)
        ax2.yaxis.tick_right()
        ax2.set_ylabel('ch3')
        ax2.plot(x, y2)
        ax3.cla()
        ax3.set_xlim(x[-1]-10, x[-1])
        ax3.set_ylim(np.mean(y3) - scale/2, np.mean(y3) + scale/2)
        ax3.yaxis.tick_right()
        ax3.set_ylabel('ch4')
        ax3.plot(x, y3)
        graph.pyplot(fig)
    
    time.sleep(wait_time)
def update_temp(i, graph, inlet, fig, ax):
    sample, timestamp = inlet.pull_sample()
    x.append(i*wait_time)
    y.append(convert_temp(sample[0]))

    if x[-1] > 10:
        del x[0]
        del y[0]

    if x[-1] % 1 == 0:
        ax.cla()
        ax.set_xlim(x[-1]-10, x[-1])
        tick_positions = [np.mean(y)]
        ax.set_ylim(np.mean(y) - scale/2, np.mean(y) + scale/2)
        ax.set_yticks(tick_positions)
        ax.yaxis.tick_right()
        ax.set_ylabel('ch1')
        ax.plot(x, y)
        graph.pyplot(fig)
    
    time.sleep(wait_time)

def main():
    setup_gui()

if __name__ == '__main__':
    main()
