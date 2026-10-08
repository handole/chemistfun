/* Frontend QA Tests for KimiFun Vue.js App */

import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import App from '@/App.vue'
import TeacherDashboard from '@/views/teacher/TeacherDashboard.vue'
import StudentDashboard from '@/views/student/StudentDashboard.vue'
import ContentManagementView from '@/views/teacher/ContentManagementView.vue'
import VirtualLabConfigView from '@/views/teacher/VirtualLabConfigView.vue'

describe('KimiFun Application Smoke Tests', () => {
  it('App component mounts without error', () => {
    const wrapper = mount(App)
    expect(wrapper.exists()).toBe(true)
    expect(wrapper.vm).toBeDefined()
  })

  it('TeacherDashboard renders without crashing', () => {
    const wrapper = mount(TeacherDashboard, {
      props: { user: { role: 'teacher', full_name: 'Guru Test' } }
    })
    expect(wrapper.exists()).toBe(true)
  })

  it('StudentDashboard renders without crashing', () => {
    const wrapper = mount(StudentDashboard, {
      props: { user: { role: 'student', full_name: 'Siswa Test' } }
    })
    expect(wrapper.exists()).toBe(true)
  })

  it('ContentManagementView renders modules without crashing', () => {
    const wrapper = mount(ContentManagementView, {
      props: { user: { role: 'teacher' } }
    })
    expect(wrapper.exists()).toBe(true)
  })

  it('VirtualLabConfigView renders lab config without crashing', () => {
    const wrapper = mount(VirtualLabConfigView, {
      props: { initialMaterial: null, user: { role: 'teacher' } }
    })
    expect(wrapper.exists()).toBe(true)
  })
})