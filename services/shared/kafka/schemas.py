"""
Shared Kafka event schemas for HRMS microservices.
Defines Pydantic models for all event types across the system.
"""

from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field
from enum import Enum


class EventType(str, Enum):
    """Event type enumeration for all HRMS events."""
    
    # User events
    USER_CREATED = "user.created"
    USER_UPDATED = "user.updated"
    USER_DELETED = "user.deleted"
    USER_SUSPENDED = "user.suspended"
    USER_ACTIVATED = "user.activated"
    USER_PASSWORD_CHANGED = "user.password_changed"
    
    # Employee events
    EMPLOYEE_CREATED = "employee.created"
    EMPLOYEE_UPDATED = "employee.updated"
    EMPLOYEE_TERMINATED = "employee.terminated"
    EMPLOYEE_STATUS_CHANGED = "employee.status_changed"
    
    # Leave events
    LEAVE_REQUESTED = "leave.requested"
    LEAVE_APPROVED = "leave.approved"
    LEAVE_REJECTED = "leave.rejected"
    LEAVE_CANCELLED = "leave.cancelled"
    LEAVE_UPDATED = "leave.updated"
    
    # Attendance events
    ATTENDANCE_MARKED = "attendance.marked"
    ATTENDANCE_UPDATED = "attendance.updated"
    ATTENDANCE_DELETED = "attendance.deleted"
    
    # Compliance events
    COMPLIANCE_VIOLATION = "compliance.violation"
    COMPLIANCE_ALERT = "compliance.alert"
    COMPLIANCE_CHECK_COMPLETED = "compliance.check_completed"
    
    # Audit events
    AUDIT_USER_ACTION = "audit.user.action"
    AUDIT_EMPLOYEE_ACTION = "audit.employee.action"
    AUDIT_LEAVE_ACTION = "audit.leave.action"
    AUDIT_ATTENDANCE_ACTION = "audit.attendance.action"
    AUDIT_COMPLIANCE_ACTION = "audit.compliance.action"


class BaseEvent(BaseModel):
    """Base event model for all Kafka events."""
    
    event_id: str = Field(..., description="Unique event identifier (UUID)")
    event_type: EventType = Field(..., description="Type of event")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Event timestamp (UTC)")
    source_service: str = Field(..., description="Service that produced the event")
    correlation_id: Optional[str] = Field(None, description="Correlation ID for tracking related events")
    
    class Config:
        use_enum_values = True


# ============================================================================
# Notification Events
# ============================================================================

class NotificationEventData(BaseModel):
    """Data payload for notification events."""
    
    recipient_email: str
    recipient_name: Optional[str] = None
    subject: str
    template_name: str
    template_data: Dict[str, Any] = Field(default_factory=dict)
    priority: str = "normal"  # low, normal, high


class NotificationEvent(BaseEvent):
    """Notification event for sending emails/notifications."""
    
    data: NotificationEventData


# ============================================================================
# Audit Events
# ============================================================================

class AuditEventData(BaseModel):
    """Data payload for audit events."""
    
    user_id: int
    action: str  # CREATE, UPDATE, DELETE, READ
    resource_type: str  # user, employee, leave, attendance, etc.
    resource_id: int
    description: Optional[str] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    old_value: Optional[str] = None
    new_value: Optional[str] = None
    changes: Optional[Dict[str, Any]] = None


class AuditEvent(BaseEvent):
    """Audit event for logging user actions."""
    
    data: AuditEventData


# ============================================================================
# User Events
# ============================================================================

class UserEventData(BaseModel):
    """Data payload for user-related events."""
    
    user_id: int
    email: str
    first_name: str
    last_name: str
    role: Optional[str] = None
    status: Optional[str] = None
    reason: Optional[str] = None  # For suspension/deletion


class UserEvent(BaseEvent):
    """User lifecycle event."""
    
    data: UserEventData


# ============================================================================
# Employee Events
# ============================================================================

class EmployeeEventData(BaseModel):
    """Data payload for employee-related events."""
    
    employee_id: int
    user_id: Optional[int] = None
    email: str
    first_name: str
    last_name: str
    department: Optional[str] = None
    position: Optional[str] = None
    status: Optional[str] = None
    hire_date: Optional[str] = None
    termination_date: Optional[str] = None


class EmployeeEvent(BaseEvent):
    """Employee lifecycle event."""
    
    data: EmployeeEventData


# ============================================================================
# Leave Events
# ============================================================================

class LeaveEventData(BaseModel):
    """Data payload for leave-related events."""
    
    leave_id: int
    employee_id: int
    employee_email: str
    employee_name: Optional[str] = None
    leave_type: str
    start_date: str
    end_date: str
    days: int
    status: str
    reason: Optional[str] = None
    approved_by: Optional[str] = None
    approved_by_name: Optional[str] = None
    rejection_reason: Optional[str] = None


class LeaveEvent(BaseEvent):
    """Leave management event."""
    
    data: LeaveEventData


# ============================================================================
# Attendance Events
# ============================================================================

class AttendanceEventData(BaseModel):
    """Data payload for attendance-related events."""
    
    attendance_id: int
    employee_id: int
    employee_email: str
    employee_name: Optional[str] = None
    date: str
    check_in: Optional[str] = None
    check_out: Optional[str] = None
    status: str  # present, absent, late, half_day
    hours_worked: Optional[float] = None
    notes: Optional[str] = None


class AttendanceEvent(BaseEvent):
    """Attendance tracking event."""
    
    data: AttendanceEventData


# ============================================================================
# Compliance Events
# ============================================================================

class ComplianceEventData(BaseModel):
    """Data payload for compliance-related events."""
    
    compliance_check_id: Optional[int] = None
    check_type: str
    resource_type: str
    resource_id: int
    status: str  # passed, failed, warning
    violations: Optional[list] = None
    recommendations: Optional[list] = None
    severity: str = "medium"  # low, medium, high, critical


class ComplianceEvent(BaseEvent):
    """Compliance check event."""
    
    data: ComplianceEventData


# ============================================================================
# Event Factory Functions
# ============================================================================

def create_notification_event(
    source_service: str,
    recipient_email: str,
    subject: str,
    template_name: str,
    template_data: Dict[str, Any],
    event_type: EventType = EventType.USER_CREATED,
    recipient_name: Optional[str] = None,
    priority: str = "normal",
    correlation_id: Optional[str] = None,
) -> NotificationEvent:
    """Create a notification event."""
    import uuid
    
    return NotificationEvent(
        event_id=str(uuid.uuid4()),
        event_type=event_type,
        source_service=source_service,
        correlation_id=correlation_id,
        data=NotificationEventData(
            recipient_email=recipient_email,
            recipient_name=recipient_name,
            subject=subject,
            template_name=template_name,
            template_data=template_data,
            priority=priority,
        ),
    )


def create_audit_event(
    source_service: str,
    user_id: int,
    action: str,
    resource_type: str,
    resource_id: int,
    event_type: EventType = EventType.AUDIT_USER_ACTION,
    description: Optional[str] = None,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None,
    old_value: Optional[str] = None,
    new_value: Optional[str] = None,
    changes: Optional[Dict[str, Any]] = None,
    correlation_id: Optional[str] = None,
) -> AuditEvent:
    """Create an audit event."""
    import uuid
    
    return AuditEvent(
        event_id=str(uuid.uuid4()),
        event_type=event_type,
        source_service=source_service,
        correlation_id=correlation_id,
        data=AuditEventData(
            user_id=user_id,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            description=description,
            ip_address=ip_address,
            user_agent=user_agent,
            old_value=old_value,
            new_value=new_value,
            changes=changes,
        ),
    )
