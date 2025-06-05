class DashboardComponent {
    constructor() {
        this.accounts = [];
        this.transactions = [];
        this.loans = [];
    }

    init(userData) {
        this.userData = userData;
        this.updateGreeting();
        this.setupCardNavigation();
    }

    updateDashboard(accounts, transactions, loans) {
        this.accounts = accounts || [];
        this.transactions = transactions || [];
        this.loans = loans || [];

        this.updateAccountSummary();
        this.updateTransactionsList();
        this.updateAccountsList();
    }

    updateGreeting(){ if(this.userData){ document.getElementById('user-fullname').textContent = this.userData.full_name;}}

    updateAccountSummary() {
        // update acc count
        document.getElementById('total-accounts').textContent = this.accounts.length;

        // calculate total balance
        const totalBalance = this.accounts.reduce((sum, account) => sum + account.balance, 0);
        document.getElementById('total-balance').textContent = this.formatCurrency(totalBalance);

        // count active loans
        const activeLoans = this.loans.filter(loan => loan.status === 'active').length;
        document.getElementById('active-loans').textContent = activeLoans;

        // count recent transactions -- last 30 days
        const thirtyDaysAgo = new Date();
        thirtyDaysAgo.setDate(thirtyDaysAgo.getDate() - 30);

        const rcntTransacs = this.transactions.filter(transaction => { return new Date(transaction.created_at) >= thirtyDaysAgo;}).length;
        document.getElementById('recent-transactions').textContent = rcntTransacs;
    }

    setupCardNavigation() {
        const summaryCards = document.querySelectorAll('.summary-card.clickable');

        // NEW FEAT -- clickable event listeners for each card on dashboard
        summaryCards.forEach(card => {
            card.addEventListener('click', () => { const section = card.getAttribute('data-section'); if(section){ this.navigateTo(section);}});
        });
    }

    navigateTo(page) {
        const navLink = document.querySelector(`.nav-link[data-page="${page}"]`);
        if(navLink){ navLink.click();}
    }

    updateTransactionsList() {
        const dbrdTransac = document.getElementById('dashboard-transactions');

        if (this.transactions.length > 0) {
            dbrdTransac.innerHTML = '';

            // show latest 5 transactions
            const latestTransactions = [...this.transactions].sort((a, b) => new Date(b.created_at) - new Date(a.created_at)).slice(0, 5);
            latestTransactions.forEach(transaction => { dbrdTransac.appendChild(this.createTransactionElement(transaction));});
        } else{ dbrdTransac.innerHTML = '<div class="empty-state">no recent transactions</div>';}
    }

    updateAccountsList() {
        const dbrdAccs = document.getElementById('dashboard-accounts');

        if (this.accounts.length > 0) {
            dbrdAccs.innerHTML = '';

            this.accounts.forEach(account => {
                const accEl = document.createElement('div');
                accEl.className = 'account-item';
                accEl.innerHTML = `
                    <div class="account-info">
                        <strong>${account.account_type}</strong> - ${account.account_number}
                    </div>
                    <div class="account-balance">
                        ${this.formatCurrency(account.balance)}
                    </div>
                `;
                dbrdAccs.appendChild(accEl);
            });
        } else{ dbrdAccs.innerHTML = '<div class="empty-state">no accounts found</div>';}
    }

    createTransactionElement(transaction) {
        const trnscEl = document.createElement('div');
        trnscEl.className = 'transaction-item';

        // format transaction amount and determine css class
        let mntClass = '';
        let mntPrfx = '';

        switch(transaction.transaction_type){
            case 'deposit': mntClass = 'deposit'; mntPrfx = '+'; break;
            case 'withdrawal': mntClass = 'withdrawal'; mntPrfx = '-'; break;
            case 'transfer':
                if(transaction.destination_account_id){ mntClass = 'withdrawal'; mntPrfx = '-';} // outgoing transfer
                else{ mntClass = 'deposit'; mntPrfx = '+';} // incoming transfer
                break;
        }

        trnscEl.innerHTML = `
            <div class="transaction-info">
                <div class="transaction-date">${this.formatDate(transaction.created_at)}</div>
                <div class="transaction-desc">${transaction.description || transaction.transaction_type}</div>
            </div>
            <div class="transaction-amount ${mntClass}">
                ${mntPrfx}${this.formatCurrency(transaction.amount)}
            </div>
        `;
        return trnscEl;
    }

    formatCurrency(amount){ return new Intl.NumberFormat('en-US',{ style: 'currency',currency: 'USD'}).format(amount);}

    formatDate(dateString){
        const date = new Date(dateString);
        return date.toLocaleDateString('en-US', {
            year: 'numeric',
            month: 'short',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        });
    }
}

const dashboardComponent = new DashboardComponent();