#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Structured Document Processing Report Analyzer
Extracts structured information from document processing reports
using configurable JSON schemas and OpenAI API.
"""

import os
import sys
import json
import hashlib
import argparse
import logging
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, asdict

from openai import OpenAI
from dotenv import load_dotenv

# Processor version
__version__ = "1.0.0"

# Logging setup
logger = logging.getLogger(__name__)


@dataclass
class CacheConfig:
    """Caching system configuration"""
    enabled: bool = True
    memory_slots: int = 100
    disk_max_size_mb: int = 500
    default_ttl_hours: int = 24
    cleanup_interval_hours: int = 6


@dataclass
class ProcessingStats:
    """Processing statistics"""
    start_time: float
    end_time: Optional[float] = None
    characters_processed: int = 0
    cache_hit: bool = False
    api_calls: int = 0
    cost_estimate_usd: float = 0.0
    
    @property
    def processing_time_seconds(self) -> float:
        if self.end_time:
            return self.end_time - self.start_time
        return time.time() - self.start_time


class TieredCacheManager:
    """Multi-tier cache manager for OpenAI API results"""
    
    def __init__(self, config: CacheConfig, cache_dir: str = "processed_documents/processing_cache"):
        self.config = config
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # Simple in-memory cache (LRU via OrderedDict can be added later)
        self.memory_cache = {}
        
        logger.info(f"Initialized cache manager with dir: {self.cache_dir}")
    
    def _generate_cache_key(self, text: str, system_prompt: str, model: str) -> str:
        """Generate smart cache key"""
        # Text normalization
        normalized_text = " ".join(text.split())
        
        # Hashes for uniqueness
        prompt_hash = hashlib.sha256(system_prompt.encode()).hexdigest()[:8]
        content_hash = hashlib.sha256(normalized_text.encode()).hexdigest()[:16]
        
        return f"{model}_{prompt_hash}_{content_hash}"
    
    def _get_cache_file_path(self, cache_key: str) -> Path:
        """Cache file path"""
        return self.cache_dir / f"{cache_key}.json"
    
    def get(self, text: str, system_prompt: str, model: str) -> Optional[Dict[str, Any]]:
        """Get from cache"""
        if not self.config.enabled:
            return None
            
        cache_key = self._generate_cache_key(text, system_prompt, model)
        
        # 1. Check memory cache
        if cache_key in self.memory_cache:
            logger.debug(f"Cache HIT (memory): {cache_key}")
            return self.memory_cache[cache_key]
        
        # 2. Check disk cache
        cache_file = self._get_cache_file_path(cache_key)
        if cache_file.exists():
            try:
                with open(cache_file, 'r', encoding='utf-8') as f:
                    cached_data = json.load(f)
                
                # TTL check
                cache_time = datetime.fromisoformat(cached_data.get('timestamp', '2000-01-01'))
                age_hours = (datetime.now() - cache_time).total_seconds() / 3600
                
                if age_hours < self.config.default_ttl_hours:
                    # Promote to memory cache
                    self.memory_cache[cache_key] = cached_data['data']
                    logger.debug(f"Cache HIT (disk): {cache_key}")
                    return cached_data['data']
                else:
                    # Expired cache
                    cache_file.unlink()
                    logger.debug(f"Cache EXPIRED: {cache_key}")
            except Exception as e:
                logger.warning(f"Error reading cache {cache_key}: {e}")
        
        return None
    
    def set(self, text: str, system_prompt: str, model: str, data: Dict[str, Any]) -> None:
        """Save to cache"""
        if not self.config.enabled:
            return
            
        cache_key = self._generate_cache_key(text, system_prompt, model)
        
        # Save to memory cache
        self.memory_cache[cache_key] = data
        
        # Save to disk cache
        cache_file = self._get_cache_file_path(cache_key)
        cache_entry = {
            'timestamp': datetime.now().isoformat(),
            'model': model,
            'data': data
        }
        
        try:
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(cache_entry, f, ensure_ascii=False, indent=2)
            logger.debug(f"Cache SET: {cache_key}")
        except Exception as e:
            logger.warning(f"Error writing cache {cache_key}: {e}")


class PromptManager:
    """System prompts manager"""
    
    def __init__(self, prompts_dir: str = "config/prompts"):
        self.prompts_dir = Path(prompts_dir)
        self.prompts_cache = {}
    
    def load_prompt(self, prompt_name: str) -> str:
        """Load prompt from file"""
        if prompt_name in self.prompts_cache:
            return self.prompts_cache[prompt_name]
        
        prompt_file = self.prompts_dir / f"{prompt_name}.txt"
        if not prompt_file.exists():
            raise FileNotFoundError(f"Prompt file not found: {prompt_file}")
        
        with open(prompt_file, 'r', encoding='utf-8') as f:
            prompt_content = f.read()
        
        self.prompts_cache[prompt_name] = prompt_content
        return prompt_content
    
    def list_available_prompts(self) -> List[str]:
        """List available prompts"""
        if not self.prompts_dir.exists():
            return []
        
        return [f.stem for f in self.prompts_dir.glob("*.txt")]


class SchemaManager:
    """JSON schemas manager"""
    
    def __init__(self, schemas_dir: str = "config/schemas"):
        self.schemas_dir = Path(schemas_dir)
        self.schemas_cache = {}
    
    def load_schema(self, schema_name: str) -> Dict[str, Any]:
        """Load schema from file"""
        if schema_name in self.schemas_cache:
            return self.schemas_cache[schema_name]
        
        schema_file = self.schemas_dir / schema_name
        if not schema_file.exists():
            raise FileNotFoundError(f"Schema file not found: {schema_file}")
        
        with open(schema_file, 'r', encoding='utf-8') as f:
            schema_content = json.load(f)
        
        self.schemas_cache[schema_name] = schema_content
        return schema_content
    
    def list_available_schemas(self) -> List[str]:
        """List available schemas"""
        if not self.schemas_dir.exists():
            return []
        
        return [f.name for f in self.schemas_dir.glob("*.json")]
    
    def get_schema_info(self, schema_name: str) -> Dict[str, Any]:
        """Get schema metadata and summary"""
        schema = self.load_schema(schema_name)
        return {
            'name': schema_name,
            'title': schema.get('title', 'Untitled Schema'),
            'description': schema.get('description', 'No description available'),
            'version': schema.get('version', '1.0.0'),
            'properties_count': len(schema.get('properties', {}))
        }


class StructuredReportProcessor:
    """Main processor class for structured report analysis"""
    
    def __init__(self, config_file: str = "config/settings.json"):
        # Load environment variables
        load_dotenv()
        
        # Load configuration
        self.config = self._load_config(config_file)
        
        # Setup logging
        self._setup_logging()
        
        # Initialize managers
        self.cache_manager = TieredCacheManager(CacheConfig(**self.config.get('cache', {})))
        self.prompt_manager = PromptManager(self.config.get('prompts_dir', 'config/prompts'))
        self.schema_manager = SchemaManager(self.config.get('schemas_dir', 'config/schemas'))
        
        # Initialize OpenAI client
        self.client = OpenAI(
            api_key=os.getenv('OPENAI_API_KEY') or self.config.get('openai_api_key')
        )
        
        logger.info(f"StructuredReportProcessor v{__version__} initialized")
    
    def _load_config(self, config_file: str) -> Dict[str, Any]:
        """Load configuration from file"""
        config_path = Path(config_file)
        if config_path.exists():
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            logger.warning(f"Config file not found: {config_file}, using defaults")
            return self._get_default_config()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration"""
        return {
            "openai": {
                "model": "gpt-4o-mini",
                "temperature": 0.1,
                "max_tokens": 4000
            },
            "cache": {
                "enabled": True,
                "memory_slots": 100,
                "disk_max_size_mb": 500,
                "default_ttl_hours": 24
            },
            "processing": {
                "default_schema": "default_schema.json",
                "default_prompt": "default_prompt",
                "input_dir": "processed_documents",
                "output_dir": "processed_documents"
            },
            "logging": {
                "level": "INFO",
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            }
        }
    
    def _setup_logging(self):
        """Setup logging configuration"""
        log_config = self.config.get('logging', {})
        logging.basicConfig(
            level=getattr(logging, log_config.get('level', 'INFO')),
            format=log_config.get('format', '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        )
    
    def _estimate_cost(self, model: str, input_tokens: int, output_tokens: int) -> float:
        """Estimate API call cost"""
        # Simplified cost estimation (prices as of 2024)
        costs = {
            'gpt-4o-mini': {'input': 0.000150 / 1000, 'output': 0.000600 / 1000},
            'gpt-4o': {'input': 0.005 / 1000, 'output': 0.015 / 1000},
            'gpt-4': {'input': 0.03 / 1000, 'output': 0.06 / 1000}
        }
        
        model_cost = costs.get(model, costs['gpt-4o-mini'])
        return (input_tokens * model_cost['input']) + (output_tokens * model_cost['output'])
    
    def _call_openai_api(self, text: str, system_prompt: str, model: str) -> Dict[str, Any]:
        """Make OpenAI API call with error handling"""
        try:
            response = self.client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": text}
                ],
                temperature=self.config['openai'].get('temperature', 0.1),
                max_tokens=self.config['openai'].get('max_tokens', 4000),
                response_format={"type": "json_object"}
            )
            
            result = json.loads(response.choices[0].message.content)
            
            # Add cost estimation
            usage = response.usage
            cost = self._estimate_cost(model, usage.prompt_tokens, usage.completion_tokens)
            
            return {
                'success': True,
                'data': result,
                'tokens_used': usage.total_tokens,
                'cost_usd': cost
            }
            
        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            return {
                'success': False,
                'error': str(e),
                'data': self._get_fallback_result()
            }
    
    def _get_fallback_result(self) -> Dict[str, Any]:
        """Generate fallback result when API fails"""
        return {
            "metadata": {
                "processor_version": __version__,
                "processing_timestamp": datetime.now(timezone.utc).isoformat(),
                "input_file": "unknown",
                "schema_name": "fallback",
                "model_used": "fallback"
            },
            "extraction_info": {
                "total_characters_processed": 0,
                "extraction_method": "fallback",
                "cache_hit": False,
                "processing_time_seconds": 0.0,
                "api_cost_estimate_usd": 0.0
            },
            "results": {
                "summary": "Processing failed - using fallback result",
                "total_files_processed": 0,
                "file_types_found": [],
                "key_findings": [
                    {
                        "category": "error",
                        "description": "API processing failed, manual review required",
                        "importance": "high"
                    }
                ],
                "processing_errors": [
                    {
                        "file_name": "system",
                        "error_type": "api_failure",
                        "error_description": "OpenAI API call failed"
                    }
                ]
            }
        }
    
    def process_report(
        self,
        input_file: str = None,
        schema_name: str = None,
        prompt_name: str = "default_prompt",
        model: str = None,
        output_file: str = None
    ) -> Dict[str, Any]:
        """
        Process a document processing report with structured extraction
        
        Args:
            input_file: Path to input markdown report
            schema_name: JSON schema file name
            prompt_name: System prompt name
            model: OpenAI model to use
            output_file: Output JSON file path
            
        Returns:
            Dict containing extracted structured information
        """
        stats = ProcessingStats(start_time=time.time())
        
        # Use defaults from config if not provided
        if input_file is None:
            input_file = f"{self.config['processing']['input_dir']}/complete_processing_report.md"
        if schema_name is None:
            schema_name = self.config['processing']['default_schema']
        if model is None:
            model = self.config['openai']['model']
        if output_file is None:
            base_name = Path(input_file).stem
            output_file = f"{self.config['processing']['output_dir']}/{base_name}_structured.json"
        
        logger.info(f"Processing: {input_file} -> {output_file}")
        logger.info(f"Schema: {schema_name}, Prompt: {prompt_name}, Model: {model}")
        
        try:
            # 1. Read input report
            input_path = Path(input_file)
            if not input_path.exists():
                raise FileNotFoundError(f"Input file not found: {input_file}")
            
            with open(input_path, 'r', encoding='utf-8') as f:
                report_text = f.read()
            
            stats.characters_processed = len(report_text)
            logger.info(f"Read {stats.characters_processed} characters from {input_file}")
            
            # 2. Load schema and prompt
            schema = self.schema_manager.load_schema(schema_name)
            system_prompt = self.prompt_manager.load_prompt(prompt_name)
            
            # 3. Check cache
            cached_result = self.cache_manager.get(report_text, system_prompt, model)
            if cached_result:
                logger.info("Using cached result")
                stats.cache_hit = True
                result = cached_result
            else:
                # 4. Call OpenAI API
                logger.info("Calling OpenAI API...")
                api_response = self._call_openai_api(report_text, system_prompt, model)
                
                if api_response['success']:
                    result = api_response['data']
                    stats.api_calls = 1
                    stats.cost_estimate_usd = api_response.get('cost_usd', 0.0)
                    
                    # Cache the result
                    self.cache_manager.set(report_text, system_prompt, model, result)
                else:
                    logger.error("API call failed, using fallback")
                    result = api_response['data']
            
            # 5. Enhance result with processing metadata
            stats.end_time = time.time()
            
            if 'metadata' not in result:
                result['metadata'] = {}
            if 'extraction_info' not in result:
                result['extraction_info'] = {}
            
            result['metadata'].update({
                'processor_version': __version__,
                'processing_timestamp': datetime.now(timezone.utc).isoformat(),
                'input_file': str(input_file),
                'schema_name': schema_name,
                'model_used': model
            })
            
            result['extraction_info'].update({
                'total_characters_processed': stats.characters_processed,
                'extraction_method': 'openai_api',
                'cache_hit': stats.cache_hit,
                'processing_time_seconds': stats.processing_time_seconds,
                'api_cost_estimate_usd': stats.cost_estimate_usd
            })
            
            # 6. Save results
            self._save_results(result, output_file)
            
            logger.info(f"Processing completed successfully")
            logger.info(f"Processing time: {stats.processing_time_seconds:.2f}s")
            logger.info(f"Cost estimate: ${stats.cost_estimate_usd:.4f}")
            
            return result
            
        except Exception as e:
            logger.error(f"Processing failed: {e}")
            raise
    
    def _save_results(self, results: Dict[str, Any], output_file: str) -> None:
        """Save results to JSON file"""
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        
        logger.info(f"Results saved to: {output_file}")
    
    def list_schemas(self) -> List[str]:
        """List available schemas"""
        return self.schema_manager.list_available_schemas()
    
    def list_prompts(self) -> List[str]:
        """List available prompts"""
        return self.prompt_manager.list_available_prompts()


def main():
    """Command line interface"""
    parser = argparse.ArgumentParser(
        description='Structured Document Processing Report Analyzer',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Process with default settings
  python structured_report_processor.py
  
  # Use specific schema and prompt
  python structured_report_processor.py -s document_analysis_schema.json -p custom_prompt
  
  # Process specific file
  python structured_report_processor.py -i reports/my_report.md -o results/output.json
  
  # List available resources
  python structured_report_processor.py --list-schemas
  python structured_report_processor.py --list-prompts
        """
    )
    
    parser.add_argument('-i', '--input', 
                       help='Input markdown report file (default: processed_documents/complete_processing_report.md)')
    parser.add_argument('-o', '--output',
                       help='Output JSON file (default: auto-generated based on input name)')
    parser.add_argument('-s', '--schema',
                       help='JSON schema file name (default: default_schema.json)')
    parser.add_argument('-p', '--prompt',
                       help='System prompt name (default: default_prompt)')
    parser.add_argument('-m', '--model',
                       help='OpenAI model (default: gpt-4o-mini)')
    parser.add_argument('--list-schemas', action='store_true',
                       help='List available schemas')
    parser.add_argument('--list-prompts', action='store_true',
                       help='List available prompts')
    parser.add_argument('-v', '--verbose', action='store_true',
                       help='Enable verbose logging')
    parser.add_argument('--version', action='version', version=f'%(prog)s {__version__}')
    
    args = parser.parse_args()
    
    # Setup basic logging for CLI
    log_level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(level=log_level, format='%(asctime)s - %(levelname)s - %(message)s')
    
    try:
        processor = StructuredReportProcessor()
        
        if args.list_schemas:
            schemas = processor.list_schemas()
            print("Available schemas:")
            for schema in schemas:
                print(f"  - {schema}")
            return
        
        if args.list_prompts:
            prompts = processor.list_prompts()
            print("Available prompts:")
            for prompt in prompts:
                print(f"  - {prompt}")
            return
        
        # Process report
        result = processor.process_report(
            input_file=args.input,
            schema_name=args.schema,
            prompt_name=args.prompt,
            model=args.model,
            output_file=args.output
        )
        
        print("✅ Processing completed successfully!")
        print(f"📄 Results saved to: {args.output or 'auto-generated filename'}")
        
        # Show summary
        if 'results' in result and 'summary' in result['results']:
            print(f"📋 Summary: {result['results']['summary']}")
        
    except Exception as e:
        logger.error(f"CLI execution failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()