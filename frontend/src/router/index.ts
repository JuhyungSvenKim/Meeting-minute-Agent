import { createRouter, createWebHistory, type RouteRecordRaw } from 'vue-router'

const routes: RouteRecordRaw[] = [
  {
    path: '/',
    name: 'meetings',
    component: () => import('@/views/MeetingListView.vue'),
  },
  {
    path: '/meetings/new',
    name: 'meeting-new',
    component: () => import('@/views/MeetingCreateView.vue'),
  },
  {
    path: '/meetings/:id',
    name: 'meeting-detail',
    component: () => import('@/views/MeetingDetailView.vue'),
    props: true,
  },
  {
    path: '/about',
    name: 'about',
    component: () => import('@/views/AboutView.vue'),
  },
  { path: '/:pathMatch(.*)*', redirect: '/' },
]

export const router = createRouter({
  history: createWebHistory(),
  routes,
})
