#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Структурированная обработка отчетов через OpenAI API
Извлекает структурированную информацию из отчетов обработки документов
согласно настраиваемым промптам.
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

# Версия процессора
__version__ = "1.0.0"

# Настройка логирования
logger = logging.getLogger(__name__)


@dataclass
class CacheConfig:
    """Конфигурация системы кеширования"""
    enabled: bool = True
    memory_slots: int = 100
    disk_max_size_mb: int = 500
    default_ttl_hours: int = 24
    cleanup_interval_hours: int = 6


@dataclass
class ProcessingStats:
    """Статистика обработки"""
    start_time: float
    end_time: Optional[float] = None
    characters_processed: int = 0
    cache_hit: bool = False
    api_calls: int = 0
    
    @property
    def processing_time_seconds(self) -> float:
        if self.end_time:
            return self.end_time - self.start_time
        return time.time() - self.start_time


class TieredCacheManager:
    """Многоуровневый менеджер кеша для OpenAI API результатов"""
    
    def __init__(self, config: CacheConfig, cache_dir: str = "processed_documents/processing_cache"):
        self.config = config
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # Простой in-memory кеш
        self.memory_cache = {}
        
        logger.info(f"Initialized cache manager with dir: {self.cache_dir}")
    
    def _generate_cache_key(self, text: str, system_prompt: str, model: str) -> str:
        """Генерация умного ключа кеша"""
        normalized_text = " ".join(text.split())
        prompt_hash = hashlib.sha256(system_prompt.encode()).hexdigest()[:8]
        content_hash = hashlib.sha256(normalized_text.encode()).hexdigest()[:16]
        return f"{model}_{prompt_hash}_{content_hash}"
    
    def _get_cache_file_path(self, cache_key: str) -> Path:
        """Путь к файлу кеша"""
        return self.cache_dir / f"{cache_key}.json"
    
    def get(self, text: str, system_prompt: str, model: str) -> Optional[Dict[str, Any]]:
        """Получение из кеша"""
        if not self.config.enabled:
            return None
            
        cache_key = self._generate_cache_key(text, system_prompt, model)
        
        # 1. Проверка memory cache
        if cache_key in self.memory_cache:
            logger.debug(f"Cache HIT (memory): {cache_key}")
            return self.memory_cache[cache_key]
        
        # 2. Проверка disk cache
        cache_file = self._get_cache_file_path(cache_key)
        if cache_file.exists():
            try:
                with open(cache_file, 'r', encoding='utf-8') as f:
                    cached_data = json.load(f)
                
                # Проверка TTL
                cache_time = datetime.fromisoformat(cached_data.get('timestamp', '2000-01-01'))
                age_hours = (datetime.now() - cache_time).total_seconds() / 3600
                
                if age_hours < self.config.default_ttl_hours:
                    self.memory_cache[cache_key] = cached_data['data']
                    logger.debug(f"Cache HIT (disk): {cache_key}")
                    return cached_data['data']
                else:
                    cache_file.unlink()
                    logger.debug(f"Cache EXPIRED: {cache_key}")
            except Exception as e:
                logger.warning(f"Error reading cache {cache_key}: {e}")
        
        return None
    
    def set(self, text: str, system_prompt: str, model: str, data: Dict[str, Any]) -> None:
        """Сохранение в кеш"""
        if not self.config.enabled:
            return
            
        cache_key = self._generate_cache_key(text, system_prompt, model)
        
        # Сохранение в memory cache
        self.memory_cache[cache_key] = data
        
        # Сохранение в disk cache
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
    """Менеджер системных промптов"""
    
    def __init__(self, prompts_dir: str = "config/prompts"):
        self.prompts_dir = Path(prompts_dir)
        self.prompts_cache = {}
    
    def load_prompt(self, prompt_name: str) -> str:
        """Загрузка промпта из файла"""
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
        """Список доступных промптов"""
        if not self.prompts_dir.exists():
            return []
        
        return [f.stem for f in self.prompts_dir.glob("*.txt")]


class StructuredReportProcessor:
    """
    Основной класс для структурированной обработки отчетов
    через OpenAI API с кешированием и валидацией
    """
    
    def __init__(self, config_file: str = "config/settings.json"):
        """Инициализация процессора с конфигурацией"""
        self.config = self._load_config(config_file)
        self._setup_logging()
        
        # Инициализация компонентов
        self.cache_manager = TieredCacheManager(CacheConfig(**self.config["cache_settings"]))
        self.prompt_manager = PromptManager()
        
        # OpenAI клиент
        load_dotenv()
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY not found in environment variables")
        
        self.client = OpenAI(api_key=api_key)
        logger.info(f"Initialized StructuredReportProcessor v{__version__}")
    
    def _load_config(self, config_file: str) -> Dict[str, Any]:
        """Загрузка конфигурации"""
        config_path = Path(config_file)
        if config_path.exists():
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            logger.warning(f"Config file {config_file} not found, using defaults")
            return self._get_default_config()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Конфигурация по умолчанию"""
        return {
            "default_model": "gpt-4.1-mini",
            "fallback_model": "gpt-4.1-mini",
            "timeout_seconds": 120,
            "temperature": 0,
            "cache_settings": {
                "enabled": True,
                "memory_slots": 100,
                "disk_max_size_mb": 500,
                "default_ttl_hours": 24,
                "cleanup_interval_hours": 6
            },
            "input_settings": {
                "default_input_file": "processed_documents/complete_processing_report.md",
                "max_input_size_mb": 50,
                "encoding": "utf-8"
            },
            "output_settings": {
                "output_directory": "processed_documents",
                "filename_template": "structured_results_{timestamp}.json",
                "pretty_print": True
            },
            "logging": {
                "level": "INFO"
            }
        }
    
    def _setup_logging(self):
        """Настройка логирования"""
        log_level = getattr(logging, self.config["logging"]["level"], logging.INFO)
        logging.basicConfig(
            level=log_level,
            format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
    
    def _call_openai_api(self, text: str, system_prompt: str, model: str) -> Dict[str, Any]:
        """Вызов OpenAI API с обработкой ошибок и кешированием"""
        # Проверка кеша
        cached_result = self.cache_manager.get(text, system_prompt, model)
        if cached_result:
            return cached_result
        
        try:
            logger.info(f"Calling OpenAI API with model: {model}")
            resp = self.client.chat.completions.create(
                model=model,
                response_format={"type": "json_object"},
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": text},
                ],
                temperature=self.config["temperature"],
                timeout=self.config["timeout_seconds"],
            )
            
            content = resp.choices[0].message.content
            result = json.loads(content)
            
            # Сохранение в кеш
            self.cache_manager.set(text, system_prompt, model, result)
            
            logger.info("Successfully processed OpenAI response")
            return result
            
        except Exception as e:
            logger.error(f"OpenAI API call failed: {e}")
            return self._get_fallback_result()
    
    def _get_fallback_result(self) -> Dict[str, Any]:
        """Fallback результат при ошибке API"""
        return {
            "metadata": {
                "processor_version": __version__,
                "processing_timestamp": datetime.now(timezone.utc).isoformat(),
                "input_file": "unknown",
                "prompt_used": "fallback",
                "model_used": "fallback"
            },
            "extraction_info": {
                "total_characters_processed": 0,
                "extraction_method": "fallback",
                "cache_hit": False,
                "processing_time_seconds": 0
            },
            "results": {
                "summary": "Processing failed - using fallback result",
                "total_files_processed": 0,
                "file_types_found": [],
                "key_findings": [
                    {
                        "category": "error",
                        "description": "OpenAI API call failed",
                        "importance": "high"
                    }
                ],
                "processing_errors": []
            }
        }
    
    def process_report(
        self,
        input_file: str = None,
        prompt_name: str = "default_prompt",
        model: str = None,
        output_file: str = None
    ) -> Dict[str, Any]:
        """Основной метод обработки отчета"""
        stats = ProcessingStats(start_time=time.time())
        
        try:
            input_file = input_file or self.config["input_settings"]["default_input_file"]
            model = model or self.config["default_model"]
            
            logger.info(f"Starting processing: {input_file} with prompt: {prompt_name}")
            
            # Чтение входного файла
            input_path = Path(input_file)
            if not input_path.exists():
                raise FileNotFoundError(f"Input file not found: {input_file}")
            
            with open(input_path, 'r', encoding=self.config["input_settings"]["encoding"]) as f:
                text_content = f.read()
            
            stats.characters_processed = len(text_content)
            
            # Загрузка системного промпта
            system_prompt = self.prompt_manager.load_prompt(prompt_name)
            
            # Вызов OpenAI API
            result = self._call_openai_api(text_content, system_prompt, model)
            
            # Обновление метаданных в результате
            if "metadata" in result:
                result["metadata"].update({
                    "processor_version": __version__,
                    "processing_timestamp": datetime.now(timezone.utc).isoformat(),
                    "input_file": str(input_path),
                    "prompt_used": prompt_name,
                    "model_used": model
                })
            
            # Обновление статистики извлечения
            stats.end_time = time.time()
            if "extraction_info" in result:
                result["extraction_info"].update({
                    "total_characters_processed": stats.characters_processed,
                    "extraction_method": "cached" if stats.cache_hit else "openai_api",
                    "cache_hit": stats.cache_hit,
                    "processing_time_seconds": stats.processing_time_seconds
                })
            
            # Сохранение результата
            if output_file:
                self._save_results(result, output_file)
            else:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = self.config["output_settings"]["filename_template"].format(timestamp=timestamp)
                output_path = Path(self.config["output_settings"]["output_directory"]) / filename
                self._save_results(result, str(output_path))
            
            logger.info(f"Processing completed successfully in {stats.processing_time_seconds:.2f}s")
            return result
            
        except Exception as e:
            logger.error(f"Processing failed: {e}")
            stats.end_time = time.time()
            return self._get_fallback_result()
    
    def _save_results(self, results: Dict[str, Any], output_file: str) -> None:
        """Сохранение результатов в файл"""
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            if self.config["output_settings"]["pretty_print"]:
                json.dump(results, f, ensure_ascii=False, indent=2)
            else:
                json.dump(results, f, ensure_ascii=False)
        
        logger.info(f"Results saved to: {output_path}")
    
    def list_prompts(self) -> List[str]:
        """Список доступных промптов"""
        return self.prompt_manager.list_available_prompts()


def main():
    """Основная функция CLI"""
    parser = argparse.ArgumentParser(
        description="Структурированная обработка отчетов через OpenAI API",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Примеры использования:
  %(prog)s                                     # Обработка с настройками по умолчанию
  %(prog)s --prompt custom_prompt             # Использование конкретного промпта
  %(prog)s --input custom_report.md           # Обработка конкретного файла
  %(prog)s --model gpt-3.5-turbo             # Использование другой модели
  %(prog)s --list-prompts                     # Показать доступные промпты
        """
    )
    
    parser.add_argument("--input", "-i", help="Входной файл отчета")
    parser.add_argument("--output", "-o", help="Выходной файл результатов")
    parser.add_argument("--prompt", "-p", default="default_prompt", help="Системный промпт для использования")
    parser.add_argument("--model", "-m", help="OpenAI модель для использования")
    parser.add_argument("--config", "-c", default="config/settings.json", help="Файл конфигурации")
    
    # Утилитарные команды
    parser.add_argument("--list-prompts", action="store_true", help="Показать доступные промпты")
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    
    args = parser.parse_args()
    
    try:
        processor = StructuredReportProcessor(config_file=args.config)
        
        # Утилитарные команды
        if args.list_prompts:
            prompts = processor.list_prompts()
            print("Доступные промпты:")
            for prompt in prompts:
                print(f"  - {prompt}")
            return
        
        # Основная обработка
        result = processor.process_report(
            input_file=args.input,
            prompt_name=args.prompt,
            model=args.model,
            output_file=args.output
        )
        
        # Вывод кратких результатов
        if "results" in result and "summary" in result["results"]:
            print(f"✅ Обработка завершена: {result['results']['summary']}")
            
        if "extraction_info" in result:
            info = result["extraction_info"]
            print(f"📊 Статистика: {info.get('total_characters_processed', 0)} символов, "
                  f"{info.get('processing_time_seconds', 0):.2f}с")
        
    except Exception as e:
        logger.error(f"Application error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()