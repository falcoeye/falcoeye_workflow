from .utils import fill_args
from app.node import create_node_from_dict,Source
import logging 
import threading
from flask import current_app

class Workflow:
    def __init__(self,analysis_id,nodes,starters,nodes_in_order):
        self._analysis_id = analysis_id
        self._nodes = nodes
        self._starters = starters
        self._nodes_in_order = nodes_in_order
        self._busy = False
        self._tasks = {}
    
    def run_sequentially(self):
        logging.info(f"Running {self._analysis_id} sequentially")
        self._busy = True
        for n in self._nodes_in_order:
            logging.info(f"Running {n._name}")
            n.run()
        logging.info(f"{self._analysis_id} completed")
        self._busy = False

    def run_sequentially_async(self):
        logging.info(f"Running {self._analysis_id} asynchronously")
        self._busy = True
        self._tasks = {}
        for n in self._nodes_in_order:
            print(n.name)
            self._tasks[n.name] = True
            logging.info(f"Running {n._name}")   
            n.run_async(self.done_task_callback,self.error_task_callback)

        logging.info(f"{self._analysis_id} completed")

    def done_task_callback(self,task):
        logging.info(f"Received done callback from {task}")
        self._tasks[task] = False
        if all(self._tasks.values()):
            # TODO update db
            pass
    
    def error_task_callback(self,task,error):
        logging.error(error)

    def status(self):
        return self._tasks


class WorkflowFactory:
    def __init__(self):
        pass

    @staticmethod
    def create_from_dict(workflow_structure,analysis):    
        # Getting nodes dictionary
        nodes_json = workflow_structure["nodes"]
        # Creating dict to escape for loop in fill args
        workflow_args = {n["name"]: n for n in workflow_structure["args"]}
        # replace workflow placeholders with user inputs
        fill_args(nodes_json,workflow_args,analysis["args"])

        # This is important for output nodes
        nodes = {}
        for n in nodes_json:
            logging.info(f"creating node {n}")
            if "nodes" in n:
                n["nodes"] = [nodes[i] for i in n["nodes"]]
            elif "node" in n:
                n["node"] = nodes[n["node"]]
            nodes[n["name"]] = create_node_from_dict(n)
            # to avoid RuntimeError: working outside of request context
            # when running asynchronously 
            nodes[n["name"]].set_context(current_app._get_current_object())
        
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