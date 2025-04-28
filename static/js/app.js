/**
 * Banking System Main Application
 * Integrates all components and handles application flow
 */

document.addEventListener('DOMContentLoaded', () => {
    // App state
    const state = {
        currentPage: null,
        user: null,
        accounts: [],
        transactions: [],
        loans: []
    };

    // Initialize the application
    init();

    /**
     * Initialize the application
     */
    function init() {
        // Initialize event listeners
        initializeEventListeners();

        // Check authentication status
        checkAuth();
    }

    /**
     * Initialize all event listeners
     */
    function initializeEventListeners() {
        // Navigation links
        document.querySelectorAll('.nav-link').forEach(link => {
            link.addEventListener('click', (e) => {
                e.preventDefault();
                const page = e.target.closest('.nav-link').getAttribute('data-page');
                navigateTo(page);
            });
        });

        // Auth form links
        document.getElementById('show-register').addEventListener('click', (e) => {
            e.preventDefault();
            showAuthPage('register');
        });

        document.getElementById('show-login').addEventListener('click', (e) => {
            e.preventDefault();
            showAuthPage('login');
        });

        // Logout button
        document.getElementById('logout-btn').addEventListener('click', (e) => {
            e.preventDefault();
            logout();
        });

        // Auth forms
        document.getElementById('login-form').addEventListener('submit', handleLogin);
        document.getElementById('register-form').addEventListener('submit', handleRegister);

        // Close modals when clicking outside
        window.addEventListener('click', (e) => {
            document.querySelectorAll('.modal').forEach(modal => {
                if (e.target === modal) {
                    modal.style.display = 'none';
                }
            });
        });
    }

    /**
     * Check authentication status
     */
    async function checkAuth() {
        if (api.isAuthenticated()) {
            try {
                // Get current user profile
                const userData = await api.getProfile();
                state.user = userData;

                // Show authenticated UI
                showAuthenticatedUI();

                // Load initial data
                loadDashboard();

                // Initialize admin dashboard if user is admin
                if (state.user.role === 'admin') {
                    await adminComponent.initAdminDashboard(state.user);
                }
            } catch (error) {
                // Token may be invalid or expired
                logout();
            }
        } else {
            // Show login page
            showAuthPage('login');
        }
    }

    /**
     * Show authenticated UI
     */
    function showAuthenticatedUI() {
        document.getElementById('auth-pages').style.display = 'none';
        document.getElementById('main-pages').style.display = 'block';
        document.getElementById('nav-authenticated').style.display = 'block';

        // Set user name in UI
        document.getElementById('user-fullname').textContent = state.user.full_name;

        // Navigate to dashboard by default
        navigateTo('dashboard');
    }

    /**
     * Show specific auth page
     * @param {string} page - Auth page name ('login' or 'register')
     */
    function showAuthPage(page) {
        // Hide all pages
        document.querySelectorAll('#auth-pages .page').forEach(p => {
            p.classList.remove('active');
        });

        // Show specified page
        document.getElementById(`${page}-page`).classList.add('active');

        // Clear error messages
        document.getElementById('login-error').style.display = 'none';
        document.getElementById('register-error').style.display = 'none';
    }

    /**
     * Navigate to specific page
     * @param {string} page - Page name
     */
    function navigateTo(page) {
        // skip if already on this page
        if (state.currentPage === page) return;

        // handle admin page SEPARATELY
        if (page === 'admin') {
            if (state.user && state.user.role === 'admin') {
                state.currentPage = page;
                adminComponent.showAdminDashboard();
            } else {
                // if not admin ==>> redirect to dashboard
                navigateTo('dashboard');
                return;
            }
        } else {
            state.currentPage = page;

            // hide all pages
            document.querySelectorAll('#main-pages .page').forEach(p => {
                p.classList.remove('active');
            });

            // show specified page
            document.getElementById(`${page}-page`).classList.add('active');
        }

        // remove active class from nav links
        document.querySelectorAll('.nav-link').forEach(link => {
            link.classList.remove('active');
        });

        // add active class to current nav link
        const activeLink = document.querySelector(`.nav-link[data-page="${page}"]`);
        if (activeLink) {
            activeLink.classList.add('active');
        }

        loadPageData(page);
    }

    /**
     * Load data for specific page
     * @param {string} page - Page name
     */
    async function loadPageData(page) {
        switch (page) {
            case 'dashboard':
                await loadDashboard();
                break;
            case 'accounts':
                await loadAccounts();
                break;
            case 'transfers':
                await loadTransfers();
                break;
            case 'transactions':
                await loadTransactions();
                break;
            case 'loans':
                await loadLoans();
                break;
            case 'profile':
                loadProfile();
                break;
            case 'admin':
                // Admin data is loaded by adminComponent
                break;
        }
    }

    /**
     * Load dashboard data
     */
    async function loadDashboard() {
        try {
            // Load accounts
            const accountsData = await api.getAccounts();
            state.accounts = accountsData.accounts || [];

            // Load transactions
            const transactionsData = await api.getUserTransactions();
            state.transactions = transactionsData.transactions || [];

            // Load loans
            const loansData = await api.getLoans();
            state.loans = loansData.loans || [];

            // Update dashboard component
            dashboardComponent.init(state.user);
            dashboardComponent.updateDashboard(state.accounts, state.transactions, state.loans);
        } catch (error) {
            console.error('Error loading dashboard:', error);
        }
    }

    /**
     * Load accounts page data
     */
    async function loadAccounts() {
        try {
            // Load accounts
            const accountsData = await api.getAccounts();
            state.accounts = accountsData.accounts || [];

            // Update accounts component
            accountsComponent.setAccounts(state.accounts);
        } catch (error) {
            console.error('Error loading accounts:', error);
        }
    }

    /**
     * Load transfers page data
     */
    async function loadTransfers() {
        try {
            // Load accounts if not already loaded
            if (state.accounts.length === 0) {
                const accountsData = await api.getAccounts();
                state.accounts = accountsData.accounts || [];
            }

            // Update transfers component
            transfersComponent.setAccounts(state.accounts);
        } catch (error) {
            console.error('Error loading transfers:', error);
        }
    }

    /**
     * Load transactions page data
     */
    async function loadTransactions() {
        try {
            // Load accounts if not already loaded
            if (state.accounts.length === 0) {
                const accountsData = await api.getAccounts();
                state.accounts = accountsData.accounts || [];
            }

            // Load all user transactions
            const transactionsData = await api.getUserTransactions();
            state.transactions = transactionsData.transactions || [];

            // Update transactions component
            transactionsComponent.setData(state.transactions, state.accounts);
        } catch (error) {
            console.error('Error loading transactions:', error);
        }
    }

    /**
     * Load loans page data
     */
    async function loadLoans() {
        try {
            // Load loans
            const loansData = await api.getLoans();
            state.loans = loansData.loans || [];

            // Update loans component
            loansComponent.setLoans(state.loans);
        } catch (error) {
            console.error('Error loading loans:', error);
        }
    }

    /**
     * Load profile page data
     */
    function loadProfile() {
        // Update profile component
        profileComponent.setUserData(state.user);
    }

    /**
     * Handle login form submission
     * @param {Event} e - Form submit event
     */
    async function handleLogin(e) {
        e.preventDefault();

        const username = document.getElementById('login-username').value;
        const password = document.getElementById('login-password').value;

        try {
            const result = await api.login(username, password);

            state.user = result.user;
            showAuthenticatedUI();

            // Initialize admin dashboard if user is admin
            if (state.user.role === 'admin') {
                await adminComponent.initAdminDashboard(state.user);
            }
        } catch (error) {
            const errorElem = document.getElementById('login-error');
            errorElem.textContent = error.message || 'Invalid username or password';
            errorElem.style.display = 'block';
        }
    }

    /**
     * Handle register form submission
     * @param {Event} e - Form submit event
     */
    async function handleRegister(e) {
        e.preventDefault();

        const userData = {
            username: document.getElementById('register-username').value,
            password: document.getElementById('register-password').value,
            email: document.getElementById('register-email').value,
            full_name: document.getElementById('register-fullname').value
        };

        try {
            await api.register(userData);

            // Auto login after registration
            await api.login(userData.username, userData.password);

            const profileData = await api.getProfile();
            state.user = profileData;

            showAuthenticatedUI();
        } catch (error) {
            const errorElem = document.getElementById('register-error');
            errorElem.textContent = error.message || 'Registration failed';
            errorElem.style.display = 'block';
        }
    }

    function logout() {
        api.logout();
        state.user = null;
        state.accounts = [];
        state.transactions = [];
        state.loans = [];

        // remove admin tab if exists -- so regular users cant see or access it
        const adminNavItem = document.querySelector('.nav-link[data-page="admin"]');
        if (adminNavItem) {
            adminNavItem.parentNode.remove();
        }

        document.getElementById('auth-pages').style.display = 'block';
        document.getElementById('main-pages').style.display = 'none';
        document.getElementById('nav-authenticated').style.display = 'none';

        showAuthPage('login');
    }
});