
import unittest

import mdp
from mdp import numx as n
import mdp.parallel as parallel
import mdp.hinet as hinet
from mdp import numx as n

import testing_tools


class TestParallelFlowNode(unittest.TestCase):
    """Tests for ParallelFlowNode."""

    def test_flownode(self):
        """Test ParallelFlowNode."""
        flow = mdp.Flow([parallel.ParallelSFANode(output_dim=5),
                         mdp.nodes.PolynomialExpansionNode(degree=2),
                         parallel.ParallelSFANode(output_dim=3)])
        flownode = parallel.ParallelFlowNode(flow)
        x = n.random.random([100,50])
        chunksize = 25
        chunks = [x[i*chunksize : (i+1)*chunksize] 
                    for i in range(len(x)/chunksize)]
        while flownode.get_remaining_train_phase() > 0:
            for chunk in chunks:
                forked_node = flownode.fork()
                forked_node.train(chunk)
                flownode.join(forked_node)
            flownode.stop_training()
        # test execution
        flownode.execute(x)
        
    def test_parallelnet(self):
        """Test a simple parallel net with big data. 
        
        Includes ParallelFlowNode, ParallelCloneLayer, ParallelSFANode
        and training via a ParallelFlow.
        """
        noisenode = mdp.nodes.NormalNoiseNode(input_dim=20*20, 
                                              noise_args=(0,0.0001))
        sfa_node = parallel.ParallelSFANode(input_dim=20*20, output_dim=10)
        switchboard = hinet.Rectangular2dSwitchboard(x_in_channels=100, 
                                                     y_in_channels=100, 
                                                     x_field_channels=20, 
                                                     y_field_channels=20,
                                                     x_field_spacing=10, 
                                                     y_field_spacing=10)
        flownode = parallel.ParallelFlowNode(mdp.Flow([noisenode, sfa_node]))
        sfa_layer = parallel.ParallelCloneLayer(flownode, 
                                                switchboard.output_channels)
        flow = parallel.ParallelFlow([switchboard, sfa_layer])
        data_iterables = [None,
                          [n.random.random((10, 100*100)) for _ in range(3)]]
        scheduler = parallel.Scheduler()
        flow.train(data_iterables, scheduler=scheduler)
        
    def test_makeparallel(self):
        """Test make_flow_parallel and unmake_flow_parallel for a hinet."""
        sfa_node = mdp.nodes.SFANode(input_dim=20*20, output_dim=10)
        switchboard = hinet.Rectangular2dSwitchboard(x_in_channels=100, 
                                                     y_in_channels=100, 
                                                     x_field_channels=20, 
                                                     y_field_channels=20,
                                                     x_field_spacing=10, 
                                                     y_field_spacing=10)
        flownode = hinet.FlowNode(mdp.Flow([sfa_node]))
        sfa_layer = hinet.CloneLayer(flownode, switchboard.output_channels)
        flow = mdp.Flow([switchboard, sfa_layer])
        data_iterables = [None,
                          [n.random.random((50, 100*100)) for _ in range(3)]]
        parallel_flow = parallel.make_flow_parallel(flow)
        scheduler = parallel.Scheduler()
        parallel_flow.train(data_iterables, scheduler=scheduler)
        flow.train(data_iterables)
        reconstructed_flow = parallel.unmake_flow_parallel(parallel_flow)
        x = mdp.numx.random.random((10, flow[0].input_dim))
        y1 = abs(flow.execute(x))
        y2 = abs(reconstructed_flow.execute(x))
        testing_tools.assert_array_almost_equal(y1, y2)
        
        
class TestParallelLayer(unittest.TestCase):
    """Tests for TestParallelLayer."""

    def test_layer(self):
        """Test Simple random test with three nodes."""
        node1 = parallel.ParallelSFANode(input_dim=10, output_dim=5)
        node2 = parallel.ParallelSFANode(input_dim=17, output_dim=3)
        node3 = parallel.ParallelSFANode(input_dim=3, output_dim=1)
        layer = parallel.ParallelLayer([node1, node2, node3])
        flow = parallel.ParallelFlow([layer])
        data_iterables = [[n.random.random((10, 30)) for _ in range(3)]]
        scheduler = parallel.Scheduler()
        flow.train(data_iterables, scheduler=scheduler)


def get_suite(testname=None):
    # this suite just ignores the testname argument
    # you can't select tests by name here!
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestParallelFlowNode))
    suite.addTest(unittest.makeSuite(TestParallelLayer))
    return suite
            
if __name__ == '__main__':
    unittest.main() 