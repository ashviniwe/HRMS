"""
Shared Kafka utilities and configuration for HRMS microservices.
"""

__version__ = "1.0.0"

from .schemas import (
    EventType,
    BaseEvent,
    NotificationEvent,
    NotificationEventData,
    AuditEvent,
    AuditEventData,
    UserEvent,
    UserEventData,
    EmployeeEvent,
    EmployeeEventData,
    LeaveEvent,
    LeaveEventData,
    AttendanceEvent,
    AttendanceEventData,
    ComplianceEvent,
    ComplianceEventData,
    create_notification_event,
    create_audit_event,
    create_employee_event,
    create_leave_event,
    create_attendance_event,
)

from .producer import KafkaProducer, get_producer, close_producer
from .consumer import KafkaConsumer

__all__ = [
    # Event types
    "EventType",
    # Base events
    "BaseEvent",
    # Notification
    "NotificationEvent",
    "NotificationEventData",
    # Audit
    "AuditEvent",
    "AuditEventData",
    # User
    "UserEvent",
    "UserEventData",
    # Employee
    "EmployeeEvent",
    "EmployeeEventData",
    # Leave
    "LeaveEvent",
    "LeaveEventData",
    # Attendance
    "AttendanceEvent",
    "AttendanceEventData",
    # Compliance
    "ComplianceEvent",
    "ComplianceEventData",
    # Factory functions
    "create_notification_event",
    "create_audit_event",
    "create_employee_event",
    "create_leave_event",
    "create_attendance_event",
    # Producer/Consumer
    "KafkaProducer",
    "KafkaConsumer",
    "get_producer",
    "close_producer",
]
