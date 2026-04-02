import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import AiSessionManager from '../../../pages/tools/AiSessionManager'
import api from '../../../utils/api'

vi.mock('../../../utils/api', () => ({
  default: {
    get: vi.fn(),
    interceptors: {
      request: { use: vi.fn() },
      response: { use: vi.fn() },
    },
  },
}))

const mockSessions = [
  {
    id: 'sess-1',
    project_name: 'workbench',
    directory: '/mnt/g/knowledge/project/workbench',
    message_count: 42,
    time_updated: 1712000000000,
  },
  {
    id: 'sess-2',
    project_name: '',
    directory: '/mnt/g/knowledge/project/other',
    message_count: 10,
    time_updated: 1711000000000,
  },
]

const mockMessages = [
  {
    data: JSON.stringify({ role: 'user' }),
    parts: [
      { data: JSON.stringify({ type: 'text', text: 'Hello, help me with code' }) },
    ],
  },
  {
    data: JSON.stringify({ role: 'assistant' }),
    parts: [
      { data: JSON.stringify({ type: 'text', text: 'Sure, here is the solution' }) },
    ],
  },
]

describe('AiSessionManager', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('renders empty state initially', async () => {
    vi.mocked(api.get).mockResolvedValue({ data: [] })
    render(<AiSessionManager />)
    await waitFor(() => {
      expect(screen.getByText('暂无会话')).toBeTruthy()
    })
  })

  it('renders loading state while fetching', async () => {
    vi.mocked(api.get).mockImplementation(
      () => new Promise(() => {})
    )
    render(<AiSessionManager />)
    expect(screen.getByText('加载中...')).toBeTruthy()
  })

  it('renders error state on API failure', async () => {
    vi.mocked(api.get).mockRejectedValue({
      response: { data: { detail: 'Network error' } },
    })
    render(<AiSessionManager />)
    await waitFor(() => {
      expect(screen.getByText('Network error')).toBeTruthy()
    })
  })

  it('displays sessions list when data is available', async () => {
    vi.mocked(api.get).mockResolvedValue({ data: mockSessions })
    render(<AiSessionManager />)
    await waitFor(() => {
      expect(screen.getByText('workbench')).toBeTruthy()
    })
  })

  it('fetches sessions with correct source parameter', async () => {
    vi.mocked(api.get).mockResolvedValue({ data: mockSessions })
    render(<AiSessionManager />)
    await waitFor(() => {
      expect(api.get).toHaveBeenCalledWith(
        '/api/tools/ai_session_manager/sessions',
        { params: { source: 'kilo', limit: 100 } }
      )
    })
  })

  it('switches source and refetches when clicking OpenCode button', async () => {
    vi.mocked(api.get).mockResolvedValue({ data: [] })
    render(<AiSessionManager />)
    await waitFor(() => {
      expect(screen.getByText('暂无会话')).toBeTruthy()
    })

    vi.clearAllMocks()
    vi.mocked(api.get).mockResolvedValue({ data: mockSessions })

    fireEvent.click(screen.getByText('OpenCode'))
    await waitFor(() => {
      expect(api.get).toHaveBeenCalledWith(
        '/api/tools/ai_session_manager/sessions',
        { params: { source: 'opencode', limit: 100 } }
      )
    })
  })

  it('fetches messages when clicking a session', async () => {
    vi.mocked(api.get)
      .mockResolvedValueOnce({ data: mockSessions })
      .mockResolvedValueOnce({ data: mockMessages })

    render(<AiSessionManager />)
    await waitFor(() => {
      expect(screen.getByText('workbench')).toBeTruthy()
    })

    fireEvent.click(screen.getByText('workbench'))
    await waitFor(() => {
      expect(api.get).toHaveBeenCalledWith(
        '/api/tools/ai_session_manager/messages/session/sess-1/with-parts',
        { params: { source: 'kilo' } }
      )
    })
  })

  it('displays messages after selecting a session', async () => {
    vi.mocked(api.get)
      .mockResolvedValueOnce({ data: mockSessions })
      .mockResolvedValueOnce({ data: mockMessages })

    render(<AiSessionManager />)
    await waitFor(() => {
      expect(screen.getByText('workbench')).toBeTruthy()
    })

    fireEvent.click(screen.getByText('workbench'))
    await waitFor(() => {
      expect(screen.getByText('👤 用户')).toBeTruthy()
      expect(screen.getByText('🤖 助手')).toBeTruthy()
      expect(screen.getByText('Hello, help me with code')).toBeTruthy()
    })
  })

  it('shows empty message state when no session is selected', async () => {
    vi.mocked(api.get).mockResolvedValue({ data: mockSessions })
    render(<AiSessionManager />)
    await waitFor(() => {
      expect(screen.getByText('点击左侧会话查看详情')).toBeTruthy()
    })
  })

  it('handles search when query is entered and Enter is pressed', async () => {
    vi.mocked(api.get)
      .mockResolvedValueOnce({ data: mockSessions })
      .mockResolvedValueOnce({ data: [mockSessions[0]] })

    render(<AiSessionManager />)
    await waitFor(() => {
      expect(screen.getByText('workbench')).toBeTruthy()
    })

    const searchInput = screen.getByPlaceholderText('搜索会话...')
    fireEvent.change(searchInput, { target: { value: 'workbench' } })
    fireEvent.keyDown(searchInput, { key: 'Enter' })

    await waitFor(() => {
      expect(api.get).toHaveBeenCalledWith(
        '/api/tools/ai_session_manager/search',
        { params: { q: 'workbench', source: 'kilo' } }
      )
    })
  })

  it('does not search when query is empty', async () => {
    vi.mocked(api.get).mockResolvedValue({ data: mockSessions })
    render(<AiSessionManager />)
    await waitFor(() => {
      expect(screen.getByText('workbench')).toBeTruthy()
    })

    const searchInput = screen.getByPlaceholderText('搜索会话...')
    fireEvent.keyDown(searchInput, { key: 'Enter' })

    const searchCalls = vi.mocked(api.get).mock.calls.filter(
      (call) => call[0] === '/api/tools/ai_session_manager/search'
    )
    expect(searchCalls.length).toBe(0)
  })

  it('uses directory fallback when project_name is empty', async () => {
    vi.mocked(api.get).mockResolvedValue({ data: [mockSessions[1]] })
    render(<AiSessionManager />)
    await waitFor(() => {
      expect(screen.getByText('other')).toBeTruthy()
    })
  })
})
