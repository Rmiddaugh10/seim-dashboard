// src/utils/constants.ts
export const SEVERITY_LEVELS = {
    CRITICAL: 'critical',
    HIGH: 'high',
    MEDIUM: 'medium',
    LOW: 'low'
  } as const;
  
  export const EVENT_TYPES = {
    ALERT: 'alert',
    LOG: 'log',
    METRIC: 'metric'
  } as const;
  
  export const TIME_RANGES = {
    HOUR: '1h',
    DAY: '24h',
    WEEK: '7d',
    MONTH: '30d'
  } as const;