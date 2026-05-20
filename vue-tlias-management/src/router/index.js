import { createRouter, createWebHashHistory } from 'vue-router';
import Index from '@/views/index/index.vue';
import Clazz from '@/views/clazz/index.vue';
import Stu from '@/views/stu/index.vue';
import Dept from '@/views/dept/index.vue';
import Emp from '@/views/emp/index.vue';
import StuReport from '@/views/report/stu/index.vue';
import Login from '@/views/login/index.vue';
import Layout from '@/views/layout/index.vue';

const routes = [
  {
    path: '/',
    component: Layout,
    redirect: '/index',
    children: [
      { path: '/index', component: Index },
      { path: '/clazz', component: Clazz },
      { path: '/stu', component: Stu },
      { path: '/dept', component: Dept },
      { path: '/emp', component: Emp },
      { path: '/report/stu', component: StuReport }
    ]
  },
  { path: '/login', component: Login }
];

const router = createRouter({
  history: createWebHashHistory(),
  routes,
});

router.beforeEach((to, from, next) => {
  const loginUser = localStorage.getItem('loginUser');
  if (to.path === '/login') {
    next();
  } else if (!loginUser) {
    next('/login');
  } else {
    next();
  }
});

export default router;