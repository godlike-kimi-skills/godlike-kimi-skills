"""
Apache Kafka Skill - Professional Message Queue Operations

A comprehensive Kafka client for topic management, producing/consuming messages,
and consumer group operations.
"""

__version__ = "1.0.0"
__author__ = "godlike-kimi-skills"

from .main import KafkaSkill, KafkaTopicManager, KafkaProducer, KafkaConsumer

__all__ = [
    "KafkaSkill",
    "KafkaTopicManager", 
    "KafkaProducer",
    "KafkaConsumer",
]
