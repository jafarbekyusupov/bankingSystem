/**
 * banking system main app
 * integrates ALL components & handles app flow
 */

document.addEventListener('DOMContentLoaded', () => {
    // app stae
    const state = {
        currentPage: null,
        user: null,
        accounts: [],
        transactions: [],
        loans: []
    };

    // initailize the app
    init();

    function init() {
        initializeEventListeners();

        checkAuth();
    }

    function initializeEventListeners() {
        // links
        document.querySelectorAll('.nav-link').forEach(link => {
            link.addEventListener('click', (e) => {
                e.preventDefault();
                const page = e.target.closest('.nav-link').getAttribute('data-page');
                navigateTo(page);
            });
        });

        // auth form links
        document.getElementById('show-register').addEventListener('click', (e) => {
            e.preventDefault();
            showAuthPage('register');
        });

        document.getElementById('show-login').addEventListener('click', (e) => {
            e.preventDefault();
            showAuthPage('login');
        });

        // logout btn
        document.getElementById('logout-btn').addEventListener('click', (e) => {
            e.preventDefault();
            logout();
        });

        // auth forms
        document.getElementById('login-form').addEventListener('submit', handleLogin);
        document.getElementById('register-form').addEventListener('submit', handleRegister);

        // close modals when clicking outside
        window.addEventListener('click', (e) => {
            document.querySelectorAll('.modal').forEach(modal => {
                if (e.target === modal) {
                    modal.style.display = 'none';
                }
            });
        });
    }

    /** check auth status */
    async function checkAuth() {
        if (api.isAuthenticated()) {
            try {
                // get cur user profile
                const userData = await api.getProfile();
                state.user = userData;

                showAuthenticatedUI();

                loadDashboard();
            }
            catch(error){ // in case token invalid or expired
                logout();
            }
        } else{ // show login page
            showAuthPage('login');
        }
    }

    /** show authenticated UI */
    function showAuthenticatedUI() {
        document.getElementById('auth-pages').style.display = 'none';
        document.getElementById('main-pages').style.display = 'block';
        document.getElementById('nav-authenticated').style.display = 'block';

        // set username
        document.getElementById('user-fullname').textContent = state.user.full_name;

        // to dashboard by default
        navigateTo('dashboard');
    }

    /**
     * show partic-r auth page
     * @param {string} page - auth page name ('login' or 'register')
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
     * to specific page
     * @param {string} page - page name
     */
    function navigateTo(page) {
        // skip if already on this page
        if (state.currentPage === page) return;

        state.currentPage = page;

        // hide all pages
        document.querySelectorAll('#main-pages .page').forEach(p => {
            p.classList.remove('active');
        });

        // show specified page
        document.getElementById(`${page}-page`).classList.add('active');

        // remove active class from nav links
        document.querySelectorAll('.nav-link').forEach(link => {
            link.classList.remove('active');
        });

        // add active class to cur nav link
        const activeLink = document.querySelector(`.nav-link[data-page="${page}"]`);
        if (activeLink) {
            activeLink.classList.add('active');
        }

        // load data for page
        loadPageData(page);
    }

    /**
     * load data for specific page
     * @param {string} page - paeg name
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
        }
    }

    /**
     * load dashboard data
     */
    async function loadDashboard() {
        try {
            // load accs
            const accountsData = await api.getAccounts();
            state.accounts = accountsData.accounts || [];

            // load transacs
            const transactionsData = await api.getUserTransactions();
            state.transactions = transactionsData.transactions || [];

            // load loans
            const loansData = await api.getLoans();
            state.loans = loansData.loans || [];

            // upd dashboard component
            dashboardComponent.init(state.user);
            dashboardComponent.updateDashboard(state.accounts, state.transactions, state.loans);
        } catch (error) {
            console.error('Error loading dashboard:', error);
        }
    }

    /** load accounts page data */
    async function loadAccounts() {
        try {
            // load accs
            const accountsData = await api.getAccounts();
            state.accounts = accountsData.accounts || [];

            // upd accs
            accountsComponent.setAccounts(state.accounts);
        } catch (error) {
            console.error('Error loading accounts:', error);
        }
    }

    /**
     * load transfers page data
     */
    async function loadTransfers() {
        try {
            // load acs if not already loaded
            if (state.accounts.length === 0) {
                const accountsData = await api.getAccounts();
                state.accounts = accountsData.accounts || [];
            }

            // upd transfers
            transfersComponent.setAccounts(state.accounts);
        } catch (error) {
            console.error('Error loading transfers:', error);
        }
    }

    /** load transactions page data */
    async function loadTransactions() {
        try {
            // load accounts if not already loaded
            if (state.accounts.length === 0) {
                const accountsData = await api.getAccounts();
                state.accounts = accountsData.accounts || [];
            }

            // load all user transactions
            const transactionsData = await api.getUserTransactions();
            state.transactions = transactionsData.transactions || [];

            // upd transactions component
            transactionsComponent.setData(state.transactions, state.accounts);
        } catch (error) {
            console.error('Error loading transactions:', error);
        }
    }

    /** load loans page data */
    async function loadLoans() {
        try {
            // load loans
            const loansData = await api.getLoans();
            state.loans = loansData.loans || [];

            // upd loans component
            loansComponent.setLoans(state.loans);
        } catch (error) {
            console.error('Error loading loans:', error);
        }
    }

    /** load profile page data */
    function loadProfile() {
        // upd profile component
        profileComponent.setUserData(state.user);
    }

    /**
     * handle login form submission
     * @param {Event} e - form submit event
     */
    async function handleLogin(e) {
        e.preventDefault();

        const username = document.getElementById('login-username').value;
        const password = document.getElementById('login-password').value;

        try{
            const result = await api.login(username, password);

            state.user = result.user;
            showAuthenticatedUI();
        }
        catch(error){
            const errorElem = document.getElementById('login-error');
            errorElem.textContent = error.message || 'Invalid username or password';
            errorElem.style.display = 'block';
        }
    }

    /**
     * handle register form submission
     * @param {Event} e - form submit event
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

            // auto login after register
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

    /**
     * logout user
     */
    function logout() {
        api.logout();
        state.user = null;
        state.accounts = [];
        state.transactions = [];
        state.loans = [];

        // Show login page
        document.getElementById('auth-pages').style.display = 'block';
        document.getElementById('main-pages').style.display = 'none';
        document.getElementById('nav-authenticated').style.display = 'none';

        showAuthPage('login');
    }
});