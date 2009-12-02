"""
Test the inspection of a normal (non-bi) Flow with the BiNet inspection.

Since this requires the creation of files and opens them in a browser this
should not be included in the unittests.
"""

import numpy

import mdp
import binet

# create the flow
noisenode = mdp.nodes.NormalNoiseNode(input_dim=20*20, 
                                      noise_args=(0, 0.0001))
sfa_node = mdp.nodes.SFANode(input_dim=20*20, output_dim=10, dtype='f')
switchboard = mdp.hinet.Rectangular2dSwitchboard(
                                          x_in_channels=100, 
                                          y_in_channels=100,
                                          x_field_channels=20, 
                                          y_field_channels=20,
                                          x_field_spacing=10, 
                                          y_field_spacing=10)
flownode = mdp.hinet.FlowNode(mdp.Flow([noisenode, sfa_node]))
sfa_layer = mdp.hinet.CloneLayer(flownode, switchboard.output_channels)
flow = mdp.Flow([switchboard, sfa_layer])

train_data = [numpy.cast['f'](numpy.random.random((10, 100*100)))
              for _ in range(5)]

# do the inspection, open in browser
binet.show_training(flow=flow, data_iterables=[None, train_data])
filename, out = binet.show_execution(flow, x=train_data[0])
print "done."
