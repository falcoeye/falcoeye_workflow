from .utils import fill_args
from app.node import create_node_from_dict
import logging 
import threading

class Workflow:
    def __init__(self,analysis_id,nodes,starters,nodes_in_order):
        self._analysis_id = analysis_id
        self._nodes = nodes
        self._starters = starters
        self._nodes_in_order = nodes_in_order
        self._busy = False
    
    def run_sequentially(self):
        logging.info(f"Running {self._analysis_id} sequentially")
        self._busy = True
        for n in self._nodes_in_order:
            logging.info(f"Running {n._name}")
            n.run()
        logging.info(f"{self._analysis_id} completed")
        self._busy = False

    def run_sequentially_async(self):
        w_thread = threading.Thread(
                target=self.run_sequentially,
                args=(),
                daemon= True
            )    
        w_thread.start()

class WorkflowFactory:
    def __init__(self):
        pass

    @staticmethod
    def create_from_dict(workflow_structure,analysis):
        
        name = workflow_structure["name"]
        
        nodes_json = workflow_structure["nodes"]
        fill_args(nodes_json,analysis["args"])
        nodes = {}
        for n in nodes_json:
            logging.info(f"creating node {n}")
            nodes[n["name"]] = create_node_from_dict(n)
        logging.info(nodes)

        edgelist = workflow_structure["edges"]
        for f,t in edgelist:
            nodes[f].add_sink(nodes[t])
        
        starterslist = workflow_structure["starters"]
        starters = [nodes[s] for s in starterslist]
    
        run_order = workflow_structure["run_order"]
        nodes_in_order = [nodes[n] for n in run_order]
        
        w = Workflow(analysis["id"],nodes,starters,nodes_in_order)

        return w