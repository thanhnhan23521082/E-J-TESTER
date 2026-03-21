import { format, formatDistanceToNow, parseISO, isValid } from 'date-fns'
import { vi } from 'date-fns/locale'

export function formatDate(dateString: string, formatStr: string = 'dd/MM/yyyy'): string {
  try {
    const date = parseISO(dateString)
    if (!isValid(date)) return dateString
    return format(date, formatStr, { locale: vi })
  } catch {
    return dateString
  }
}

export function formatDateRelative(dateString: string): string {
  try {
    const date = parseISO(dateString)
    if (!isValid(date)) return dateString
    return formatDistanceToNow(date, { addSuffix: true, locale: vi })
  } catch {
    return dateString
  }
}

export function formatDateTime(dateString: string): string {
  return formatDate(dateString, 'HH:mm dd/MM/yyyy')
}

export function getDaysUntilDeadline(deadlineDate: string): number {
  try {
    const deadline = parseISO(deadlineDate)
    const now = new Date()
    const diffTime = deadline.getTime() - now.getTime()
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24))
    return diffDays
  } catch {
    return 0
  }
}
