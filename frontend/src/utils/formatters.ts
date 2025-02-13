// src/utils/formatters.ts
export const formatDate = (date: string | Date) => {
  return new Date(date).toLocaleString();
};

export const formatNumber = (num: number) => {
  return new Intl.NumberFormat().format(num);
};

export const formatSeverity = (severity: string) => {
  return severity.charAt(0).toUpperCase() + severity.slice(1).toLowerCase();
};

export const formatBytes = (bytes: number) => {
  const units = ['B', 'KB', 'MB', 'GB', 'TB'];
  let size = bytes;
  let unitIndex = 0;
  
  while (size >= 1024 && unitIndex < units.length - 1) {
    size /= 1024;
    unitIndex++;
  }
  
  return `${size.toFixed(1)} ${units[unitIndex]}`;
};