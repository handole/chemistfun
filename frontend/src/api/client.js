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
    listModules(classIdOrParams = null) {
      if (!classIdOrParams) return request('/content/modules')
      if (typeof classIdOrParams === 'object') {
        const params = new URLSearchParams()
        if (classIdOrParams.grade_level) params.append('grade_level', classIdOrParams.grade_level)
        if (classIdOrParams.class_id) params.append('class_id', classIdOrParams.class_id)
        return request(`/content/modules?${params.toString()}`)
      }
      return request(`/content/modules?class_id=${classIdOrParams}`)
    },
    listModulesByGrade(gradeLevel) {
      return request(`/content/modules?grade_level=${gradeLevel}`)
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
    getLabByUuid(labUuid) {
      return request(`/content/labs/${labUuid}`)
    },
    listLabs(status = null) {
      const params = new URLSearchParams()
      if (status) params.append('status', status)
      const q = params.toString()
      return request(`/content/labs${q ? `?${q}` : ''}`)
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
    generateLabWithAI(prompt, materialUuid = null) {
      return request('/content/labs/generate-ai', {
        method: 'POST',
        body: JSON.stringify({
          teacher_prompt: prompt,
          material_uuid: materialUuid,
        }),
      })
    },
    generateMaterialWithAI(topic, moduleId = null) {
      return request('/content/materials/generate-ai', {
        method: 'POST',
        body: JSON.stringify({
          topic,
          module_id: moduleId,
        }),
      })
    },
    chatChemBot(question) {
      return request('/content/chembot/chat', {
        method: 'POST',
        body: JSON.stringify({ question }),
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
    getQuizByModule(moduleId) {
      return request(`/assessment/quizzes/by-module/${moduleId}`)
    },
    getQuiz(quizUuid) {
      return request(`/assessment/quizzes/${quizUuid}`)
    },
    listQuestionsStudent(quizUuid) {
      return request(`/assessment/quizzes/${quizUuid}/questions/student-view`)
    },
    startAttempt(quizId, studentId = null) {
      return request('/assessment/attempts/start', {
        method: 'POST',
        body: JSON.stringify({ quiz_id: quizId, student_id: studentId }),
      })
    },
    saveAnswer(attemptId, questionId, selectedAnswer) {
      return request('/assessment/answers', {
        method: 'POST',
        body: JSON.stringify({
          attempt_id: attemptId,
          question_id: questionId,
          selected_answer: selectedAnswer,
        }),
      })
    },
    submitAttempt(attemptUuid) {
      return request(`/assessment/attempts/${attemptUuid}/submit`, {
        method: 'POST',
      })
    },
    getAttempt(attemptUuid) {
      return request(`/assessment/attempts/${attemptUuid}`)
    },
  }
}

