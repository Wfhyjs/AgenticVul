import { createRouter, createWebHistory } from 'vue-router';
import Login from '../components/login/Login.vue'; // 更新引用为 Login.vue
// import Home from "@/components/Home.vue";
import Register from "@/components/login/Register.vue";
import ForgetPassword from "@/components/login/ForgetPassword.vue";
import Home from "@/components/Home.vue";
import OverView from "@/components/overview/OverView.vue";
import Account from "@/components/account/Account.vue";
import Chat from "@/components/chat/Chat.vue";
import codeDetection from "@/components/codedetection/codeDetection.vue";
import Upload from "@/components/upload/Upload.vue";
import Project from "@/components/project/Project.vue";
import ProjectDetail from "@/components/project/ProjectDetail.vue";
import ProjectOverview from "@/components/project/ProjectOverview.vue";

const routes = [
    { path: '/', redirect: '/home/index' },
    {
        path: '/home', component: Home, meta: {requiresAuth: true},
        children: [
            {
                path: 'index',
                component: OverView,
                meta: { sidebar: 'default' },
            },
            {
                path: 'account',
                component: Account,
                meta: { sidebar: 'default' },
            },
            {
                path: 'chat',
                component: Chat,
                meta: { sidebar: 'default' },
            },
            {
                path: 'codedetection',
                component: codeDetection,
                meta: { sidebar: 'default' },
            },
            {
                path: 'upload',
                component: Upload,
                meta: { sidebar: 'default' },
            },
            {
                path: 'project',
                component: Project,
                meta: { sidebar: 'default' },
            },
            {
                path: 'project/:id/:pname/:file_path', // 添加 ProjectDetail 的动态路由
                name: 'ProjectDetail',
                component: ProjectDetail,
                meta: { sidebar: 'project' },
            },
            {
                path: 'project/:pname',
                name: 'ProjectOverview',
                component: ProjectOverview,
                meta: { sidebar: 'project' },
            },



        ],
    },
    // { path: '/', redirect: '/login' },
    {path: '/login', component: Login},
    {path: '/register', component: Register},
    {path: '/forget', component: ForgetPassword},
    {path: '/profile', component: Account },
    {path: '/:pathMatch(.*)*', redirect: '/home'},

];



const router = createRouter({
    history: createWebHistory(),
    routes,
});

export default router;
