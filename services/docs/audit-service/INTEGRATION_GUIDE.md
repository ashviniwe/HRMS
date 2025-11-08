# Audit Service - Integration Guide

## Overview

The Audit Service is a centralized microservice designed to capture and manage audit logs across all HRMS microservices. This guide provides detailed instructions for integrating any microservice with the Audit Service.

## Table of Contents

1. [Quick Start](#quick-start)
2. [Service Configuration](#service-configuration)
3. [Python Integration](#python-integration)
4. [JavaScript/Node.js Integration](#javascriptnodejs-integration)
5. [Go Integration](#go-integration)
6. [Common Patterns](#common-patterns)
7. [Error Handling](#error-handling)
8. [Testing](#testing)
9. [Compliance & Security](#compliance--security)
10. [Troubleshooting](#troubleshooting)

---

## Quick Start

### Prerequisites

- Your microservice is running on FastAPI, Express, Django, or similar framework
- Network connectivity to the Audit Service
- JWT token for authentication (if required)

### 3-Minute Setup

1. **Get the Audit Service URL**
   ```
   AUDIT_SERVICE_URL=http://audit-service:8000/api/v1
   ```

2. **Create a helper function** (see language-specific examples below)

3. **Call the helper in your endpoints**
   ```python
   await log_audit_event(
       user_id=current_user.sub,
       action="created",
       log_type="leave_request",
       entity_type="LeaveRequest",
       entity_id=str(leave_request.id),
       service_name="leave-management-service"
   )
   ```

Done! Your events are now being audited.

---

## Service Configuration

### Environment Variables

Add these to your `.env` file:

```env
# Audit Service Configuration
AUDIT_SERVICE_URL=http://audit-service:8000/api/v1
AUDIT_SERVICE_ENABLED=True
AUDIT_SERVICE_TIMEOUT=5.0
AUDIT_SERVICE_RETRIES=3
AUDIT_LOG_LEVEL=INFO

# Service Identification
SERVICE_NAME=leave-management-service
SERVICE_VERSION=1.0.0
```

### Load Configuration

```python
# config.py
from pydantic_settings import BaseSettings

class AuditConfig(BaseSettings):
    audit_service_url: str = "http://audit-service:8000/api/v1"
    audit_service_enabled: bool = True
    audit_service_timeout: float = 5.0
    audit_service_retries: int = 3
    audit_log_level: str = "INFO"
    service_name: str = "unknown-service"
    service_version: str = "1.0.0"

    class Config:
        env_file = ".env"
        case_sensitive = False

audit_config = AuditConfig()
```

---

## Python Integration

### Method 1: Using httpx (Recommended for async services)

```python
# audit_client.py
import httpx
import json
import logging
from typing import Optional, Dict, Any, List
from datetime import datetime
from enum import Enum
from contextlib import asynccontextmanager

logger = logging.getLogger(__name__)


class AuditLogType(str, Enum):
    """Audit log type enumeration matching the backend"""
    LEAVE_REQUEST = "leave_request"
    LEAVE_APPROVAL = "leave_approval"
    ATTENDANCE = "attendance"
    PAYROLL = "payroll"
    EMPLOYEE_UPDATE = "employee_update"
    EMPLOYEE_CREATE = "employee_create"
    EMPLOYEE_DELETE = "employee_delete"
    POLICY_UPDATE = "policy_update"
    POLICY_CREATE = "policy_create"
    POLICY_DELETE = "policy_delete"
    DOCUMENT_UPLOAD = "document_upload"
    DOCUMENT_DELETE = "document_delete"
    ROLE_ASSIGNMENT = "role_assignment"
    PERMISSION_CHANGE = "permission_change"
    LOGIN = "login"
    LOGOUT = "logout"
    EXPORT = "export"
    IMPORT = "import"
    OTHER = "other"


class AuditClient:
    """
    AsyncIO-based client for Audit Service.
    Handles all audit logging operations with retry logic and error handling.
    """

    def __init__(
        self,
        base_url: str,
        timeout: float = 5.0,
        retries: int = 3,
        raise_on_error: bool = False,
    ):
        """
        Initialize the Audit Client.

        Args:
            base_url: Base URL of Audit Service
            timeout: Request timeout in seconds
            retries: Number of retry attempts
            raise_on_error: Whether to raise exceptions on audit failures
        """
        self.base_url = base_url
        self.timeout = timeout
        self.retries = retries
        self.raise_on_error = raise_on_error

    @asynccontextmanager
    async def _get_client(self):
        """Context manager for HTTP client"""
        async with httpx.AsyncClient(
            base_url=self.base_url,
            timeout=self.timeout,
            follow_redirects=True,
        ) as client:
            yield client

    async def create_log(
        self,
        user_id: str,
        action: str,
        log_type: AuditLogType,
        entity_type: str,
        entity_id: str,
        service_name: str,
        status: str = "success",
        description: Optional[str] = None,
        old_values: Optional[Dict[str, Any]] = None,
        new_values: Optional[Dict[str, Any]] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        request_id: Optional[str] = None,
        error_message: Optional[str] = None,
    ) -> Optional[Dict[str, Any]]:
        """
        Create an audit log entry in the Audit Service.

        Args:
            user_id: ID of the user performing the action
            action: Action name (e.g., "created", "updated", "deleted")
            log_type: Category of audit log
            entity_type: Type of entity affected (e.g., "LeaveRequest")
            entity_id: ID of the entity affected
            service_name: Name of the calling service
            status: "success" or "failure"
            description: Human-readable description
            old_values: Previous state (dict)
            new_values: New state (dict)
            ip_address: Client IP address
            user_agent: Client user agent string
            request_id: Request ID for correlation
            error_message: Error details if status is "failure"

        Returns:
            Created audit log dict, or None if failed
        """
        payload = {
            "user_id": user_id,
            "action": action,
            "log_type": log_type.value if isinstance(log_type, AuditLogType) else log_type,
            "entity_type": entity_type,
            "entity_id": entity_id,
            "service_name": service_name,
            "status": status,
            "description": description,
            "old_values": json.dumps(old_values) if old_values else None,
            "new_values": json.dumps(new_values) if new_values else None,
            "ip_address": ip_address,
            "user_agent": user_agent,
            "request_id": request_id,
            "error_message": error_message,
        }

        # Remove None values
        payload = {k: v for k, v in payload.items() if v is not None}

        for attempt in range(self.retries):
            try:
                async with self._get_client() as client:
                    response = await client.post("/audit-logs", json=payload)
                    response.raise_for_status()
                    logger.info(f"Audit log created: {action} on {entity_type}")
                    return response.json()
            except httpx.TimeoutException:
                logger.warning(
                    f"Audit log timeout (attempt {attempt + 1}/{self.retries}): {action}"
                )
                if attempt == self.retries - 1 and self.raise_on_error:
                    raise
            except httpx.HTTPError as e:
                logger.error(f"Audit log HTTP error: {str(e)}")
                if attempt == self.retries - 1 and self.raise_on_error:
                    raise
            except Exception as e:
                logger.error(f"Unexpected error creating audit log: {str(e)}")
                if attempt == self.retries - 1 and self.raise_on_error:
                    raise

        return None

    async def get_user_logs(
        self,
        user_id: str,
        limit: int = 100,
        offset: int = 0,
        log_type: Optional[AuditLogType] = None,
    ) -> Optional[Dict[str, Any]]:
        """
        Retrieve audit logs for a specific user.

        Args:
            user_id: User ID to query
            limit: Maximum records to return
            offset: Number of records to skip
            log_type: Filter by log type (optional)

        Returns:
            Paginated list of audit logs
        """
        try:
            params = {
                "limit": min(limit, 1000),
                "offset": offset,
            }
            if log_type:
                params["log_type"] = log_type.value if isinstance(log_type, AuditLogType) else log_type

            async with self._get_client() as client:
                response = await client.get(
                    f"/audit-logs/user/{user_id}",
                    params=params,
                )
                response.raise_for_status()
                return response.json()
        except Exception as e:
            logger.error(f"Failed to get user logs: {str(e)}")
            if self.raise_on_error:
                raise
            return None

    async def get_logs_by_type(
        self,
        log_type: AuditLogType,
        limit: int = 100,
        offset: int = 0,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> Optional[Dict[str, Any]]:
        """
        Retrieve audit logs by type.

        Args:
            log_type: Type of logs to retrieve
            limit: Maximum records to return
            offset: Number of records to skip
            start_date: Start date filter
            end_date: End date filter

        Returns:
            Paginated list of audit logs
        """
        try:
            params = {
                "limit": min(limit, 1000),
                "offset": offset,
            }
            if start_date:
                params["start_date"] = start_date.isoformat()
            if end_date:
                params["end_date"] = end_date.isoformat()

            async with self._get_client() as client:
                response = await client.get(
                    f"/audit-logs/type/{log_type.value}",
                    params=params,
                )
                response.raise_for_status()
                return response.json()
        except Exception as e:
            logger.error(f"Failed to get logs by type: {str(e)}")
            if self.raise_on_error:
                raise
            return None

    async def get_log_by_id(self, audit_id: int) -> Optional[Dict[str, Any]]:
        """Get a specific audit log by ID"""
        try:
            async with self._get_client() as client:
                response = await client.get(f"/audit-logs/{audit_id}")
                response.raise_for_status()
                return response.json()
        except Exception as e:
            logger.error(f"Failed to get audit log {audit_id}: {str(e)}")
            if self.raise_on_error:
                raise
            return None


# Global instance
_audit_client: Optional[AuditClient] = None


def get_audit_client(
    base_url: str = None,
    timeout: float = 5.0,
    retries: int = 3,
) -> AuditClient:
    """Get or create the global audit client instance"""
    global _audit_client
    if _audit_client is None:
        from app.core.config import settings
        _audit_client = AuditClient(
            base_url=base_url or settings.AUDIT_SERVICE_URL,
            timeout=timeout,
            retries=retries,
        )
    return _audit_client
```

### Usage in FastAPI Endpoints

```python
# routers/leave_requests.py
from fastapi import APIRouter, HTTPException, Request, Depends
from typing import Annotated
from audit_client import get_audit_client, AuditLogType
from app.core.security import CurrentUser

router = APIRouter(prefix="/leave-requests", tags=["leave"])


@router.post("/")
async def create_leave_request(
    request: Request,
    leave_data: LeaveRequestCreate,
    current_user: CurrentUser,
    session: SessionDep,
):
    """Create a new leave request with audit logging"""
    
    audit_client = get_audit_client()
    
    try:
        # Create the leave request
        db_leave = LeaveRequest(**leave_data.dict())
        session.add(db_leave)
        session.commit()
        session.refresh(db_leave)

        # Log successful creation
        await audit_client.create_log(
            user_id=current_user.sub,
            action="created",
            log_type=AuditLogType.LEAVE_REQUEST,
            entity_type="LeaveRequest",
            entity_id=str(db_leave.id),
            service_name="leave-management-service",
            status="success",
            description=f"Leave request created for {leave_data.days} days starting {leave_data.start_date}",
            new_values={
                "employee_id": db_leave.employee_id,
                "start_date": db_leave.start_date.isoformat(),
                "end_date": db_leave.end_date.isoformat(),
                "days": db_leave.days,
                "status": db_leave.status,
                "reason": db_leave.reason,
            },
            ip_address=request.client.host if request.client else None,
            user_agent=request.headers.get("user-agent"),
            request_id=request.headers.get("x-request-id"),
        )

        return db_leave

    except Exception as e:
        # Log failure
        await audit_client.create_log(
            user_id=current_user.sub,
            action="create_failed",
            log_type=AuditLogType.LEAVE_REQUEST,
            entity_type="LeaveRequest",
            entity_id="unknown",
            service_name="leave-management-service",
            status="failure",
            description="Failed to create leave request",
            error_message=str(e),
            ip_address=request.client.host if request.client else None,
            user_agent=request.headers.get("user-agent"),
            request_id=request.headers.get("x-request-id"),
        )
        raise HTTPException(status_code=400, detail=str(e))


@router.patch("/{leave_id}")
async def update_leave_request(
    request: Request,
    leave_id: int,
    update_data: LeaveRequestUpdate,
    current_user: CurrentUser,
    session: SessionDep,
):
    """Update a leave request with change tracking"""
    
    audit_client = get_audit_client()
    
    try:
        db_leave = session.get(LeaveRequest, leave_id)
        if not db_leave:
            raise HTTPException(status_code=404, detail="Leave request not found")

        # Capture old values
        old_values = {
            "status": db_leave.status,
            "start_date": db_leave.start_date.isoformat(),
            "end_date": db_leave.end_date.isoformat(),
            "reason": db_leave.reason,
        }

        # Update the request
        update_dict = update_data.dict(exclude_unset=True)
        for key, value in update_dict.items():
            setattr(db_leave, key, value)

        session.add(db_leave)
        session.commit()
        session.refresh(db_leave)

        # Log the update with both old and new values
        await audit_client.create_log(
            user_id=current_user.sub,
            action="updated",
            log_type=AuditLogType.LEAVE_REQUEST,
            entity_type="LeaveRequest",
            entity_id=str(leave_id),
            service_name="leave-management-service",
            status="success",
            description=f"Leave request {leave_id} updated",
            old_values=old_values,
            new_values=update_dict,
            ip_address=request.client.host if request.client else None,
            user_agent=request.headers.get("user-agent"),
            request_id=request.headers.get("x-request-id"),
        )

        return db_leave

    except HTTPException:
        raise
    except Exception as e:
        await audit_client.create_log(
            user_id=current_user.sub,
            action="update_failed",
            log_type=AuditLogType.LEAVE_REQUEST,
            entity_type="LeaveRequest",
            entity_id=str(leave_id),
            service_name="leave-management-service",
            status="failure",
            error_message=str(e),
            ip_address=request.client.host if request.client else None,
            user_agent=request.headers.get("user-agent"),
        )
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{leave_id}")
async def delete_leave_request(
    request: Request,
    leave_id: int,
    current_user: CurrentUser,
    session: SessionDep,
):
    """Delete a leave request with audit logging"""
    
    audit_client = get_audit_client()
    
    try:
        db_leave = session.get(LeaveRequest, leave_id)
        if not db_leave:
            raise HTTPException(status_code=404, detail="Leave request not found")

        # Capture values before deletion
        old_values = {
            "id": db_leave.id,
            "status": db_leave.status,
            "days": db_leave.days,
            "reason": db_leave.reason,
        }

        session.delete(db_leave)
        session.commit()

        # Log the deletion
        await audit_client.create_log(
            user_id=current_user.sub,
            action="deleted",
            log_type=AuditLogType.LEAVE_REQUEST,
            entity_type="LeaveRequest",
            entity_id=str(leave_id),
            service_name="leave-management-service",
            status="success",
            description=f"Leave request {leave_id} deleted",
            old_values=old_values,
            ip_address=request.client.host if request.client else None,
            user_agent=request.headers.get("user-agent"),
            request_id=request.headers.get("x-request-id"),
        )

        return {"ok": True}

    except HTTPException:
        raise
    except Exception as e:
        await audit_client.create_log(
            user_id=current_user.sub,
            action="delete_failed",
            log_type=AuditLogType.LEAVE_REQUEST,
            entity_type="LeaveRequest",
            entity_id=str(leave_id),
            service_name="leave-management-service",
            status="failure",
            error_message=str(e),
        )
        raise HTTPException(status_code=400, detail=str(e))
```

### Method 2: Using requests (For synchronous services)

```python
# audit_client_sync.py
import requests
import json
import logging
from typing import Optional, Dict, Any
from enum import Enum

logger = logging.getLogger(__name__)


class AuditClient:
    """Synchronous client for Audit Service"""

    def __init__(
        self,
        base_url: str,
        timeout: float = 5.0,
        retries: int = 3,
    ):
        self.base_url = base_url
        self.timeout = timeout
        self.retries = retries

    def create_log(
        self,
        user_id: str,
        action: str,
        log_type: str,
        entity_type: str,
        entity_id: str,
        service_name: str,
        **kwargs
    ) -> Optional[Dict[str, Any]]:
        """Create an audit log entry"""
        
        payload = {
            "user_id": user_id,
            "action": action,
            "log_type": log_type,
            "entity_type": entity_type,
            "entity_id": entity_id,
            "service_name": service_name,
            **kwargs
        }

        # JSON encode complex fields
        if "old_values" in payload and isinstance(payload["old_values"], dict):
            payload["old_values"] = json.dumps(payload["old_values"])
        if "new_values" in payload and isinstance(payload["new_values"], dict):
            payload["new_values"] = json.dumps(payload["new_values"])

        for attempt in range(self.retries):
            try:
                response = requests.post(
                    f"{self.base_url}/audit-logs",
                    json=payload,
                    timeout=self.timeout,
                )
                response.raise_for_status()
                logger.info(f"Audit log created: {action}")
                return response.json()
            except requests.Timeout:
                logger.warning(f"Audit log timeout (attempt {attempt + 1})")
            except requests.RequestException as e:
                logger.error(f"Audit log request error: {str(e)}")

        return None
```

---

## JavaScript/Node.js Integration

### Using Axios

```javascript
// auditClient.js
import axios from 'axios';

class AuditLogType {
    static LEAVE_REQUEST = 'leave_request';
    static LEAVE_APPROVAL = 'leave_approval';
    static ATTENDANCE = 'attendance';
    static PAYROLL = 'payroll';
    static EMPLOYEE_UPDATE = 'employee_update';
    static EMPLOYEE_CREATE = 'employee_create';
    static EMPLOYEE_DELETE = 'employee_delete';
    static OTHER = 'other';
}

class AuditClient {
    constructor(baseUrl, options = {}) {
        this.baseUrl = baseUrl;
        this.timeout = options.timeout || 5000;
        this.retries = options.retries || 3;
        this.raiseOnError = options.raiseOnError || false;

        this.client = axios.create({
            baseURL: this.baseUrl,
            timeout: this.timeout,
        });
    }

    async createLog({
        userId,
        action,
        logType,
        entityType,
        entityId,
        serviceName,
        status = 'success',
        description = null,
        oldValues = null,
        newValues = null,
        ipAddress = null,
        userAgent = null,
        requestId = null,
        errorMessage = null,
    }) {
        const payload = {
            user_id: userId,
            action,
            log_type: logType,
            entity_type: entityType,
            entity_id: entityId,
            service_name: serviceName,
            status,
            description,
            old_values: oldValues ? JSON.stringify(oldValues) : null,
            new_values: newValues ? JSON.stringify(newValues) : null,
            ip_address: ipAddress,
            user_agent: userAgent,
            request_id: requestId,
            error_message: errorMessage,
        };

        // Remove null values
        Object.keys(payload).forEach(key => 
            payload[key] === null && delete payload[key]
        );

        for (let attempt = 0; attempt < this.retries; attempt++) {
            try {
                const response = await this.client.post('/audit-logs', payload);
                console.log(`Audit log created: ${action}`);
                return response.data;
            } catch (error) {
                if (error.code === 'ECONNABORTED') {
                    console.warn(`Audit timeout (attempt ${attempt + 1})`);
                } else {
                    console.error(`Audit error: ${error.message}`);
                }

                if (attempt === this.retries - 1 && this.raiseOnError) {
                    throw error;
                }
            }
        }

        return null;
    }

    async getUserLogs(userId, options = {}) {
        try {
            const response = await this.client.get(`/audit-logs/user/${userId}`, {
                params: {
                    limit: Math.min(options.limit || 100, 1000),
                    offset: options.offset || 0,
                    log_type: options.logType,
                }
            });
            return response.data;
        } catch (error) {
            console.error(`Failed to get user logs: ${error.message}`);
            if (this.raiseOnError) throw error;
            return null;
        }
    }

    async getLogsByType(logType, options = {}) {
        try {
            const response = await this.client.get(`/audit-logs/type/${logType}`, {
                params: {
                    limit: Math.min(options.limit || 100, 1000),
                    offset: options.offset || 0,
                    start_date: options.startDate,
                    end_date: options.endDate,
                }
            });
            return response.data;
        } catch (error) {
            console.error(`Failed to get logs by type: ${error.message}`);
            if (this.raiseOnError) throw error;
            return null;
        }
    }
}

export { AuditClient, AuditLogType };
```

### Using in Express Routes

```javascript
// routes/leaveRequests.js
import express from 'express';
import { AuditClient, AuditLogType } from '../auditClient.js';

const router = express.Router();
const auditClient = new AuditClient(process.env.AUDIT_SERVICE_URL);

router.post('/', async (req, res) => {
    try {
        const { leaveData } = req.body;
        const userId = req.user.id;

        // Create leave request
        const leaveRequest = await LeaveRequest.create(leaveData);

        // Log to audit service
        await auditClient.createLog({
            userId,
            action: 'created',
            logType: AuditLogType.LEAVE_REQUEST,
            entityType: 'LeaveRequest',
            entityId: leaveRequest.id.toString(),
            serviceName: 'leave-management-service',
            status: 'success',
            description: `Leave request created for ${leaveData.days} days`,
            newValues: leaveRequest.toJSON(),
            ipAddress: req.ip,
            userAgent: req.headers['user-agent'],
            requestId: req.headers['x-request-id'],
        });

        res.json(leaveRequest);
    } catch (error) {
        // Log failure
        await auditClient.createLog({
            userId: req.user.id,
            action: 'create_failed',
            logType: AuditLogType.LEAVE_REQUEST,
            entityType: 'LeaveRequest',
            entityId: 'unknown',
            serviceName: 'leave-management-service',
            status: 'failure',
            errorMessage: error.message,
        });

        res.status(400).json({ error: error.message });
    }
});

router.patch('/:id', async (req, res) => {
    try {
        const leaveId = req.params.id;
        const { updateData } = req.body;
        const userId = req.user.id;

        const leaveRequest = await LeaveRequest.findById(leaveId);
        if (!leaveRequest) {
            return res.status(404).json({ error: 'Not found' });
        }

        // Capture old values
        const oldValues = leaveRequest.toJSON();

        // Update
        Object.assign(leaveRequest, updateData);
        await leaveRequest.save();

        // Log the update
        await auditClient.createLog({
            userId,
            action: 'updated',
            logType: AuditLogType.LEAVE_REQUEST,
            entityType: 'LeaveRequest',
            entityId: leaveId,
            serviceName: 'leave-management-service',
            status: 'success',
            description: `Leave request ${leaveId} updated`,
            oldValues,
            newValues: updateData,
            ipAddress: req.ip,
            userAgent: req.headers['user-agent'],
        });

        res.json(leaveRequest);
    } catch (error) {
        await auditClient.createLog({
            userId: req.user.id,
            action: 'update_failed',
            logType: AuditLogType.LEAVE_REQUEST,
            entityType: 'LeaveRequest',
            entityId: req.params.id,
            serviceName: 'leave-management-service',
            status: 'failure',
            errorMessage: error.message,
        });

        res.status(400).json({ error: error.message });
    }
});

export default router;
```

---

## Go Integration

### Using Go HTTP Client

```go
// audit_client.go
package audit

import (
    "bytes"
    "encoding/json"
    "fmt"
    "io"
    "net/http"
    "time"
)

type LogType string

const (
    LeaveRequest      LogType = "leave_request"
    LeaveApproval     LogType = "leave_approval"
    Attendance        LogType = "attendance"
    Payroll           LogType = "payroll"
    EmployeeUpdate    LogType = "employee_update"
    EmployeeCreate    LogType = "employee_create"
    EmployeeDelete    LogType = "employee_delete"
    PolicyUpdate      LogType = "policy_update"
    PolicyCreate      LogType = "policy_create"
    PolicyDelete      LogType = "policy_delete"
    DocumentUpload    LogType = "document_upload"
    DocumentDelete    LogType = "document_delete"
    RoleAssignment    LogType = "role_assignment"
    PermissionChange  LogType = "permission_change"
    Login             LogType = "login"
    Logout            LogType = "logout"
    Export            LogType = "export"
    Import            LogType = "import"
    Other             LogType = "other"
)

type CreateLogRequest struct {
    UserID       string                 `json:"user_id"`
    Action       string                 `json:"action"`
    LogType      LogType                `json:"log_type"`
    EntityType   string                 `json:"entity_type"`
    EntityID     string                 `json:"entity_id"`
    ServiceName  string                 `json:"service_name"`
    Status       string                 `json:"status"`
    Description  *string                `json:"description,omitempty"`
    OldValues    *string                `json:"old_values,omitempty"`
    NewValues    *string                `json:"new_values,omitempty"`
    IPAddress    *string                `json:"ip_address,omitempty"`
    UserAgent    *string                `json:"user_agent,omitempty"`
    RequestID    *string                `json:"request_id,omitempty"`
    ErrorMessage *string                `json:"error_message,omitempty"`
}

type Client struct {
    baseURL    string
    httpClient *http.Client
    timeout    time.Duration
    retries    int
}

func NewClient(baseURL string, options ...func(*Client)) *Client {
    c := &Client{
        baseURL: baseURL,
        httpClient: &http.Client{},
        timeout: 5 * time.Second,
        retries: 3,
    }

    for _, opt := range options {
        opt(c)
    }

    return c
}

func WithTimeout(timeout time.Duration) func(*Client) {
    return func(c *Client) {
        c.timeout = timeout
    }
}

func WithRetries(retries int) func(*Client) {
    return func(c *Client) {
        c.retries = retries
    }
}

func (c *Client) CreateLog(req CreateLogRequest) (map[string]interface{}, error) {
    payload, err := json.Marshal(req)
    if err != nil {
        return nil, fmt.Errorf("failed to marshal request: %w", err)
    }

    var lastErr error
    for attempt := 0; attempt < c.retries; attempt++ {
        resp, err := c.httpClient.Post(
            fmt.Sprintf("%s/audit-logs", c.baseURL),
            "application/json",
            bytes.NewReader(payload),
        )

        if err != nil {
            lastErr = err
            continue
        }

        defer resp.Body.Close()

        if resp.StatusCode >= 200 && resp.StatusCode < 300 {
            var result map[string]interface{}
            if err := json.NewDecoder(resp.Body).Decode(&result); err != nil {
                return nil, fmt.Errorf("failed to decode response: %w", err)
            }
            return result, nil
        }

        body, _ := io.ReadAll(resp.Body)
        lastErr = fmt.Errorf("audit service returned %d: %s", resp.StatusCode, string(body))
    }

    return nil, fmt.Errorf("failed after %d retries: %w", c.retries, lastErr)
}

func (c *Client) GetUserLogs(userID string, limit, offset int) (map[string]interface{}, error) {
    url := fmt.Sprintf("%s/audit-logs/user/%s?limit=%d&offset=%d", c.baseURL, userID, limit, offset)
    
    resp, err := c.httpClient.Get(url)
    if err != nil {
        return nil, fmt.Errorf("request failed: %w", err)
    }
    defer resp.Body.Close()

    var result map[string]interface{}
    if err := json.NewDecoder(resp.Body).Decode(&result); err != nil {
        return nil, fmt.Errorf("failed to decode response: %w", err)
    }

    return result, nil
}
```

### Using in Gin Routes

```go
// routes/leave.go
package routes

import (
    "github.com/gin-gonic/gin"
    "your-module/audit"
)

var auditClient = audit.NewClient(
    "http://audit-service:8000/api/v1",
    audit.WithTimeout(5*time.Second),
    audit.WithRetries(3),
)

func CreateLeaveRequest(c *gin.Context) {
    userID := c.GetString("user_id")
    
    var req LeaveRequest
    if err := c.ShouldBindJSON(&req); err != nil {
        c.JSON(400, gin.H{"error": err.Error()})
        return
    }

    // Create leave request
    leaveReq := &LeaveRequest{...}
    if err := db.Create(leaveReq).Error; err != nil {
        // Log failure
        auditClient.CreateLog(audit.CreateLogRequest{
            UserID:       userID,
            Action:       "create_failed",
            LogType:      audit.LeaveRequest,
            EntityType:   "LeaveRequest",
            EntityID:     "unknown",
            ServiceName:  "leave-management-service",
            Status:       "failure",
            ErrorMessage: ptrString(err.Error()),
        })

        c.JSON(500, gin.H{"error": err.Error()})
        return
    }

    // Log success
    newVals, _ := json.Marshal(leaveReq)
    auditClient.CreateLog(audit.CreateLogRequest{
        UserID:      userID,
        Action:      "created",
        LogType:     audit.LeaveRequest,
        EntityType:  "LeaveRequest",
        EntityID:    fmt.Sprint(leaveReq.ID),
        ServiceName: "leave-management-service",
        Status:      "success",
        NewValues:   ptrString(string(newVals)),
        IPAddress:   ptrString(c.ClientIP()),
        UserAgent:   ptrString(c.Request.UserAgent()),
    })

    c.JSON(201, leaveReq)
}

func ptrString(s string) *string {
    return &s
}
```

---

## Common Patterns

### Pattern 1: Wrapping Database Operations

```python
# patterns.py
from contextlib import asynccontextmanager
from audit_client import get_audit_client, AuditLogType

@asynccontextmanager
async def audit_create(user_id, entity_type, service_name, **context):
    """Context manager for audited creation"""
    audit_client = get_audit_client()
    try:
        yield
        await audit_client.create_log(
            user_id=user_id,
            action="created",
            log_type=context.get("log_type", AuditLogType.OTHER),
            entity_type=entity_type,
            entity_id=context.get("entity_id"),
            service_name=service_name,
            status="success",
            new_values=context.get("new_values"),
        )
    except Exception as e:
        await audit_client.create_log(
            user_id=user_id,
            action="create_failed",
            log_type=context.get("log_type", AuditLogType.OTHER),
            entity_type=entity_type,
            entity_id=context.get("entity_id", "unknown"),
            service_name=service_name,
            status="failure",
            error_message=str(e),
        )
        raise

# Usage
async def create_leave_request(leave_data, user_id):
    async with audit_create(
        user_id=user_id,
        entity_type="LeaveRequest",
        service_name="leave-management-service",
        log_type=AuditLogType.LEAVE_REQUEST,
    ) as context:
        leave = LeaveRequest(**leave_data.dict())
        session.add(leave)
        session.commit()
        context["entity_id"] = str(leave.id)
        context["new_values"] = leave.dict()
```

### Pattern 2: Middleware for Automatic Logging

```python
# middleware.py
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from audit_client import get_audit_client

class AuditLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Only log state-changing operations
        if request.method in ["POST", "PUT", "PATCH", "DELETE"]:
            audit_client = get_audit_client()
            
            # Log the action
            await audit_client.create_log(
                user_id=request.scope.get("user_id", "anonymous"),
                action=request.method.lower(),
                log_type="api_call",
                entity_type=request.url.path,
                entity_id=request.url.path,
                service_name="api-gateway",
                ip_address=request.client.host if request.client else None,
                user_agent=request.headers.get("user-agent"),
                request_id=request.headers.get("x-request-id"),
            )
        
        response = await call_next(request)
        return response

# In main.py
app.add_middleware(AuditLoggingMiddleware)
```

---

## Error Handling

### Graceful Degradation

The audit service should never break your main business logic:

```python
async def safe_audit_log(**kwargs):
    """Create audit log with graceful failure"""
    audit_client = get_audit_client()
    try:
        return await audit_client.create_log(**kwargs)
    except Exception as e:
        logger.error(f"Failed to log audit: {str(e)}", exc_info=True)
        # Send alert to ops team
        send_alert_to_ops(f"Audit logging failed: {str(e)}")
        # Don't raise - let business logic continue
        return None
```

### Retry Logic with Exponential Backoff

```python
import asyncio

async def audit_log_with_backoff(**kwargs):
    """Create audit log with exponential backoff"""
    audit_client = get_audit_client()
    max_retries = 5
    base_delay = 0.1
    
    for attempt in range(max_retries):
        try:
            return await audit_client.create_log(**kwargs)
        except Exception as e:
            if attempt == max_retries - 1:
                logger.error(f"Audit logging failed after {max_retries} attempts")
                return None
            
            delay = base_delay * (2 ** attempt)
            logger.warning(f"Audit logging failed, retrying in {delay}s")
            await asyncio.sleep(delay)
```

---

## Testing

### Unit Testing

```python
# tests/test_audit_integration.py
import pytest
from unittest.mock import AsyncMock, patch
from audit_client import AuditClient, AuditLogType

@pytest.mark.asyncio
async def test_create_log():
    """Test creating an audit log"""
    with patch('httpx.AsyncClient.post') as mock_post:
        mock_post.return_value.json.return_value = {"id": 1}
        
        client = AuditClient("http://localhost:8000/api/v1")
        result = await client.create_log(
            user_id="test_user",
            action="created",
            log_type=AuditLogType.LEAVE_REQUEST,
            entity_type="LeaveRequest",
            entity_id="123",
            service_name="test-service",
        )
        
        assert result["id"] == 1
        mock_post.assert_called_once()
```

### Integration Testing

```python
# tests/test_integration.py
import pytest
from httpx import AsyncClient
from app.main import app

@pytest.mark.asyncio
async def test_create_and_retrieve_audit_log():
    """Test end-to-end audit logging"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        # Create log
        response = await client.post("/api/v1/audit-logs", json={
            "user_id": "user123",
            "action": "created",
            "log_type": "leave_request",
            "entity_type": "LeaveRequest",
            "entity_id": "leave456",
            "service_name": "test-service",
        })
        
        assert response.status_code == 201
        log_id = response.json()["id"]
        
        # Retrieve log
        response = await client.get(f"/api/v1/audit-logs/{log_id}")
        assert response.status_code == 200
        assert response.json()["id"] == log_id
```

---

## Compliance & Security

### Data Sensitivity Guidelines

1. **Never log passwords or secrets**
   ```python
   # Bad
   new_values = {"password": user_password}
   
   # Good
   new_values = {"username": username}  # Only non-sensitive data
   ```

2. **Mask PII in descriptions**
   ```python
   # Bad
   description = f"Employee {emp.ssn} updated"
   
   # Good
   description = f"Employee {emp.id} updated"
   ```

3. **Use old_values and new_values carefully**
   ```python
   # Only log relevant changes
   old_values = {"department": "HR"}
   new_values = {"department": "Finance"}
   ```

### GDPR Compliance

- Right to be forgotten: Use the DELETE endpoint to remove user's audit logs if requested
- Data minimization: Only log necessary information
- Purpose limitation: Use audit logs only for auditing and compliance

### Retention Policy

```python
# Set in config
AUDIT_LOG_RETENTION_DAYS = 365  # Default 1 year

# Implement cleanup task
from apscheduler.schedulers.asyncio import AsyncIOScheduler

scheduler = AsyncIOScheduler()

@scheduler.scheduled_job('cron', days=7)
async def cleanup_old_logs():
    """Delete audit logs older than retention period"""
    cutoff_date = datetime.utcnow() - timedelta(days=AUDIT_LOG_RETENTION_DAYS)
    # DELETE FROM audit_logs WHERE timestamp < cutoff_date
```

---

## Troubleshooting

### Issue: "Connection refused" error

**Cause**: Audit service is not running or not accessible

**Solution**:
```bash
# Check if service is running
curl http://audit-service:8000/health

# Check DNS resolution
nslookup audit-service
ping audit-service

# Check firewall rules
telnet audit-service 8000
```

### Issue: Audit logs not appearing

**Cause**: Service configuration or network issue

**Solution**:
1. Verify `AUDIT_SERVICE_URL` is correct
2. Check service logs: `docker logs audit-service`
3. Enable debug logging in your service
4. Test connectivity: `curl -X POST http://audit-service:8000/api/v1/audit-logs ...`

### Issue: Timeouts on audit logging

**Cause**: Audit service is overloaded or database is slow

**Solution**:
1. Increase timeout: `AuditClient(base_url, timeout=10.0)`
2. Implement background task:
   ```python
   from celery import shared_task
   
   @shared_task
   def log_audit_async(**kwargs):
       audit_client.create_log(**kwargs)
   ```
3. Contact ops team to scale audit service

---

**Last Updated**: January 2024  
**Version**: 1.0.0