// ChemistFun API Client
const BASE_URL = '/api'

function getAuthHeader() {
  const token = localStorage.getItem('chemistfun_token')
  return token ? { Authorization: `Bearer ${token}` } : {}
}

async function request(endpoint, options = {}) {
  const url = `${BASE_URL}${endpoint}`
  const headers = {
    'Content-Type': 'application/json',
    ...getAuthHeader(),
    ...(options.headers || {}),
  }

  try {
    const res = await fetch(url, { ...options, headers })

    if (res.status === 204) {
      return { ok: true }
    }

    const data = await res.json().catch(() => ({}))

    if (!res.ok) {
      const errorMsg = data.detail || (typeof data === 'string' ? data : 'Terjadi kesalahan sistem')
      throw new Error(Array.isArray(errorMsg) ? errorMsg.map(e => e.msg).join(', ') : errorMsg)
    }

    return data
  } catch (err) {
    console.error(`API Error on [${options.method || 'GET'}] ${url}:`, err.message)
    throw err
  }
}

export const api = {
  // Health
  checkHealth() {
    return request('/health')
  },

  // Auth
  auth: {
    login(email, password) {
      return request('/auth/login', {
        method: 'POST',
        body: JSON.stringify({ email, password }),
      })
    },
    register(payload) {
      return request('/auth/register', {
        method: 'POST',
        body: JSON.stringify(payload),
      })
    },
    getMe() {
      return request('/auth/me')
    },
  },

  // Classes
  classes: {
    enrollByCode(enrollmentCode, studentId = null) {
      return request('/classes/enroll', {
        method: 'POST',
        body: JSON.stringify({ enrollment_code: enrollmentCode, student_id: studentId }),
      })
    },
    list(teacherId = null, myClasses = false) {
      const params = new URLSearchParams()
      if (teacherId) params.append('teacher_id', teacherId)
      if (myClasses) params.append('my_classes', 'true')
      const qs = params.toString() ? `?${params.toString()}` : ''
      return request(`/classes/${qs}`)
    },
    create(data) {
      return request('/classes/', {
        method: 'POST',
        body: JSON.stringify(data),
      })
    },
    getStudents(classUuid) {
      return request(`/classes/${classUuid}/students`)
    },
    unenroll(classUuid, studentId) {
      return request(`/classes/${classUuid}/students/${studentId}`, {
        method: 'DELETE',
      })
    },
    delete(classUuid) {
      return request(`/classes/${classUuid}`, {
        method: 'DELETE',
      })
    }
  },

  // Content (Modules & Materials & Virtual Lab)
  content: {
    listModules(classId) {
      return request(`/content/modules?class_id=${classId}`)
    },
    createModule(data) {
      return request('/content/modules', {
        method: 'POST',
        body: JSON.stringify(data),
      })
    },
    deleteModule(moduleUuid) {
      return request(`/content/modules/${moduleUuid}`, {
        method: 'DELETE',
      })
    },
    listMaterials(moduleId) {
      return request(`/content/materials?module_id=${moduleId}`)
    },
    createMaterial(data) {
      return request('/content/materials', {
        method: 'POST',
        body: JSON.stringify(data),
      })
    },
    updateMaterial(materialUuid, data) {
      return request(`/content/materials/${materialUuid}`, {
        method: 'PATCH',
        body: JSON.stringify(data),
      })
    },
    deleteMaterial(materialUuid) {
      return request(`/content/materials/${materialUuid}`, {
        method: 'DELETE',
      })
    },
    getLab(materialUuid) {
      return request(`/content/materials/${materialUuid}/lab`)
    },
    upsertLab(materialUuid, data) {
      return request(`/content/materials/${materialUuid}/lab`, {
        method: 'PUT',
        body: JSON.stringify(data),
      })
    },
    verifyInquiry(payload) {
      return request('/content/labs/verify-inquiry', {
        method: 'POST',
        body: JSON.stringify(payload),
      })
    },
  },

  // Assessment (Metrics, Quizzes, Questions, Attempts)
  assessment: {
    listMetrics(moduleId) {
      return request(`/assessment/metrics?module_id=${moduleId}`)
    },
    createMetric(data) {
      return request('/assessment/metrics', {
        method: 'POST',
        body: JSON.stringify(data),
      })
    },
    createQuiz(data) {
      return request('/assessment/quizzes', {
        method: 'POST',
        body: JSON.stringify(data),
      })
    },
    listQuestions(quizUuid) {
      return request(`/assessment/quizzes/${quizUuid}/questions`)
    },
    createQuestion(data) {
      return request('/assessment/questions', {
        method: 'POST',
        body: JSON.stringify(data),
      })
    },
    deleteQuestion(questionUuid) {
      return request(`/assessment/questions/${questionUuid}`, {
        method: 'DELETE',
      })
    },
    listAttempts(quizId = null) {
      const qs = quizId ? `?quiz_id=${quizId}` : ''
      return request(`/assessment/attempts${qs}`)
    },
  }
}

