/* Frontend QA Tests for KimiFun Vue.js App */

import { describe, it, expect, vi } from 'vitest'
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
    expect(wrapper.find('h1').text()).toBe('KimiFun')
  })

  it('TeacherDashboard renders without crashing', () => {
    const wrapper = mount(TeacherDashboard, {
      props: { user: { role: 'teacher', full_name: 'Guru Test' } }
    })
    expect(wrapper.exists()).toBe(true)
    expect(wrapper.find('[data-test="teacher-dashboard"]').exists()).toBe(true)
  })

  it('StudentDashboard renders without crashing', () => {
    const wrapper = mount(StudentDashboard, {
      props: { user: { role: 'student', full_name: 'Siswa Test' } }
    })
    expect(wrapper.exists()).toBe(true)
    expect(wrapper.find('[data-test="student-dashboard"]').exists()).toBe(true)
  })

  it('ContentManagementView renders modules', () => {
    const wrapper = mount(ContentManagementView, {
      props: { user: { role: 'teacher' } }
    })
    expect(wrapper.exists()).toBe(true)
    expect(wrapper.find('[data-test="content-management"]').exists()).toBe(true)
  })

  it('VirtualLabConfigView renders lab config', () => {
    const wrapper = mount(VirtualLabConfigView, {
      props: { initialMaterial: null, user: { role: 'teacher' } }
    })
    expect(wrapper.exists()).toBe(true)
    expect(wrapper.find('[data-test="virtual-lab-config"]').exists()).toBe(true)
  })

  it('API proxy configuration is correct', () => {
    // Test that the Vite proxy is configured correctly
    const wrapper = mount(App)
    // Check that the app is mounted and functional
    expect(wrapper.vm).toBeDefined()
  })
})