import { supabase } from '../lib/supabase'

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1'

async function getAuthHeaders(options = {}) {
  if (options.skipAuth) {
    return {
      ...(options.body instanceof FormData ? {} : { 'Content-Type': 'application/json' }),
      ...options.headers,
    }
  }

  const { data } = await supabase.auth.getSession()
  const token = data.session?.access_token
  const isFormData = options.body instanceof FormData

  return {
    ...(isFormData ? {} : { 'Content-Type': 'application/json' }),
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
    ...options.headers,
  }
}

async function fetchAPI(endpoint, options = {}) {
  const url = `${API_BASE}${endpoint}`
  const { skipAuth, ...fetchOptions } = options
  const response = await fetch(url, {
    ...fetchOptions,
    headers: await getAuthHeaders(options),
  })

  const contentType = response.headers.get('content-type') || ''
  const payload = contentType.includes('application/json')
    ? await response.json()
    : await response.text()

  if (!response.ok) {
    const message =
      payload?.detail ||
      payload?.message ||
      `API Error: ${response.status}`
    throw new Error(message)
  }

  return payload
}

export const getCurrentUser = () => fetchAPI('/auth/me')
export const getProfile = () => fetchAPI('/profile/me')

export const uploadProfileCv = async (cvFile = null, cvText = '') => {
  const formData = new FormData()
  if (cvFile) {
    formData.append('cv_file', cvFile)
  }
  if (cvText.trim()) {
    formData.append('cv_text', cvText)
  }

  return fetchAPI('/profile/cv', {
    method: 'POST',
    body: formData,
  })
}

// Listings
export const getListings = (params = {}) => {
  const query = new URLSearchParams(params).toString()
  return fetchAPI(`/listings${query ? `?${query}` : ''}`, { skipAuth: true })
}
export const getListing = (id) => fetchAPI(`/listings/${id}`, { skipAuth: true })

// Companies
export const getCompanies = () => fetchAPI('/companies', { skipAuth: true })
export const getCompany = (id) => fetchAPI(`/companies/${id}`, { skipAuth: true })

// CV Analysis
export const analyzeCv = async (jobDescription, cvFile = null, cvText = '') => {
  const formData = new FormData()
  formData.append('job_description', jobDescription)
  if (cvFile) {
    formData.append('cv_file', cvFile)
  }
  if (cvText.trim()) {
    formData.append('cv_text', cvText)
  }

  return fetchAPI('/cv/analyze', {
    method: 'POST',
    body: formData,
  })
}

// Interview — Basic Mode
export const getInterviewQuestion = (category, questionIndex) =>
  fetchAPI('/interview/ask', {
    method: 'POST',
    skipAuth: true,
    body: JSON.stringify({ category, question_index: questionIndex }),
  })

export const evaluateAnswer = (question, answer) =>
  fetchAPI('/interview/evaluate', {
    method: 'POST',
    skipAuth: true,
    body: JSON.stringify({ question, answer }),
  })

// Interview — LangGraph Mode
export const lgStartInterview = (
  company = 'Genel',
  position = 'Yazılım Mühendisi Stajyeri',
  category = 'technical',
  maxQuestions = 5,
  candidateProfile = {},
) =>
  fetchAPI('/interview/lg/start', {
    method: 'POST',
    skipAuth: true,
    body: JSON.stringify({
      company,
      position,
      category,
      max_questions: maxQuestions,
      candidate_profile: candidateProfile,
    }),
  })

export const lgAnswerQuestion = (sessionId, answer) =>
  fetchAPI('/interview/lg/answer', {
    method: 'POST',
    skipAuth: true,
    body: JSON.stringify({
      session_id: sessionId,
      answer,
    }),
  })

// CrewAI Company Research
export const startCrewResearch = (companyName) =>
  fetchAPI('/crew/research', {
    method: 'POST',
    body: JSON.stringify({ company_name: companyName }),
  })

// LangGraph Application Workflow
export const startWorkflow = (listingId, cvText = '') =>
  fetchAPI('/workflow/prepare', {
    method: 'POST',
    body: JSON.stringify({
      listing_id: listingId,
      cv_text: cvText,
    }),
  })

// MCP Demo
export const runMcpDemo = (listingId, cvText = '') =>
  fetchAPI('/mcp/demo', {
    method: 'POST',
    skipAuth: true,
    body: JSON.stringify({
      listing_id: listingId,
      cv_text: cvText,
    }),
  })
