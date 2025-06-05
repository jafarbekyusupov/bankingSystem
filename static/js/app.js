/** ====================================
 *  --------- BANK SYS MAIN APP --------
 *  ==================================== */

document.addEventListener('DOMContentLoaded', () => {
    const state = {
        currentPage: null,
        user: null,
        accounts: [],
        transactions: [],
        loans: []
    };

    init();

    function init(){ initializeEventListeners(); checkAuth();}

    function initializeEventListeners() {
        document.querySelectorAll('.nav-link').forEach(link => {
            link.addEventListener('click', (e) => {
                e.preventDefault();
                const page = e.target.closest('.nav-link').getAttribute('data-page');
                navigateTo(page);
            });
        });

        // NEW FEAT -- logo link to dashboard
        const logoLink = document.querySelector('.logo .home-link');
        if(logoLink){
            logoLink.addEventListener('click', (e) => {
                e.preventDefault(); navigateTo('dashboard');
            });
        }

        document.getElementById('show-register').addEventListener('click', (e) => {
            e.preventDefault();
            showAuthPage('register');
        });

        document.getElementById('show-login').addEventListener('click', (e) => {
            e.preventDefault();
            showAuthPage('login');
        });

        document.getElementById('logout-btn').addEventListener('click', (e) => {
            e.preventDefault();
            logout();
        });

        document.getElementById('login-form').addEventListener('submit', handleLogin);
        document.getElementById('register-form').addEventListener('submit', handleRegister);

        window.addEventListener('click', (e) => {
            document.querySelectorAll('.modal').forEach(modal => {
                if(e.target === modal){ modal.style.display = 'none';}
            });
        });
    }

    async function checkAuth(){
        if(api.isAuthenticated()){
            try{
                const userData = await api.getProfile();
                state.user = userData;
                showAuthenticatedUI();
                loadDashboard();
                if(state.user.role === 'admin'){ await adminComponent.initAdminDashboard(state.user);}
            }
            catch(error){ logout();}
        } else{ showAuthPage('login');}
    }

    function showAuthenticatedUI(){
        document.getElementById('auth-pages').style.display = 'none';
        document.getElementById('main-pages').style.display = 'block';
        document.getElementById('nav-authenticated').style.display = 'block';
        document.getElementById('user-fullname').textContent = state.user.full_name;
        navigateTo('dashboard');
    }

    function showAuthPage(page){
        document.querySelectorAll('#auth-pages .page').forEach(p =>{ p.classList.remove('active');});
        document.getElementById(`${page}-page`).classList.add('active');
        document.getElementById('login-error').style.display = 'none';
        document.getElementById('register-error').style.display = 'none';
    }

    function navigateTo(page){
        if(state.currentPage === page) return; // skip if already on this page

        // handle admin page SEPARATELY
        if(page === 'admin'){
            if(state.user && state.user.role === 'admin'){ state.currentPage = page; adminComponent.showAdminDashboard();}
            else{ navigateTo('dashboard'); return;} // if not admin ==>> redirect to dashboard
        } else{
            state.currentPage = page;
            // hide all pages
            document.querySelectorAll('#main-pages .page').forEach(p =>{ p.classList.remove('active');});
            // show specified page
            document.getElementById(`${page}-page`).classList.add('active');
        }

        // remove active class from nav links
        document.querySelectorAll('.nav-link').forEach(link =>{ link.classList.remove('active');});

        const activeLink = document.querySelector(`.nav-link[data-page="${page}"]`);
        if(activeLink){ activeLink.classList.add('active');}
        loadPageData(page);
    }

    async function loadPageData(page){
        switch(page){
            case 'dashboard': await loadDashboard(); break;
            case 'accounts': await loadAccounts(); break;
            case 'transfers': await loadTransfers(); break;
            case 'transactions': await loadTransactions(); break;
            case 'loans': await loadLoans(); break;
            case 'profile': loadProfile(); break;
            case 'admin': break;
        }
    }

    async function loadDashboard(){
        try{
            const accountsData = await api.getAccounts();
            state.accounts = accountsData.accounts || [];

            const transactionsData = await api.getUserTransactions();
            state.transactions = transactionsData.transactions || [];

            const loansData = await api.getLoans();
            state.loans = loansData.loans || [];
            dashboardComponent.init(state.user);
            dashboardComponent.updateDashboard(state.accounts, state.transactions, state.loans);
        } catch(error){ console.error('Error loading dashboard:', error);}
    }

    async function loadAccounts(){
        try{
            const accountsData = await api.getAccounts();
            state.accounts = accountsData.accounts || [];
            accountsComponent.setAccounts(state.accounts);
        } catch(error){ console.error('Error loading accounts:', error);}
    }

    async function loadTransfers(){
        try{
            if(state.accounts.length === 0){
                const accountsData = await api.getAccounts();
                state.accounts = accountsData.accounts || [];
            }
            transfersComponent.setAccounts(state.accounts);
        } catch(error){ console.error('Error loading transfers:', error);}
    }

    async function loadTransactions(){
        try{
            if(state.accounts.length === 0){
                const accountsData = await api.getAccounts();
                state.accounts = accountsData.accounts || [];
            }
            const transactionsData = await api.getUserTransactions();
            state.transactions = transactionsData.transactions || [];
            transactionsComponent.setData(state.transactions, state.accounts);
        } catch (error){ console.error('Error loading transactions:', error);}
    }

    async function loadLoans(){
        try{
            const loansData = await api.getLoans();
            state.loans = loansData.loans || [];
            if(state.accounts.length === 0){
                const accountsData = await api.getAccounts();
                state.accounts = accountsData.accounts || [];
            }
            // NEW FEATURE - upd loans as well as accounts data (balance)
            loansComponent.setLoans(state.loans);
            loansComponent.setAccounts(state.accounts);
        } catch(error){ console.error('Error loading loans:', error);}
    }

    function loadProfile(){ profileComponent.setUserData(state.user);}

    async function handleLogin(e){
        e.preventDefault();
        const username = document.getElementById('login-username').value;
        const password = document.getElementById('login-password').value;

        try{
            const result = await api.login(username, password);
            state.user = result.user;
            showAuthenticatedUI();
            if(state.user.role === 'admin'){ await adminComponent.initAdminDashboard(state.user);}

        } catch(error){
            const errorElem = document.getElementById('login-error');
            errorElem.textContent = error.message || 'Invalid username or password';
            errorElem.style.display = 'block';
        }
    }

    async function handleRegister(e){
        e.preventDefault();

        const userData ={
            username: document.getElementById('register-username').value,
            password: document.getElementById('register-password').value,
            email: document.getElementById('register-email').value,
            full_name: document.getElementById('register-fullname').value
        };

        try{
            await api.register(userData);
            await api.login(userData.username, userData.password);
            const profileData = await api.getProfile();
            state.user = profileData;
            showAuthenticatedUI();
        } catch (error){
            const errorElem = document.getElementById('register-error');
            errorElem.textContent = error.message || 'Registration failed';
            errorElem.style.display = 'block';
        }
    }

    function logout(){
        api.logout();
        state.user = null;
        state.accounts = [];
        state.transactions = [];
        state.loans = [];

        // remove admin tab if exists -- so regular users cant see or access it
        const adminNavItem = document.querySelector('.nav-link[data-page="admin"]');
        if(adminNavItem){ adminNavItem.parentNode.remove();}

        document.getElementById('auth-pages').style.display = 'block';
        document.getElementById('main-pages').style.display = 'none';
        document.getElementById('nav-authenticated').style.display = 'none';
        showAuthPage('login');
    }
});