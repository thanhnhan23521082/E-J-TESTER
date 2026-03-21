# API Module Documentation

## Overview

This directory contains the frontend API layer organized by user roles (student, parent, mentor) and shared utilities. The API layer provides a clean abstraction over data fetching and prepares the codebase for backend integration.

## Architecture

```
src/api/
├── types.ts           # Shared TypeScript types
├── client.ts          # Base HTTP client
├── student/           # Student-specific API calls
├── parent/            # Parent-specific API calls
├── mentor/            # Mentor-specific API calls
├── shared/            # Shared API utilities
└── index.ts           # Barrel exports
```

## Role-Based Organization

### Student API (`student/index.ts`)
- `getStudent(studentId)` - Get student profile
- `getMilestones(studentId)` - Get student milestones
- `getEtesterScore(studentId)` - Get E-Tester score
- `submitEssay(studentId, essay)` - Submit essay for milestone

### Parent API (`parent/index.ts`)
- `getChildren(parentId)` - Get all children
- `getWellbeingAlerts(studentId)` - Get wellbeing alerts
- `getDigest(studentId)` - Get digest data
- `sendMessage(parentId, mentorId, message)` - Send message to mentor

### Mentor API (`mentor/index.ts`)
- `getMentor(mentorId)` - Get mentor profile
- `getStudents(mentorId)` - Get assigned students
- `getPendingEssays(mentorId)` - Get pending essays for review
- `submitReview(mentorId, milestoneId, review)` - Submit essay review

### Shared API (`shared/index.ts`)
- `getStudentById(studentId)` - Get student by ID (all roles)
- `healthCheck()` - API health check

## Usage

### Basic Usage

```typescript
import { studentApi, parentApi, mentorApi } from '@/api'

// Fetch student data
const response = await studentApi.getStudent('student_001')
if (response.error) {
  console.error(response.error)
} else {
  console.log(response.data)
}
```

### With React Hooks

```typescript
import { useState, useEffect } from 'react'
import { studentApi } from '@/api'

function StudentProfile({ studentId }: { studentId: string }) {
  const [student, setStudent] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    const fetchStudent = async () => {
      setLoading(true)
      const response = await studentApi.getStudent(studentId)

      if (response.error) {
        setError(response.error)
      } else {
        setStudent(response.data)
      }

      setLoading(false)
    }

    fetchStudent()
  }, [studentId])

  if (loading) return <div>Loading...</div>
  if (error) return <div>Error: {error}</div>
  if (!student) return <div>No data</div>

  return <div>{student.name}</div>
}
```

## API Response Format

All API methods return a standardized `ApiResponse<T>` type:

```typescript
interface ApiResponse<T> {
  data: T | null      // Response data (null on error)
  error: string | null // Error message (null on success)
  status: number       // HTTP status code
}
```

## Error Handling

```typescript
const response = await studentApi.getStudent('student_001')

if (response.error) {
  // Handle error
  switch (response.status) {
    case 404:
      console.error('Student not found')
      break
    case 500:
      console.error('Server error')
      break
    default:
      console.error(response.error)
  }
} else {
  // Handle success
  console.log(response.data)
}
```

## Mock Implementation

Currently, all API methods use mock data with artificial delays (100-200ms) to simulate network latency. This allows frontend development to proceed independently of backend implementation.

### Mock Data Sources
- `mockStudents` - Student profiles
- `mockMilestones` - Student milestones
- `mockEtesterScores` - E-Tester scores
- `mockWellbeingAlerts` - Wellbeing alerts
- `mockDigestData` - Digest data
- `mockMentors` - Mentor profiles

## Migration to Backend

When the backend is ready, replace mock implementations with actual API calls:

1. **Update API client configuration** (`client.ts`):
   ```typescript
   private config: ApiConfig = {
     baseUrl: process.env.VITE_API_URL || 'http://localhost:3000/api',
     timeout: 10000,
     headers: {
       'Content-Type': 'application/json',
       'Authorization': `Bearer ${getAuthToken()}`, // Add auth
     },
   }
   ```

2. **Replace mock implementations** in each API module:
   ```typescript
   // Before (mock)
   async getStudent(studentId: string): Promise<ApiResponse<Student>> {
     await new Promise((resolve) => setTimeout(resolve, 100))
     const student = mockStudents.find((s) => s.id === studentId)
     return { data: student, error: null, status: 200 }
   }

   // After (real API)
   async getStudent(studentId: string): Promise<ApiResponse<Student>> {
     return apiClient.get<Student>(`/students/${studentId}`)
   }
   ```

3. **Remove mock data imports** from API modules

4. **Add authentication** to API client if needed

## Testing

```typescript
import { studentApi } from '@/api'

describe('StudentApi', () => {
  it('should fetch student by ID', async () => {
    const response = await studentApi.getStudent('student_001')

    expect(response.error).toBeNull()
    expect(response.status).toBe(200)
    expect(response.data).toBeDefined()
    expect(response.data?.id).toBe('student_001')
  })

  it('should handle student not found', async () => {
    const response = await studentApi.getStudent('invalid_id')

    expect(response.data).toBeNull()
    expect(response.error).toBe('Student not found')
    expect(response.status).toBe(404)
  })
})
```

## Best Practices

1. **Always check for errors** before using response data
2. **Use loading states** in UI components
3. **Handle all error cases** (404, 500, network errors)
4. **Use TypeScript types** for type safety
5. **Keep API methods focused** - one responsibility per method
6. **Add TODO comments** for backend migration points
7. **Use optional chaining** when accessing nested data
8. **Implement proper timeout handling** for long requests

## Configuration

The API client can be configured globally:

```typescript
import { apiClient } from '@/api'

apiClient.setConfig({
  baseUrl: 'https://api.example.com',
  timeout: 15000,
  headers: {
    'Content-Type': 'application/json',
    'Authorization': 'Bearer token',
  },
})
```
