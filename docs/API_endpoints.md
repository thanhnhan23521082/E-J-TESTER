# ETEST ONE API Endpoints Documentation

> **Version:** 1.0.0
> **Last Updated:** 2026-03-21
> **Base URL:** `http://localhost:3000/api` (default)

This document describes all API endpoints required by the ETEST ONE frontend application, organized by user role.

---

## Table of Contents

1. [Overview](#overview)
2. [Authentication](#authentication)
3. [Common Response Format](#common-response-format)
4. [Error Handling](#error-handling)
5. [Student API](#student-api)
6. [Parent API](#parent-api)
7. [Mentor API](#mentor-api)
8. [Shared API](#shared-api)
9. [Data Models](#data-models)
10. [Frontend Integration](#frontend-integration)

---

## Overview

### Architecture

The API layer is organized by user role for clear separation of concerns:

```
src/api/
├── types.ts          # Common API types (ApiResponse, ApiConfig)
├── client.ts         # Base HTTP client with GET/POST methods
├── index.ts          # Barrel exports
├── student/          # Student-specific endpoints
├── parent/           # Parent-specific endpoints
├── mentor/           # Mentor-specific endpoints
└── shared/           # Shared utilities (all roles)
```

### HTTP Client Configuration

```typescript
interface ApiConfig {
  baseUrl: string      // Default: 'http://localhost:3000/api'
  timeout: number      // Default: 10000ms
  headers: Record<string, string>  // Default: { 'Content-Type': 'application/json' }
}
```

---

## Authentication

> **Note:** Authentication is not yet implemented. The following structure is proposed for future implementation.

### Proposed Auth Flow

```http
POST /auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "********",
  "role": "student" | "parent" | "mentor"
}
```

**Response:**
```json
{
  "data": {
    "token": "jwt_token_here",
    "user": { ... },
    "expiresIn": 3600
  },
  "error": null,
  "status": 200
}
```

### Authorization Header (Future)

```http
Authorization: Bearer <jwt_token>
```

---

## Common Response Format

All API responses follow this standardized envelope format:

```typescript
interface ApiResponse<T> {
  data: T | null       // Response payload (null on error)
  error: string | null // Error message (null on success)
  status: number       // HTTP status code
}
```

### Success Response Example

```json
{
  "data": {
    "id": "student_001",
    "name": "Nguyễn Hà Minh Anh",
    "program": "AMP"
  },
  "error": null,
  "status": 200
}
```

### Error Response Example

```json
{
  "data": null,
  "error": "Student not found",
  "status": 404
}
```

---

## Error Handling

### HTTP Status Codes

| Code | Description |
|------|-------------|
| 200 | Success |
| 201 | Created (for POST requests) |
| 400 | Bad Request - Invalid input |
| 401 | Unauthorized - Authentication required |
| 403 | Forbidden - Insufficient permissions |
| 404 | Not Found - Resource doesn't exist |
| 500 | Internal Server Error |

### Error Response Structure

```json
{
  "data": null,
  "error": "Descriptive error message",
  "status": 400
}
```

---

## Student API

Base path: `/students/{studentId}`

### 1. Get Student Profile

Retrieves the complete student profile including academic information and target schools.

```http
GET /students/{studentId}
```

**Path Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| studentId | string | Yes | Unique student identifier |

**Response:**
```json
{
  "data": {
    "id": "student_001",
    "name": "Nguyễn Hà Minh Anh",
    "program": "AMP",
    "monthsEnrolled": 14,
    "ieltsScore": 6.5,
    "satScore": 1320,
    "gpa": 3.8,
    "skillBreakdown": {
      "L": 7.0,
      "R": 6.5,
      "W": 6.0,
      "S": 6.5
    },
    "targetSchools": [
      {
        "name": "University of Melbourne",
        "country": "Úc",
        "deadline": "2026-05-07",
        "ieltsRequired": 7.0,
        "satRequired": null,
        "daysUntilDeadline": 47,
        "isEligible": false,
        "gapIelts": 0.5,
        "gapSat": null
      }
    ],
    "parentId": "parent_001",
    "mentorId": "mentor_001"
  },
  "error": null,
  "status": 200
}
```

**Frontend Usage:**
- `StudentHome.tsx` - Displays profile header, quick stats
- `StudentEtester.tsx` - Displays student info
- `useStudentData.ts` hook

---

### 2. Get Student Milestones

Retrieves all milestones/achievements for a student.

```http
GET /students/{studentId}/milestones
```

**Path Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| studentId | string | Yes | Unique student identifier |

**Response:**
```json
{
  "data": [
    {
      "id": "ms_001",
      "studentId": "student_001",
      "type": "essay_review",
      "title": "Why I want to study at Melbourne — Draft 2",
      "date": "2026-03-15",
      "score": null,
      "scoreLabel": "",
      "mentorId": "mentor_001",
      "mentorApproved": true,
      "authScore": 91,
      "notes": "Bài viết tốt, giọng văn rõ ràng và nhất quán.",
      "status": "completed",
      "contributorType": "mentor",
      "aiSummary": {
        "summary": "Bài luận Melbourne Draft 2 được mentor xác nhận...",
        "skillsDemonstrated": ["Academic Writing", "Critical Thinking", "Self-reflection"],
        "evidenceStrength": "high"
      }
    }
  ],
  "error": null,
  "status": 200
}
```

**Frontend Usage:**
- `StudentHome.tsx` - Recent achievements section
- `StudentTimeline.tsx` - Full timeline view
- `useStudentData.ts` hook

---

### 3. Get E-Tester Score

Retrieves the ETESTER authenticity and contribution score data.

```http
GET /students/{studentId}/etester
```

**Path Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| studentId | string | Yes | Unique student identifier |

**Response:**
```json
{
  "data": {
    "studentId": "student_001",
    "academicScore": 84,
    "writingGrowth": 72,
    "skills": ["Academic Writing", "Critical Thinking", "Research", "Leadership"],
    "mentorVerifications": 18,
    "parentSupportLevel": "active",
    "institutionalStamp": true,
    "consistencyScore": 91,
    "totalContributions": 23,
    "lastUpdated": "2026-03-21T09:00:00Z",
    "narrativeCache": "Minh Anh đã có 14 tháng học tập kiên trì tại ETEST...",
    "badgeIssued": true
  },
  "error": null,
  "status": 200
}
```

**Frontend Usage:**
- `StudentHome.tsx` - ETESTER Snapshot card
- `StudentEtester.tsx` - Full ETESTER profile
- `EtesterPublic.tsx` - Public verification page
- `useStudentData.ts` hook

---

### 4. Submit Essay

Submits a new essay for review.

```http
POST /students/{studentId}/essays
Content-Type: application/json

{
  "milestoneId": "ms_xxx",
  "content": "Essay content here...",
  "wordCount": 650
}
```

**Path Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| studentId | string | Yes | Unique student identifier |

**Request Body:**
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| milestoneId | string | Yes | Associated milestone ID |
| content | string | Yes | Essay text content |
| wordCount | number | Yes | Word count of essay |

**Response:**
```json
{
  "data": {
    "submissionId": "submission_1711024800000"
  },
  "error": null,
  "status": 201
}
```

**Frontend Usage:**
- `StudentContribute.tsx` - Essay submission form
- `EssayCheck.tsx` - Essay authenticity check

---

## Parent API

Base path: `/parents/{parentId}`

### 1. Get Children

Retrieves all students associated with a parent.

```http
GET /parents/{parentId}/children
```

**Path Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| parentId | string | Yes | Unique parent identifier |

**Response:**
```json
{
  "data": [
    {
      "id": "student_001",
      "name": "Nguyễn Hà Minh Anh",
      "program": "AMP",
      "monthsEnrolled": 14,
      "ieltsScore": 6.5,
      "satScore": 1320,
      "gpa": 3.8,
      "skillBreakdown": { "L": 7.0, "R": 6.5, "W": 6.0, "S": 6.5 },
      "targetSchools": [...],
      "parentId": "parent_001",
      "mentorId": "mentor_001"
    }
  ],
  "error": null,
  "status": 200
}
```

**Frontend Usage:**
- `ParentHome.tsx` - Child selection
- `ParentProfile.tsx` - Children list

---

### 2. Get Wellbeing Alerts

Retrieves wellbeing alerts for a student (behavioral warnings, study patterns).

```http
GET /students/{studentId}/wellbeing
```

**Path Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| studentId | string | Yes | Unique student identifier |

**Response:**
```json
{
  "data": {
    "alert": true,
    "severity": "medium",
    "message": "Minh Anh học muộn 3 đêm liên tiếp tuần này",
    "action": "Nhắn hỏi thăm con tối nay"
  },
  "error": null,
  "status": 200
}
```

**Severity Values:**
- `low` - Minor concern
- `medium` - Moderate concern, attention needed
- `high` - Urgent concern, immediate action required

**Frontend Usage:**
- `ParentHome.tsx` - Wellbeing alert card
- `useStudentData.ts` hook

---

### 3. Get Digest Data

Retrieves the weekly/monthly digest summary for a student.

```http
GET /students/{studentId}/digest
```

**Path Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| studentId | string | Yes | Unique student identifier |

**Response:**
```json
{
  "data": {
    "progressPct": 68,
    "milestonesCompleted": 17,
    "nextDeadline": "University of Melbourne",
    "daysLeft": 47,
    "priorityAction": "Ôn Writing Task 2 trước deadline",
    "weakestSkill": "IELTS Writing"
  },
  "error": null,
  "status": 200
}
```

**Frontend Usage:**
- `ParentHome.tsx` - Weekly summary section, deadline card
- `useStudentData.ts` hook

---

### 4. Send Message to Mentor

Sends a message from parent to mentor.

```http
POST /parents/{parentId}/messages
Content-Type: application/json

{
  "mentorId": "mentor_001",
  "message": "Cảm ơn thầy đã hỗ trợ con em tuần qua."
}
```

**Path Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| parentId | string | Yes | Unique parent identifier |

**Request Body:**
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| mentorId | string | Yes | Target mentor ID |
| message | string | Yes | Message content |

**Response:**
```json
{
  "data": {
    "messageId": "msg_1711024800000"
  },
  "error": null,
  "status": 201
}
```

**Frontend Usage:**
- `ParentChat.tsx` - AI chat (future: direct messaging)
- `ParentProfile.tsx` - Contact mentor

---

### 5. AI Chat (Proposed)

> **Note:** Currently implemented as client-side mock. Backend endpoint proposed for future.

```http
POST /parents/{parentId}/ai-chat
Content-Type: application/json

{
  "studentId": "student_001",
  "message": "Minh Anh đang yếu môn nào?"
}
```

**Response:**
```json
{
  "data": {
    "response": "Dựa trên dữ liệu gần nhất, Minh Anh đang yếu nhất ở kỹ năng Writing...",
    "suggestions": ["Làm sao để cải thiện Writing?", "Tiến độ so với deadline?"]
  },
  "error": null,
  "status": 200
}
```

---

## Mentor API

Base path: `/mentors/{mentorId}`

### 1. Get Mentor Profile

Retrieves mentor profile and assigned students.

```http
GET /mentors/{mentorId}
```

**Path Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| mentorId | string | Yes | Unique mentor identifier |

**Response:**
```json
{
  "data": {
    "id": "mentor_001",
    "name": "Thầy Nguyễn Minh",
    "studentIds": ["student_001"],
    "pendingEssayCount": 3,
    "pendingSessionNoteCount": 2
  },
  "error": null,
  "status": 200
}
```

**Frontend Usage:**
- `MentorHome.tsx` - Mentor greeting, action cards
- `StudentList.tsx` - Student list

---

### 2. Get Assigned Students

Retrieves all students assigned to a mentor.

```http
GET /mentors/{mentorId}/students
```

**Path Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| mentorId | string | Yes | Unique mentor identifier |

**Response:**
```json
{
  "data": [
    {
      "id": "student_001",
      "name": "Nguyễn Hà Minh Anh",
      "program": "AMP",
      "monthsEnrolled": 14,
      "ieltsScore": 6.5,
      "satScore": 1320,
      "gpa": 3.8,
      "skillBreakdown": { "L": 7.0, "R": 6.5, "W": 6.0, "S": 6.5 },
      "targetSchools": [...],
      "parentId": "parent_001",
      "mentorId": "mentor_001"
    }
  ],
  "error": null,
  "status": 200
}
```

**Frontend Usage:**
- `MentorHome.tsx` - Student cards
- `StudentList.tsx` - Full student list
- `MentorEtester.tsx` - Student ETESTER view

---

### 3. Get Pending Essays

Retrieves essays pending mentor review.

```http
GET /mentors/{mentorId}/pending-essays
```

**Path Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| mentorId | string | Yes | Unique mentor identifier |

**Response:**
```json
{
  "data": [
    {
      "id": "ms_001",
      "studentId": "student_001",
      "type": "essay_review",
      "title": "Why I want to study at Melbourne — Draft 2",
      "date": "2026-03-15",
      "status": "in_progress",
      "authScore": 91,
      "aiSummary": {
        "summary": "Bài luận thể hiện tư duy phản biện...",
        "skillsDemonstrated": ["Academic Writing", "Critical Thinking"],
        "evidenceStrength": "high"
      }
    }
  ],
  "error": null,
  "status": 200
}
```

**Frontend Usage:**
- `MentorHome.tsx` - Pending count display
- `EssayReview.tsx` - Essay list for review

---

### 4. Submit Review

Submits mentor review for an essay/milestone.

```http
POST /mentors/{mentorId}/reviews
Content-Type: application/json

{
  "milestoneId": "ms_001",
  "score": 8.5,
  "feedback": "Bài viết có cấu trúc tốt, lập luận chặt chẽ.",
  "strengths": ["Cấu trúc rõ ràng", "Lập luận chặt chẽ"],
  "improvements": ["Cần mở rộng ví dụ", "Tăng độ đa dạng từ vựng"]
}
```

**Path Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| mentorId | string | Yes | Unique mentor identifier |

**Request Body:**
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| milestoneId | string | Yes | Milestone being reviewed |
| score | number | Yes | Review score (0-10) |
| feedback | string | Yes | General feedback |
| strengths | string[] | Yes | List of strengths |
| improvements | string[] | Yes | List of areas for improvement |

**Response:**
```json
{
  "data": {
    "success": true
  },
  "error": null,
  "status": 201
}
```

**Frontend Usage:**
- `EssayReview.tsx` - Review submission
- `EssayDetailPanel.tsx` - Review form

---

### 5. Add Session Note (Proposed)

```http
POST /mentors/{mentorId}/session-notes
Content-Type: application/json

{
  "studentId": "student_001",
  "date": "2026-03-21",
  "duration": 60,
  "notes": "Tiến bộ tốt ở Reading, cần tập trung Writing.",
  "topics": ["Reading comprehension", "Essay structure"]
}
```

---

## Shared API

Endpoints accessible by all user roles.

### 1. Get Student by ID

Retrieves student information (accessible by student, parent, mentor).

```http
GET /students/{studentId}
```

Same response as [Get Student Profile](#1-get-student-profile).

**Frontend Usage:**
- `EtesterPublic.tsx` - Public profile verification
- All role dashboards

---

### 2. Health Check

API health check endpoint.

```http
GET /health
```

**Response:**
```json
{
  "data": {
    "status": "ok",
    "timestamp": "2026-03-21T16:00:00.000Z"
  },
  "error": null,
  "status": 200
}
```

**Frontend Usage:**
- App initialization
- Connection status monitoring

---

## Data Models

### Core Types

```typescript
// User Roles
type Role = 'student' | 'parent' | 'mentor'

// Severity Levels
type Severity = 'high' | 'medium' | 'low'

// Milestone Types
type ContributionType =
  | 'session_notes'
  | 'essay_review'
  | 'readiness'
  | 'mock_review'
  | 'program_verify'
  | 'outcome_record'
  | 'mock_test'
  | 'essay_draft'
  | 'camp'
  | 'csr'
  | 'other'

// Evidence Strength
type EvidenceStrength = 'low' | 'medium' | 'high' | 'highest'

// Milestone Status
type MilestoneStatus = 'completed' | 'in_progress' | 'upcoming'
```

### Student

```typescript
interface Student {
  id: string
  name: string
  program: 'AMP' | 'IELTS' | 'SAT'
  monthsEnrolled: number
  ieltsScore: number
  satScore: number | null
  gpa: number
  skillBreakdown: {
    L: number  // Listening
    R: number  // Reading
    W: number  // Writing
    S: number  // Speaking
  }
  targetSchools: TargetSchool[]
  parentId: string
  mentorId: string
}
```

### TargetSchool

```typescript
interface TargetSchool {
  name: string
  country: string
  deadline: string         // ISO date string
  ieltsRequired: number
  satRequired: number | null
  daysUntilDeadline: number
  isEligible: boolean
  gapIelts: number
  gapSat: number | null
}
```

### Milestone

```typescript
interface Milestone {
  id: string
  studentId: string
  type: ContributionType
  title: string
  date: string             // ISO date string
  score: number | null
  scoreLabel: string
  mentorId: string | null
  mentorApproved: boolean
  authScore: number | null
  notes: string
  status: MilestoneStatus
  contributorType: 'student' | 'mentor' | 'parent' | 'institution'
  aiSummary: {
    summary: string
    skillsDemonstrated: string[]
    evidenceStrength: EvidenceStrength
  }
}
```

### EtesterCore

```typescript
interface EtesterCore {
  studentId: string
  academicScore: number
  writingGrowth: number
  skills: string[]
  mentorVerifications: number
  parentSupportLevel: 'low' | 'medium' | 'active' | 'high'
  institutionalStamp: boolean
  consistencyScore: number
  totalContributions: number
  lastUpdated: string      // ISO date string
  narrativeCache: string   // AI-generated narrative
  badgeIssued: boolean
}
```

### WellbeingAlert

```typescript
interface WellbeingAlert {
  alert: boolean
  severity: Severity
  message: string
  action: string
}
```

### DigestData

```typescript
interface DigestData {
  progressPct: number
  milestonesCompleted: number
  nextDeadline: string
  daysLeft: number
  priorityAction: string
  weakestSkill: string
}
```

### Mentor

```typescript
interface Mentor {
  id: string
  name: string
  studentIds: string[]
  pendingEssayCount: number
  pendingSessionNoteCount: number
}
```

### ChatMessage

```typescript
interface ChatMessage {
  id: string
  sender: 'parent' | 'ai'
  content: string
  timestamp: string        // ISO date string
}
```

### AuthenticityResult

```typescript
interface AuthenticityResult {
  authScore: number
  confidence: number
  consistentPatterns: string[]
  divergentPatterns: string[]
  recommendation: string
}
```

### UpsellCourse

```typescript
interface UpsellCourse {
  courseName: string
  reason: string
  ctaUrl: string
  tag: 'Trại hè' | 'Khóa học' | 'Workshop'
}
```

---

## Frontend Integration

### Using the API Layer

```typescript
import { studentApi, parentApi, mentorApi, sharedApi } from '../api'

// Fetch student data
const response = await studentApi.getStudent('student_001')
if (response.error) {
  console.error(response.error)
} else {
  console.log(response.data)
}
```

### Using Hooks

```typescript
import { useStudentData } from '../hooks/useStudentData'

function ParentDashboard() {
  const { student, wellbeing, digest, etester, milestones, loading, error } =
    useStudentData('student_001')

  if (loading) return <LoadingSpinner />
  if (error) return <ErrorMessage error={error} />

  return <Dashboard data={student} />
}
```

### Parallel Data Fetching

The `useStudentData` hook fetches multiple endpoints in parallel:

```typescript
const [studentRes, wellbeingRes, digestRes, etesterRes, milestonesRes] =
  await Promise.all([
    studentApi.getStudent(studentId),
    parentApi.getWellbeingAlerts(studentId),
    parentApi.getDigest(studentId),
    studentApi.getEtesterScore(studentId),
    studentApi.getMilestones(studentId),
  ])
```

### Error Handling Pattern

```typescript
try {
  const response = await studentApi.getStudent(studentId)

  if (response.error) {
    // Handle API-level error
    setError(response.error)
    return
  }

  // Use response.data
  setStudent(response.data)
} catch (err) {
  // Handle network/unexpected errors
  setError(err instanceof Error ? err.message : 'Unknown error')
}
```

---

## Appendix

### API Module Structure

```
src/api/
├── types.ts              # ApiResponse, ApiConfig
├── client.ts             # HTTP client (fetch wrapper)
├── index.ts              # Barrel exports
├── student/
│   └── index.ts          # StudentApi class
├── parent/
│   └── index.ts          # ParentApi class
├── mentor/
│   └── index.ts          # MentorApi class
└── shared/
    └── index.ts          # SharedApi class
```

### Mock Data Structure

```
src/data/
├── mock.ts               # Legacy mock exports (MOCK_STUDENT, etc.)
├── mockData.ts           # Array exports for API layer
└── json/
    ├── student.json
    ├── wellbeing.json
    ├── digest.json
    ├── etester.json
    ├── milestones.json
    ├── mentor.json
    └── upsell.json
```

### Mock Implementation Delays

| Endpoint | Delay (ms) |
|----------|------------|
| getStudent | 100 |
| getMilestones | 150 |
| getEtesterScore | 100 |
| getWellbeingAlerts | 150 |
| getDigest | 100 |
| getPendingEssays | 100 |
| submitEssay | 200 |
| submitReview | 200 |
| sendMessage | 200 |

### Future Endpoints (Not Yet Implemented)

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/auth/login` | POST | User authentication |
| `/auth/logout` | POST | Session termination |
| `/auth/refresh` | POST | Token refresh |
| `/parents/{id}/ai-chat` | POST | AI chatbot |
| `/mentors/{id}/session-notes` | POST | Session note creation |
| `/students/{id}/contributions` | POST | Student contribution submission |
| `/upload` | POST | File upload |
| `/students/{id}/behavioral-logs` | GET | Study behavior logs |

---

## Changelog

### v1.0.0 (2026-03-21)
- Initial API documentation
- Role-based API organization (student, parent, mentor, shared)
- Standard response envelope format
- Mock implementation with artificial delays
- Comprehensive data model documentation
