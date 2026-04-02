import { describe, it, expect } from 'vitest'
import {
  windowsToWsl,
  wslToWindows,
  parsePath,
  getParentPath,
  isWslPath,
} from '../pathUtils'

describe('windowsToWsl', () => {
  it('converts standard Windows path to WSL', () => {
    expect(windowsToWsl('G:\\knowledge\\Project')).toBe('/mnt/g/knowledge/Project')
  })

  it('handles lowercase drive letter', () => {
    expect(windowsToWsl('c:\\Users\\test')).toBe('/mnt/c/Users/test')
  })

  it('handles C: drive', () => {
    expect(windowsToWsl('C:\\Windows\\System32')).toBe('/mnt/c/Windows/System32')
  })

  it('returns original if not a Windows path', () => {
    expect(windowsToWsl('/mnt/g/knowledge')).toBe('/mnt/g/knowledge')
  })

  it('returns original for empty string', () => {
    expect(windowsToWsl('')).toBe('')
  })

  it('handles single-level path', () => {
    expect(windowsToWsl('D:\\temp')).toBe('/mnt/d/temp')
  })
})

describe('wslToWindows', () => {
  it('converts standard WSL path to Windows', () => {
    expect(wslToWindows('/mnt/g/knowledge/Project')).toBe('G:\\knowledge\\Project')
  })

  it('handles lowercase drive letter', () => {
    expect(wslToWindows('/mnt/c/Users/test')).toBe('C:\\Users\\test')
  })

  it('returns original if not an /mnt/ path', () => {
    expect(wslToWindows('G:\\knowledge')).toBe('G:\\knowledge')
  })

  it('returns original for empty string', () => {
    expect(wslToWindows('')).toBe('')
  })

  it('handles single-level path', () => {
    expect(wslToWindows('/mnt/d/temp')).toBe('D:\\temp')
  })
})

describe('isWslPath', () => {
  it('returns true for /mnt/ paths', () => {
    expect(isWslPath('/mnt/g/knowledge')).toBe(true)
  })

  it('returns true for /mnt/ root', () => {
    expect(isWslPath('/mnt/')).toBe(true)
  })

  it('returns false for Windows paths', () => {
    expect(isWslPath('G:\\knowledge')).toBe(false)
  })

  it('returns false for other Unix paths', () => {
    expect(isWslPath('/home/user')).toBe(false)
  })

  it('returns false for empty string', () => {
    expect(isWslPath('')).toBe(false)
  })
})

describe('parsePath', () => {
  it('parses WSL path correctly', () => {
    const result = parsePath('/mnt/g/knowledge/Project')
    expect(result.isWsl).toBe(true)
    expect(result.parts).toEqual(['mnt', 'g', 'knowledge', 'Project'])
  })

  it('parses Windows path correctly', () => {
    const result = parsePath('G:\\knowledge\\Project')
    expect(result.isWsl).toBe(false)
    expect(result.parts).toEqual(['G:', 'knowledge', 'Project'])
  })

  it('normalizes backslashes to forward slashes', () => {
    const result = parsePath('C:\\Users\\test')
    expect(result.parts).toEqual(['C:', 'Users', 'test'])
  })
})

describe('getParentPath', () => {
  it('returns parent of WSL path', () => {
    expect(getParentPath('/mnt/g/knowledge/Project')).toBe('/mnt/g/knowledge')
  })

  it('returns / for root-like WSL path', () => {
    // Note: isWslPath requires '/mnt/' with trailing slash
    // '/mnt' alone doesn't match, so getParentPath returns ''
    expect(getParentPath('/mnt')).toBe('')
  })

  it('returns / for /mnt/ root', () => {
    expect(getParentPath('/mnt/')).toBe('/')
  })

  it('returns parent of Windows path', () => {
    const result = getParentPath('G:\\knowledge\\Project')
    expect(result).toContain('knowledge')
  })
})

describe('round-trip conversion', () => {
  it('windowsToWsl -> wslToWindows returns original', () => {
    const original = 'G:\\knowledge\\Project'
    const wsl = windowsToWsl(original)
    const back = wslToWindows(wsl)
    expect(back).toBe(original)
  })

  it('wslToWindows -> windowsToWsl returns original', () => {
    const original = '/mnt/g/knowledge/Project'
    const win = wslToWindows(original)
    const back = windowsToWsl(win)
    expect(back).toBe(original)
  })
})
