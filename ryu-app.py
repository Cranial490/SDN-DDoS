from operator import attrgetter
import os
import simple_switch_13
from ryu.controller import ofp_event
from ryu.controller.handler import MAIN_DISPATCHER, DEAD_DISPATCHER
from ryu.controller.handler import set_ev_cls
from ryu.lib import hub
import Model_ML

class L2Switch(simple_switch_13.SimpleSwitch13):
    def __init__(self, *args, **kwargs):
        super(L2Switch, self).__init__(*args, **kwargs)
        self.datapaths = {}
        self.monitor_thread = hub.spawn(self._monitor)
        self.flow_count =[0,0]
        self.packet_count = [0,0]
        self.byte_count = [0,0]

        #Stores previous state (flow_count, byte_count, packet_count)
        self.datadict = {}

    def get_diff(self,state, prev_state):
        bc = abs(state[0])-abs(prev_state[0])
        pc = abs(state[1])-abs(prev_state[1])
        print(abs(state[0]),abs(prev_state[0]),abs(state[1]),abs(prev_state[1]))
        return bc,pc

    def get_ratio(self,state, prev_state):
        bc ,pc= self.get_diff(state, prev_state)
        fc = self.flow_count[1]-self.flow_count[0]
        if fc:
            bcfc = bc/fc
            pcfc = pc/fc
        else:
            return bc, pc
        return bcfc, pcfc

    #Use only when generating data for test
    def store_data(self, filename,row):
        import csv
        # open the file in the write mode
        path = './'+filename
        with open(path, 'a') as f:
            writer = csv.writer(f)
            writer.writerow(row)

    @set_ev_cls(ofp_event.EventOFPStateChange,
                [MAIN_DISPATCHER, DEAD_DISPATCHER])
    def _state_change_handler(self, ev):
        datapath = ev.datapath
        if ev.state == MAIN_DISPATCHER:
            if datapath.id not in self.datapaths:
                self.logger.debug('register datapath: %016x', datapath.id)
                self.datapaths[datapath.id] = datapath
        elif ev.state == DEAD_DISPATCHER:
            if datapath.id in self.datapaths:
                self.logger.debug('unregister datapath: %016x', datapath.id)
                del self.datapaths[datapath.id]

    def _monitor(self):
        dplen = len(self.datapaths.values())
        while True:
            for dp in self.datapaths.values():
                self._request_stats(dp)
            hub.sleep(1)  

    def _request_stats(self, datapath):
        # self.logger.debug('send stats request: %016x', datapath.id)
        parser = datapath.ofproto_parser

        req = parser.OFPFlowStatsRequest(datapath)
        datapath.send_msg(req)
        hub.sleep(1)

    @set_ev_cls(ofp_event.EventOFPFlowStatsReply, MAIN_DISPATCHER)
    def _flow_stats_reply_handler(self, ev):
        body = ev.msg.body
        self.flow_count[0] = self.flow_count[1]
        self.flow_count[1] = len(body)
        self.packet_count[0] = self.packet_count[1]
        fc = self.flow_count[1] - self.flow_count[0]
        # print("Flow count chage", fc)
        for stat in sorted([flow for flow in body if flow.priority == 1],
                           key=lambda flow: (flow.match['in_port'],
                                             flow.match['eth_dst'])):

            if ev.msg.datapath.id in self.datadict:
                prev_state = self.datadict[ev.msg.datapath.id]
                new_state = (stat.packet_count, stat.byte_count)
                self.datadict[ev.msg.datapath.id] = new_state
                bc,pc = self.get_diff(new_state, prev_state)
                bcfc, pcfc = self.get_ratio(new_state,prev_state)
                #id, flow_count, fc_diff, bc_diff, pc_diff, bcfc, pcfc, isAttack     
                data = [fc,bc,pc,bcfc,pcfc]
                prediction = Model_ML.check_DDoS(data)
                if prediction:
                    out = "Attack Detected"
                else:
                    out = "Normal"
                
                self.store_data("output.csv",[out])
            else:
                new_state = (stat.packet_count, stat.byte_count)
                self.datadict[ev.msg.datapath.id] = new_state