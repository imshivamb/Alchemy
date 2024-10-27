# backend/django_app/workflow_engine/transformers/data_transformer.py

from typing import Dict, Any, List, Union
from enum import Enum
import json
import jmespath
from datetime import datetime

class TransformationType(Enum):
    MAP = "map"
    FILTER = "filter"
    MERGE = "merge"
    FORMAT = "format"
    VALIDATE = "validate"
    CONVERT = "convert"

class DataTransformer:
    """
    Transform data between workflow steps
    """
    
    def __init__(self):
        self.transformers = {
            TransformationType.MAP: self._map_data,
            TransformationType.FILTER: self._filter_data,
            TransformationType.MERGE: self._merge_data,
            TransformationType.FORMAT: self._format_data,
            TransformationType.VALIDATE: self._validate_data,
            TransformationType.CONVERT: self._convert_data
        }
        
    async def transform(
        self,
        data: Dict[str, Any],
        transformation_rules: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Apply transformation rules to data
        """
        transformed_data = data.copy()
        
        for rule in transformation_rules:
            transform_type = TransformationType(rule.get('type'))
            transform_config = rule.get('config', {})
            
            transformer = self.transformers.get(transform_type)
            if transformer:
                transformed_data = await transformer(
                    transformed_data,
                    transform_config
                )
                
        return transformed_data
        
    async def _map_data(
        self,
        data: Dict[str, Any],
        config: Dict[str, str]
    ) -> Dict[str, Any]:
        """
        Map data fields using JMESPath expressions
        """
        result = {}
        for target_key, expression in config.items():
            try:
                result[target_key] = jmespath.search(expression, data)
            except Exception as e:
                raise ValueError(f"Mapping error for {target_key}: {str(e)}")
        return result
        
    async def _filter_data(
        self,
        data: Dict[str, Any],
        config: Dict[str, Union[List[str], Dict[str, Any]]]
    ) -> Dict[str, Any]:
        """
        Filter data based on include/exclude rules
        """
        if isinstance(config.get('include'), list):
            return {k: v for k, v in data.items() if k in config['include']}
        elif isinstance(config.get('exclude'), list):
            return {k: v for k, v in data.items() if k not in config['exclude']}
        return data
        
    async def _merge_data(
        self,
        data: Dict[str, Any],
        config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Merge multiple data sources
        """
        result = data.copy()
        for source_key, merge_config in config.items():
            if source_data := data.get(source_key):
                if merge_config.get('method') == 'overlay':
                    result.update(source_data)
                elif merge_config.get('method') == 'append':
                    result.setdefault(source_key, []).extend(source_data)
        return result
        
    async def _format_data(
        self,
        data: Dict[str, Any],
        config: Dict[str, str]
    ) -> Dict[str, Any]:
        """
        Format data fields according to specified formats
        """
        result = data.copy()
        for field, format_spec in config.items():
            if value := result.get(field):
                if format_spec == 'iso_date':
                    result[field] = self._format_date(value)
                elif format_spec == 'number':
                    result[field] = self._format_number(value)
                elif format_spec.startswith('string:'):
                    result[field] = self._format_string(
                        value,
                        format_spec.split(':')[1]
                    )
        return result
        
    async def _validate_data(
        self,
        data: Dict[str, Any],
        config: Dict[str, Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Validate data against rules
        """
        for field, rules in config.items():
            if value := data.get(field):
                self._validate_field(field, value, rules)
        return data
        
    async def _convert_data(
        self,
        data: Dict[str, Any],
        config: Dict[str, str]
    ) -> Dict[str, Any]:
        """
        Convert data types
        """
        result = data.copy()
        for field, target_type in config.items():
            if value := result.get(field):
                result[field] = self._convert_value(value, target_type)
        return result
        
    def _format_date(self, value: Union[str, datetime]) -> str:
        """Format date to ISO format"""
        if isinstance(value, str):
            value = datetime.fromisoformat(value)
        return value.isoformat()
        
    def _format_number(self, value: Union[str, int, float]) -> str:
        """Format number with proper precision"""
        return f"{float(value):.2f}"
        
    def _format_string(self, value: Any, format_spec: str) -> str:
        """Format string according to specification"""
        return format_spec.format(str(value))
        
    def _validate_field(
        self,
        field: str,
        value: Any,
        rules: Dict[str, Any]
    ):
        """Validate field against rules"""
        if 'type' in rules:
            if not isinstance(value, eval(rules['type'])):
                raise ValueError(f"Invalid type for {field}")
        if 'required' in rules and rules['required'] and value is None:
            raise ValueError(f"Required field {field} is missing")
        if 'min' in rules and value < rules['min']:
            raise ValueError(f"Value for {field} is below minimum")
        if 'max' in rules and value > rules['max']:
            raise ValueError(f"Value for {field} exceeds maximum")
        
    def _convert_value(self, value: Any, target_type: str) -> Any:
        """Convert value to target type"""
        type_converters = {
            'int': int,
            'float': float,
            'str': str,
            'bool': bool,
            'list': lambda x: json.loads(x) if isinstance(x, str) else list(x),
            'dict': lambda x: json.loads(x) if isinstance(x, str) else dict(x)
        }
        
        converter = type_converters.get(target_type)
        if not converter:
            raise ValueError(f"Unknown target type: {target_type}")
            
        try:
            return converter(value)
        except Exception as e:
            raise ValueError(f"Conversion error: {str(e)}")