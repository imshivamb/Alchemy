from typing import Dict, Any, List, Optional
from datetime import datetime
from ..base import BaseRedis
from ..exceptions import StateError

class WorkflowStateManager(BaseRedis):
    """
    Manages workflow execution state with history tracking
    """
    def __init__(self):
        super().__init__()
        self.state_prefix = "workflow_state:"
        self.history_prefix = "workflow_history:"
        
    async def save_workflow_state(self, workflow_id: str, state: Dict[str, Any], expires: Optional[int] = None):
        """
        Save workflow state with versioning and history
        """
        try:
            key = f"{self.state_prefix}{workflow_id}"
            
            # Add metadata
            state.update({
                'updated_at': datetime.utcnow().isoformat(),
                'version': await self._get_next_version(workflow_id)
            })
            
            # Save current state
            await self.set_data(key, state, expires=expires)
            
            #Add to History
            await self.push_to_queue(
                f"{self.history_prefix}{workflow_id}",
                {**state, 'timestamp': datetime.utcnow().isoformat()}
            )
            
            # Publish update event
            await self.publish('workflow_events', {
                'type': 'state_updated',
                'workflow_id': workflow_id,
                'state': state
            })
            
        except Exception as e:
            raise StateError(f"Failed to save workflow state: {str(e)}")
        