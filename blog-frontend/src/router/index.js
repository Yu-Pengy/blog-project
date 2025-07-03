import { createRouter, createWebHistory } from 'vue-router'
import Home from '../views/Home.vue'
import Login from '../views/Login.vue'
import Register from '../views/Register.vue'
import MyPosts from '../views/MyPosts.vue'
import PostDetail from '../views/PostDetail.vue'
import WritePost from '../views/WritePost.vue'
import EditPost from '../views/EditPost.vue'
import Admin from '../views/Admin.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: Home
    },
    {
      path: '/login',
      name: 'login',
      component: Login
    },
    {
      path: '/register',
      name: 'register',
      component: Register
    },
    {
      path: '/my-posts',
      name: 'my-posts',
      component: MyPosts,
      meta: { requiresAuth: true }
    },
    {
      path: '/post/:id',
      name: 'post-detail',
      component: PostDetail,
      meta: { requiresAuth: true }
    },
    {
      path: '/write',
      name: 'write-post',
      component: WritePost,
      meta: { requiresAuth: true }
    },
    {
      path: '/edit/:id',
      name: 'edit-post',
      component: EditPost,
      meta: { requiresAuth: true }
    },
    {
      path: '/admin',
      name: 'admin',
      component: Admin,
      meta: { requiresAuth: true, requiresAdmin: true }
    }
  ]
})

// 路由守卫
router.beforeEach(async (to, from, next) => {
  // 这里可以添加认证检查逻辑
  next()
})

export default router