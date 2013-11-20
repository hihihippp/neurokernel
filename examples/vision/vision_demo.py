#!/usr/bin/env python

"""
Vision system demo.

Notes
-----
Generate input file by running ./data/gen_vis_input.py
"""

import argparse
import itertools

import networkx as nx

import neurokernel.core as core
import neurokernel.base as base
import neurokernel.tools.graph as graph_tools

from neurokernel.LPU.lpu_parser import lpu_parser
from neurokernel.LPU.LPU_rev import LPU_rev
from neurokernel.LPU.LPU import LPU

parser = argparse.ArgumentParser()
parser.add_argument('--debug', default=False,
                    dest='debug', action='store_true',
                    help='Write connectivity structures and inter-LPU routed data in debug folder')
parser.add_argument('-l', '--log', default='none', type=str,
                    help='Log output to screen [file, screen, both, or none; default:none]')
parser.add_argument('-s', '--steps', default=10000, type=int,
                    help='Number of steps [default:10000]')
parser.add_argument('-d', '--data_port', default=5005, type=int,
                    help='Data port [default:5005]')
parser.add_argument('-c', '--ctrl_port', default=5006, type=int,
                    help='Control port [default:5006]')
parser.add_argument('-a', '--lam_dev', default=0, type=int,
                    help='GPU for lamina lobe [default:0]')
parser.add_argument('-m', '--med_dev', default=1, type=int,
                    help='GPU for medulla [default:1]')

args = parser.parse_args()

dt = 1e-4
dur = 1.0
Nt = int(dur/dt)

file_name = None
screen = False
if args.log.lower() in ['file', 'both']:
    file_name = 'neurokernel.log'
if args.log.lower() in ['screen', 'both']:
    screen = True    
logger = base.setup_logger(file_name, screen)

man = core.Manager(port_data=args.data_port, port_ctrl=args.ctrl_port)
man.add_brok()

(n_dict_lam, s_dict_lam) = lpu_parser('./data/lamina.gexf.gz')
lpu_lam = LPU(dt, n_dict_lam, s_dict_lam,
          input_file='./data/vision_input.h5',
          output_file='lamina_output.h5', port_ctrl= man.port_ctrl,
          port_data=man.port_data, device=args.lam_dev, id='lamina')
man.add_mod(lpu_lam)

(n_dict_med, s_dict_med) = lpu_parser('./data/medulla.gexf.gz')
lpu_med = LPU(dt, n_dict_med, s_dict_med,
          output_file='medulla_output.h5', port_ctrl= man.port_ctrl,
          port_data=man.port_data, device=args.med_dev, id='medulla')
man.add_mod(lpu_med)

g = nx.read_gexf('./data/lamina_medulla.gexf.gz', relabel=True)
conn_lam_med = graph_tools.graph_to_conn(g)
man.connect(lpu_lam, lpu_med, conn_lam_med)

man.start(steps=args.steps)
man.stop()