from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from enum import Enum
from redis_service.state.workflow_state_manager import WorkflowStateManager
from redis_service.tracking.activity_tracker import ActivityTracker
import logging
import traceback

logger = logging.getLogger(__name__)

class ErrorSeverity(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"
    
class ErrorType(Enum):
    VALIDATION = "validation"
    PROCESSING = "processing"
    INTEGRATION = "integration"
    SYSTEM = "system"
    TIMEOUT = "timeout"
    
class WorkflowErrorHandler:
    """
    Handles workflow execution errors with recovery options
    """
    
    def __init__(self):
        self.state_manager = WorkflowStateManager()
        self.activity_tracker = ActivityTracker()
        
        # Retry configurations based on error type
        self.retry_configs = {
            ErrorType.VALIDATION: {"max_retries": 0, "delay": 0},
            ErrorType.PROCESSING: {"max_retries": 3, "delay": 300},
            ErrorType.INTEGRATION: {"max_retries": 5, "delay": 600},
            ErrorType.SYSTEM: {"max_retries": 2, "delay": 1800},
            ErrorType.TIMEOUT: {"max_retries": 3, "delay": 900}
        }
    
    async def handle_error(
        self,
        workflow_id: str,
        error: Exception,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Handle workflow errors with proper recovery strategy
        """
        try:
            #Classify Error
            error_type, severity = self._classify_error(error)
            
            # Log error
            await self._log_error(workflow_id, error, error_type, severity, context)
            
            #Determin Recovery strategy
            recovery_strategy = await self._determine_recovery_strategy(error_type, severity, workflow_id, context)
            
             # Execute recovery
            recovery_result = await self._execute_recovery_strategy(
                workflow_id, recovery_strategy, context
            )
            
            return {
                'error_handled': True,
                'recovery_strategy': recovery_strategy,
                'recovery_result': recovery_result
            }
            
        except Exception as e:
            logger.critical(
                f"Error handler failed for workflow {workflow_id}: {str(e)}",
                exc_info=True
            )
            raise
        
    async def _log_error(
        self,
        workflow_id: str,
        error: Exception,
        error_type: ErrorType,
        severity: ErrorSeverity,
        context: Dict[str, Any]
    ):
        """
        Log error details for monitoring and debugging
        """
        error_data = {
            'workflow_id': workflow_id,
            'error_type': error_type.value,
            'severity': severity.value,
            'error_message': str(error),
            'stacktrace': traceback.format_exc(),
            'context': context,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        # Track error in activity tracker
        await self.activity_tracker.track_activity(
            'workflow_error',
            context.get('user_id'),
            error_data
        )
        
        # Log based on severity
        if severity in [ErrorSeverity.HIGH, ErrorSeverity.CRITICAL]:
            logger.error(
                f"Critical workflow error: {str(error)}",
                extra=error_data,
                exc_info=True
            )
        else:
            logger.warning(
                f"Workflow error: {str(error)}",
                extra=error_data
            )
            
    async def _determine_recovery_strategy(
        self,
        workflow_id: str,
        error_type: ErrorType,
        severity: ErrorSeverity,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Determine appropriate recovery strategy based on error type and severity
        """
        retry_config = self.retry_configs[error_type]
        current_retries = context.get('retries', 0)
        
        if current_retries >= retry_config['max_retries']:
            return {
                'action': 'fail',
                'reason': 'max_retries_exceeded'
            }
            
        # Get workflow state
        workflow_state = await self.state_manager.get_workflow_state(workflow_id)
        
        # Determine strategy based on error type and state
        if error_type == ErrorType.VALIDATION:
            return {
                'action': 'fail',
                'reason': 'validation_error'
            }
        elif error_type == ErrorType.INTEGRATION:
            return {
                'action': 'retry',
                'delay': retry_config['delay'],
                'cleanup_required': False
            }
        elif error_type == ErrorType.SYSTEM:
            return {
                'action': 'retry',
                'delay': retry_config['delay'],
                'cleanup_required': True
            }
        else:
            return {
                'action': 'retry',
                'delay': retry_config['delay'],
                'cleanup_required': False
            }
            
    async def _execute_recovery_strategy(
        self,
        workflow_id: str,
        strategy: Dict[str, Any],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Execute the determined recovery strategy
        """
        if strategy['action'] == 'fail':
            await self._handle_failure(workflow_id, strategy, context)
            return {'status': 'failed', 'reason': strategy['reason']}
            
        elif strategy['action'] == 'retry':
            if strategy.get('cleanup_required'):
                await self._cleanup_workflow_state(workflow_id)
                
            return await self._schedule_retry(
                workflow_id,
                strategy['delay'],
                context
            )
            
    async def _handle_failure(
        self,
        workflow_id: str,
        strategy: Dict[str, Any],
        context: Dict[str, Any]
    ):
        """
        Handle permanent workflow failure
        """
        await self.state_manager.save_workflow_state(
            workflow_id,
            {
                'status': 'failed',
                'error': strategy['reason'],
                'failure_context': context,
                'failed_at': datetime.utcnow().isoformat()
            }
        )
        
    async def _cleanup_workflow_state(self, workflow_id: str):
        """
        Clean up workflow state before retry
        """
        current_state = await self.state_manager.get_workflow_state(workflow_id)
        cleaned_state = {
            'status': 'retry_cleanup',
            'original_state': current_state,
            'cleaned_at': datetime.utcnow().isoformat()
        }
        await self.state_manager.save_workflow_state(workflow_id, cleaned_state)
        
    async def _schedule_retry(
        self,
        workflow_id: str,
        delay: int,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Schedule workflow retry
        """
        retry_time = datetime.utcnow() + timedelta(seconds=delay)
        retry_context = {
            **context,
            'retries': context.get('retries', 0) + 1,
            'retry_scheduled_at': datetime.utcnow().isoformat(),
            'retry_time': retry_time.isoformat()
        }
        
        # Save retry state
        await self.state_manager.save_workflow_state(
            workflow_id,
            {
                'status': 'retry_scheduled',
                'retry_context': retry_context
            }
        )
        
        return {
            'status': 'retry_scheduled',
            'retry_time': retry_time.isoformat(),
            'retry_attempt': retry_context['retries']
        }
        
    def _classify_error(
        self,
        error: Exception
    ) -> tuple[ErrorType, ErrorSeverity]:
        """
        Classify error type and severity
        """
        # Classification based on error type
        error_classifications = {
            ValueError: (ErrorType.VALIDATION, ErrorSeverity.LOW),
            TimeoutError: (ErrorType.TIMEOUT, ErrorSeverity.MEDIUM),
            ConnectionError: (ErrorType.INTEGRATION, ErrorSeverity.HIGH),
            Exception: (ErrorType.SYSTEM, ErrorSeverity.MEDIUM)
        }
        
        for error_class, (error_type, severity) in error_classifications.items():
            if isinstance(error, error_class):
                return error_type, severity
                
        return ErrorType.SYSTEM, ErrorSeverity.HIGH