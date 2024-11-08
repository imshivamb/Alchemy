import asyncio
import uuid
import aiohttp
from ...django_app.tasks.ai_tasks import process_ai_request
from typing import Dict, Any, Optional, List
import os
import openai
import json
from datetime import datetime
from redis_service.base import BaseRedis
from ..types.ai_types import AIModelType, PreprocessorType, AIConfig, OutputFormat
class AIService(BaseRedis):
    def __init__(self):
        super().__init__()
        self.task_prefix = "ai_task:"
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.model_configs = self._inititalize_model_configs()
        self.prompt_templates = self._load_prompt_templates()
        openai.api_key = os.getenv("OPENAI_API_KEY")
        
    def _initialize_model_configs(self):
        """Initial configs for different AI models"""
        return {
            AIModelType.GPT_40_MINI: {
                "max_tokens": 128000,
                "supports_functions": True,
                "cost_per_token": 0.01,
                "recommended_uses": ["Long context", "Latest features"]
            },
            AIModelType.GPT_4: {
                "max_tokens": 8192,
                "supports_functions": True,
                "cost_per_token": 0.03,
                "recommended_uses": ["Complex Reasoning", "Code generation"]
            },
            AIModelType.GPT_35: {
                "max_tokens": 4096,
                "supports_functions": True,
                "cost_per_token": 0.002,
                "recommended_uses": ["Quick resonse", "simple tasks"]
            }
        }
    
    def _load_prompt_templates(self) -> Dict[str, str]:
        """Load prompt templates"""
        return {
            "summarize": "Summarize the following text: \n{text}",
            "translate": "Translate the following text to {language}: \n{text}",
            "extract_info": "Extract the following information from the text:\n{fields}\nText: {text}",
            "analyze": "Analyze the following text and provide insights:\n{text}"
        }

    async def _get_ai_response(self, model: AIModelType, prompt: str, system_message: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 150) -> Dict[Any, Any]:
        """Get AI response from OpenAI"""
        try:
            if model == AIModelType.GPT_40_MINI:
                response = openai.ChatCompletion.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": system_message} if system_message else None,
                        {"role": "user", "content": prompt}
                    ],
                    temperature=temperature,
                    max_tokens=max_tokens,
                    n=1,
                    stop=None,
                    stream=False,
                )
            elif model == AIModelType.GPT_4:
                response = openai.ChatCompletion.create(
                    model="gpt-4-turbo",
                    messages=[
                        {"role": "system", "content": system_message} if system_message else None,
                        {"role": "user", "content": prompt}
                    ],
                    temperature=temperature,
                    max_tokens=max_tokens,
                    n=1,
                    stop=None,
                    stream=False,
                )
            elif model == AIModelType.GPT_35:
                response = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": system_message} if system_message else None,
                        {"role": "user", "content": prompt}
                    ],
                    temperature=temperature,
                    max_tokens=max_tokens,
                    n=1,
                    stop=None,
                    stream=False,
                )
            else:
                raise Exception(f"Model {model} not supported")
            
            return response
        
        except openai.NotFoundError as e:
            raise Exception(f"Error calling OpenAI API: {str(e)}")
        
    async def process_task(self, task_id: str):
        """Process the AI task"""
        try:
            task_data = await self.get_task_status(task_id)
            config = AIConfig(**task_data["config"])
            
            await self.update_task_status(task_id, status="processing")
            
            processed_prompt = await self.apply_preprocessors(config.preprocessors, config.prompt)
            
            response = await self._get_ai_response(
                model=config.model,
                prompt=processed_prompt,
                system_message=config.system_message,
                temperature=config.temperature,
                max_tokens=config.max_tokens
            )
            
            formatted_response = await self._format_output(response, config.output_format)
            
            await self.update_task_status(task_id, status="completed", result=formatted_response, usage=response.usage)
        except Exception as e:
            if config and config.fallback_behavior:
                try:
                    fallback_response = await self._handle_fallback(config, str(e))
                    await self.update_task_status(
                        task_id,
                        status="completed",
                        result=fallback_response,
                        error=f"Used fallback due to: {str(e)}"
                    )
                    return
                except Exception as fallback_error:
                    error = f"Original error: {str(e)}, Fallback error: {str(fallback_error)}"
            else:
                error = str(e)
                
            await self.update_task_status(
                task_id,
                status="failed",
                error=error
            )
    

    async def create_task(
        self,
        workflow_id: str,
        config: AIConfig,
        user_id: str
    ) -> str:
        """Create a new AI processing task"""
        task_id = str(uuid.uuid4())
        
        self._validate_model_config(config)
        task_data = {
            "workflow_id": workflow_id,
            "config": config.dict(),
            "status": "pending",
            "user_id": user_id,
            "created_at": datetime.utcnow().isoformat(),
            "result": None,
            "error": None,
            "usage": None
        }
        
        # Storing the task in Redis with a 24-hour expiration
        await self.set_data(
            f"{self.task_prefix}{task_id}",
            task_data,
            expires=86400
        )
        
        process_ai_request.delay(task_data)
        return task_id
    
    async def _apply_preprocessors(
        self,
        prompt: str,
        preprocessors: List[Dict[str, Any]]
    ) -> str:
        """Apply preprocessors to the prompt"""
        processed_prompt = prompt
        
        for preprocessor in preprocessors:
            preprocessor_type = PreprocessorType(preprocessor["type"])
            
            if preprocessor_type == PreprocessorType.SUMMARIZE:
                processed_prompt = await self._summarize_text(processed_prompt)
            elif preprocessor_type == PreprocessorType.TRANSLATE:
                processed_prompt = await self._translate_text(
                    processed_prompt,
                    preprocessor.get("target_language", "en")
                )
            elif preprocessor_type == PreprocessorType.EXTRACT:
                processed_prompt = await self._extract_information(
                    processed_prompt,
                    preprocessor.get("fields", [])
                )
            elif preprocessor_type == PreprocessorType.FORMAT:
                processed_prompt = await self._format_text(
                    processed_prompt,
                    preprocessor.get("format_type", "clean")
                )
                
        return processed_prompt
    
    async def _format_output(
        self,
        response: Any,
        output_format: OutputFormat
    ) -> Dict[str, Any]:
        """Format the AI response"""
        content = response.choices[0].message.content
        
        if output_format == OutputFormat.TEXT:
            return {"text": content}
            
        elif output_format == OutputFormat.JSON:
            try:
                return json.loads(content)
            except json.JSONDecodeError:
                return {
                    "text": content,
                    "format_error": "Invalid JSON response"
                }
                
        elif output_format == OutputFormat.MARKDOWN:
            return {
                "markdown": content,
                "html": self._convert_markdown_to_html(content)
            }
            
        elif output_format == OutputFormat.HTML:
            return {
                "html": content,
                "text": self._strip_html_tags(content)
            }
            
        # Default case if no format matches
        return {"text": str(content)}
    
    def _validate_model_config(self, config: AIConfig):
        """Validate the AI config"""
        model_config = self.model_configs.get(config.model)
        if not model_config:
            raise ValueError(f"Invalid model: {config.model}")
        
        if config.max_tokens > model_config["max_tokens"]:
            raise ValueError(f"Max tokens {config.max_tokens} exceeds model limit of {model_config['max_tokens']}")
        
        if not config.prompt:
            raise ValueError("Prompt is required")
        
    async def get_available_models(self) -> List[Dict[str, Any]]:
        """Get list of available models and their configurations"""
        return [
            {
                "id": model_id,
                "name": model_id,
                **config
            }
            for model_id, config in self.model_configs.items()
        ]
        
    async def estimate_cost(
        self,
        config: AIConfig,
        prompt: str
    ) -> Dict[str, float]:
        """Estimate cost for a request"""
        model_config = self.model_configs[config.model]
        estimated_tokens = len(prompt.split()) * 1.3  # Rough estimation
        
        return {
            "estimated_tokens": estimated_tokens,
            "estimated_cost": (
                estimated_tokens * model_config["cost_per_token"] / 1000
            )
        }

        
    async def get_task_status(self, task_id: str) -> Dict[str, Any]:
        """Get task status and results"""
        task_data = await self.get_data(f"{self.task_prefix}{task_id}")
        if not task_data:
            raise ValueError(f"Task {task_id} not found")
        return task_data
    
    async def update_task_status(self, task_id: str, status: str, result: Dict = None, error: str = None):
        """Update task status in Redis"""
        task_data = await self.get_task_status(task_id)
        task_data.update({
            "status": status,
            "result": result,
            "error": error,
            "updated_at": datetime.utcnow().isoformat()
        })
        await self.set_data(f"{self.task_prefix}{task_id}", task_data)

    async def setup_subscribers(self):
        """Setup subscribers for AI tasks"""
        await self.subscribe('ai_tasks', self.handle_task_update)

    async def handle_task_update(self, data: dict):
        """Handle AI task updates"""
        task_id = data.get('task_id')
        if task_id:
            await self.update_task_progress(
                task_id,
                data.get('progress', 0),
                data.get('status', 'processing')
            )
    
    

    async def _summarize_text(self, text: str, max_length: int = 1000) -> str:
        """
        Summarize text using AI model
        Args:
            text: Text to summarize
            max_length: Maximum length of summary in tokens
        Returns:
            Summarized text
        """
        try:
            response = await self._get_ai_response(
                model=AIModelType.GPT_40_MINI, 
                prompt=self.prompt_templates["summarize"].format(text=text),
                max_tokens=max_length,
                temperature=0.5  
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            raise Exception(f"Summarization failed: {str(e)}")

    async def _translate_text(self, text: str, target_language: str) -> str:
            """
            Translate text to target language
            Args:
                text: Text to translate
                target_language: Target language code (e.g., 'es', 'fr', 'de')
            Returns:
                Translated text
            """
            try:
                response = await self._get_ai_response(
                    model=AIModelType.GPT_40_MINI,
                    prompt=self.prompt_templates["translate"].format(
                        text=text,
                        language=target_language
                    ),
                    temperature=0.3 
                )
                return response.choices[0].message.content.strip()
            except Exception as e:
                raise Exception(f"Translation failed: {str(e)}")

    async def _extract_information(self, text: str, fields: List[str]) -> str:
            """
            Extract specific information from text
            Args:
                text: Source text
                fields: List of fields to extract (e.g., ["name", "date", "location"])
            Returns:
                Formatted string with extracted information
            """
            try:
                response = await self._get_ai_response(
                    model=AIModelType.GPT_40_MINI,
                    prompt=self.prompt_templates["extract_info"].format(
                        text=text,
                        fields="\n".join([f"- {field}" for field in fields])
                    ),
                    temperature=0.2 
                )
                return response.choices[0].message.content.strip()
            except Exception as e:
                raise Exception(f"Information extraction failed: {str(e)}")

    async def _format_text(self, text: str, format_type: str) -> str:
            """
            Format text based on specified format type
            Args:
                text: Text to format
                format_type: Type of formatting to apply ('clean', 'markdown', 'html', etc.)
            Returns:
                Formatted text
            """
            try:
                format_prompts = {
                    "clean": "Clean and normalize the following text, removing unnecessary whitespace and formatting:\n{text}",
                    "markdown": "Convert the following text to markdown format:\n{text}",
                    "html": "Convert the following text to HTML format:\n{text}",
                    "json": "Convert the following text to JSON format:\n{text}"
                }
                
                if format_type not in format_prompts:
                    raise ValueError(f"Unsupported format type: {format_type}")
                
                response = await self._get_ai_response(
                    model=AIModelType.GPT_40_MINI,
                    prompt=format_prompts[format_type].format(text=text),
                    temperature=0.1  
                )
                return response.choices[0].message.content.strip()
            except Exception as e:
                raise Exception(f"Text formatting failed: {str(e)}")
