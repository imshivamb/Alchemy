
import pytest
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime
from fastapi_app.types.ai_types import (
    AIBatchRequest,
    AIRequest,
    AIResponse,
    AIModelType,
    PreprocessorType,
    AIConfig,
    OutputFormat
)
from backend.fastapi_app.services.ai.ai_service import AIService

@pytest.fixture
def ai_service():
    return AIService()

@pytest.fixture
def mock_openai_response():
    return Mock(
        choices=[
            Mock(
                message=Mock(
                    content="Test response"
                )
            )
        ],
        usage={
            "prompt_tokens": 10,
            "completion_tokens": 20,
            "total_tokens": 30
        }
    )

@pytest.mark.asyncio
async def test_process_request(ai_service, mock_openai_response):
    # Arrange
    request = AIRequest(
        model=AIModelType.GPT4,
        prompt="Test prompt",
        temperature=0.7,
        max_tokens=150
    )
    
    with patch.object(ai_service, '_get_ai_response', return_value=mock_openai_response):
        # Act
        response = await ai_service.process_request(
            request=request,
            workflow_id="test-workflow",
            user_id="test-user"
        )
        
        # Assert
        assert response.status == "processing"
        assert response.task_id is not None
        assert response.created_at is not None

@pytest.mark.asyncio
async def test_process_task_success(ai_service, mock_openai_response):
    # Arrange
    task_id = "test-task"
    task_data = {
        "input_data": {
            "model": AIModelType.GPT4,
            "prompt": "Test prompt",
            "temperature": 0.7,
            "max_tokens": 150
        },
        "workflow_id": "test-workflow",
        "user_id": "test-user"
    }
    
    with patch.object(ai_service, 'get_task_status', return_value=task_data), \
         patch.object(ai_service, '_get_ai_response', return_value=mock_openai_response), \
         patch.object(ai_service, 'update_task_status') as mock_update:
        # Act
        await ai_service.process_task(task_id)
        
        # Assert
        mock_update.assert_called_with(
            task_id,
            status="completed",
            result={"text": "Test response"},
            usage=mock_openai_response.usage
        )

@pytest.mark.asyncio
async def test_process_task_with_preprocessors(ai_service, mock_openai_response):
    # Arrange
    task_id = "test-task"
    task_data = {
        "input_data": {
            "model": AIModelType.GPT4,
            "prompt": "Test prompt",
            "preprocessors": [
                {"type": PreprocessorType.SUMMARIZE}
            ]
        }
    }
    
    with patch.object(ai_service, 'get_task_status', return_value=task_data), \
         patch.object(ai_service, '_apply_preprocessors') as mock_preprocess, \
         patch.object(ai_service, '_get_ai_response', return_value=mock_openai_response):
        # Act
        await ai_service.process_task(task_id)
        
        # Assert
        mock_preprocess.assert_called_once()

@pytest.mark.asyncio
async def test_fallback_behavior(ai_service, mock_openai_response):
    # Arrange
    task_id = "test-task"
    task_data = {
        "input_data": {
            "model": AIModelType.GPT4,
            "prompt": "Test prompt",
            "fallback_behavior": {
                "fallback_model": AIModelType.GPT_35_TURBO,
                "max_retries": 3
            }
        }
    }
    
    with patch.object(ai_service, 'get_task_status', return_value=task_data), \
         patch.object(ai_service, '_get_ai_response', side_effect=[Exception(), mock_openai_response]):
        # Act
        await ai_service.process_task(task_id)
        
        # Assert
        # Should have tried fallback model successfully

@pytest.mark.asyncio
async def test_output_formatting(ai_service, mock_openai_response):
    # Arrange
    json_response = Mock(
        choices=[
            Mock(
                message=Mock(
                    content='{"key": "value"}'
                )
            )
        ]
    )
    
    # Act
    result = await ai_service._format_output(json_response, "json")
    
    # Assert
    assert result == {"key": "value"}