const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1'

async function fetchAPI(endpoint, options = {}) {
  const url = `${API_BASE}${endpoint}`
  const config = {
    headers: {
      'Content-Type': 'application/json',
      ...options.headers,
    },
    ...options,
  }

  try {
    const response = await fetch(url, config)
    if (!response.ok) {
      throw new Error(`API Error: ${response.status}`)
    }
    return await response.json()
  } catch (error) {
    console.error(`API request failed: ${endpoint}`, error)
    throw error
  }
}

// Listings
export const getListings = (params = {}) => {
  const query = new URLSearchParams(params).toString()
  return fetchAPI(`/listings${query ? `?${query}` : ''}`)
}
export const getListing = (id) => fetchAPI(`/listings/${id}`)

// Companies
export const getCompanies = () => fetchAPI('/companies')
export const getCompany = (id) => fetchAPI(`/companies/${id}`)

// CV Analysis
export const analyzeCv = (jobDescription, cvText) =>
  fetchAPI('/cv/analyze', {
    method: 'POST',
    body: JSON.stringify({ job_description: jobDescription, cv_text: cvText }),
  })

// Interview
export const getInterviewQuestion = (category, questionIndex) =>
  fetchAPI('/interview/ask', {
    method: 'POST',
    body: JSON.stringify({ category, question_index: questionIndex }),
  })

export const evaluateAnswer = (question, answer) =>
  fetchAPI('/interview/evaluate', {
    method: 'POST',
    body: JSON.stringify({ question, answer }),
  })

// CrewAI Company Research
export const startCrewResearch = (companyName) =>
  fetchAPI('/crew/research', {
    method: 'POST',
    body: JSON.stringify({ company_name: companyName }),
  })
