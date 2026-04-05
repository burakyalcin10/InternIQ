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

// CV Analysis (supports PDF upload via FormData)
export const analyzeCv = async (jobDescription, cvFile = null, cvText = '') => {
  const url = `${API_BASE}/cv/analyze`
  const formData = new FormData()
  formData.append('job_description', jobDescription)
  if (cvFile) {
    formData.append('cv_file', cvFile)
  }
  if (cvText) {
    formData.append('cv_text', cvText)
  }

  try {
    const response = await fetch(url, {
      method: 'POST',
      body: formData,
      // No Content-Type header — browser sets multipart boundary automatically
    })
    if (!response.ok) throw new Error(`API Error: ${response.status}`)
    return await response.json()
  } catch (error) {
    console.error('CV analysis failed:', error)
    throw error
  }
}

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
