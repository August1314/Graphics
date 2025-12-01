/**
 * 导航管理器
 */

export class NavigationManager {
    constructor() {
        this.activeSection = 'home';
        this.init();
    }

    init() {
        this.bindEvents();
        this.updateActiveStates();
    }

    bindEvents() {
        // 顶部导航
        const navItems = document.querySelectorAll('.nav-item');
        navItems.forEach(item => {
            item.addEventListener('click', (e) => {
                e.preventDefault();
                const href = item.getAttribute('href');
                if (href && href.startsWith('#')) {
                    this.scrollToSection(href.substring(1));
                }
            });
        });

        // 移动端导航
        const mobileNavItems = document.querySelectorAll('.mobile-nav-item');
        mobileNavItems.forEach(item => {
            item.addEventListener('click', (e) => {
                e.preventDefault();
                const href = item.getAttribute('href');
                if (href && href.startsWith('#')) {
                    this.scrollToSection(href.substring(1));
                }
            });
        });

        // Logo 点击
        const logo = document.querySelector('.nav-logo');
        if (logo) {
            logo.addEventListener('click', () => {
                this.scrollToSection('home');
            });
        }
    }

    scrollToSection(sectionId) {
        const section = document.getElementById(sectionId);
        if (section) {
            const navHeight = 60;
            const top = section.offsetTop - navHeight;
            window.scrollTo({
                top: top,
                behavior: 'smooth'
            });
            this.setActiveSection(sectionId);
        }
    }

    setActiveSection(sectionId) {
        this.activeSection = sectionId;
        this.updateActiveStates();
    }

    updateActiveStates() {
        // 更新顶部导航
        const navItems = document.querySelectorAll('.nav-item');
        navItems.forEach(item => {
            const href = item.getAttribute('href');
            if (href === `#${this.activeSection}`) {
                item.classList.add('active');
            } else {
                item.classList.remove('active');
            }
        });

        // 更新移动端导航
        const mobileNavItems = document.querySelectorAll('.mobile-nav-item');
        mobileNavItems.forEach(item => {
            const href = item.getAttribute('href');
            if (href === `#${this.activeSection}`) {
                item.classList.add('active');
            } else {
                item.classList.remove('active');
            }
        });
    }
}

export default NavigationManager;
