# # backend/django_app/tasks/workflow_tasks.py

# from .base import BaseTask
# from celery import shared_task, chain
# from typing import Dict, Any, List
# from django.conf import settings

# @shared_task(
#     bind=True,
#     base=BaseTask,
#     name='tasks.workflow_execute',
#     queue='workflow_tasks'
# )
# def execute_workflow(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
#     """Execute complete workflow"""
#     try:
#         workflow_id = task_data.get('workflow_id')
#         workflow_data = task_data.get('workflow_data')
        
#         # Create task chain based on workflow steps
#         task_chain = _create_task_chain(workflow_data['steps'])
        
#         # Execute the chain
#         result = task_chain.apply_async()
        
#         return {
#             'status': 'success',
#             'workflow_id': workflow_id,
#             'chain_id': result.id
#         }
        
#     except Exception as exc:
#         self.retry(exc=exc, countdown=60, max_retries=3)

# def _create_task_chain(steps: List[Dict[str, Any]]) -> chain:
#     """Create a chain of tasks from workflow steps"""
#     task_chain = []
    
#     for step in steps:
#         if step['type'] == 'ai_process':
#             task_chain.append(process_ai_request.s(step['config']))
#         elif step['type'] == 'webhook':
#             task_chain.append(process_webhook.s(step['config']))
#         elif step['type'] == 'transform':
#             task_chain.append(transform_data.s(step['config']))
            
#     return chain(*task_chain)

# @shared_task(
#     bind=True,
#     base=BaseTask,
#     name='tasks.workflow_step',
#     queue='workflow_tasks'
# )
# def execute_workflow_step(self, step_data: Dict[str, Any]) -> Dict[str, Any]:
#     """Execute individual workflow step"""
#     try:
#         step_type = step_data.get('type')
#         step_config = step_data.get('config')
        
#         # Execute step based on type
#         if step_type == 'ai_process':
#             return process_ai_request.delay(step_config)
#         elif step_type == 'webhook':
#             return process_webhook.delay(step_config)
#         elif step_type == 'transform':
#             return transform_data.delay(step_config)
#         else:
#             raise ValueError(f"Unknown step type: {step_type}")
            
#     except Exception as exc:
#         self.retry(exc=exc, countdown=60, max_retries=3)