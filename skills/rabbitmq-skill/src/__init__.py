"""
RabbitMQ Skill - Professional Message Queue Operations

A comprehensive RabbitMQ client for queue management, exchanges, routing,
RPC patterns, and reliable message delivery.
"""

__version__ = "1.0.0"
__author__ = "godlike-kimi-skills"

from .main import (
    RabbitMQSkill, RabbitMQConnection, RabbitMQQueueManager,
    RabbitMQExchangeManager, RabbitMQPublisher, RabbitMQConsumer, RabbitMQRPC
)

__all__ = [
    "RabbitMQSkill",
    "RabbitMQConnection",
    "RabbitMQQueueManager",
    "RabbitMQExchangeManager",
    "RabbitMQPublisher",
    "RabbitMQConsumer",
    "RabbitMQRPC",
]
