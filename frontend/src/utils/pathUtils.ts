export function windowsToWsl(path: string): string {
  const match = path.match(/^([A-Za-z]):\\(.+)$/);
  if (!match) return path;
  const drive = match[1].toLowerCase();
  const rest = match[2].replace(/\\/g, '/');
  return `/mnt/${drive}/${rest}`;
}

export function wslToWindows(path: string): string {
  const match = path.match(/^\/mnt\/([a-z])\/(.+)$/);
  if (!match) return path;
  const drive = match[1].toUpperCase();
  const rest = match[2].replace(/\//g, '\\');
  return `${drive}:\\${rest}`;
}

export function parsePath(path: string): { parts: string[]; isWsl: boolean } {
  const normalized = path.replace(/\\/g, '/');
  const isWsl = normalized.startsWith('/mnt/');
  const parts = normalized.split('/').filter(Boolean);
  return { parts, isWsl };
}

export function getParentPath(path: string): string {
  const normalized = path.replace(/\\/g, '/');
  const parts = normalized.split('/').filter(Boolean);
  if (parts.length <= 1) {
    return isWslPath(path) ? '/' : '';
  }
  parts.pop();
  const prefix = isWslPath(path) ? '/' : '';
  return prefix + parts.join('/');
}

export function isWslPath(path: string): boolean {
  return path.startsWith('/mnt/');
}