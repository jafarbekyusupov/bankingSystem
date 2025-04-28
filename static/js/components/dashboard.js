class DashboardComponent {
    constructor() {
        this.accounts = [];
        this.transactions = [];
        this.loans = [];
    }

    /**
     * initialize dashboard
     * @param {object} userdata - current user data
     */
    init(userData) {
        this.userData = userData;
        this.updateGreeting();
    }

    /**
     * update dashboard with current data
     * @param {array} accounts - user accounts
     * @param {array} transactions - user transactions
     * @param {array} loans - user loans
     */
    updateDashboard(accounts, transactions, loans) {
        this.accounts = accounts || [];
        this.transactions = transactions || [];
        this.loans = loans || [];

        this.updateAccountSummary();
        this.updateTransactionsList();
        this.updateAccountsList();
    }

    updateGreeting() {
        if (this.userData) {
            document.getElementById('user-fullname').textContent = this.userData.full_name;
        }
    }

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

        const recentTransactions = this.transactions.filter(transaction => {
            return new Date(transaction.created_at) >= thirtyDaysAgo;
        }).length;

        document.getElementById('recent-transactions').textContent = recentTransactions;
    }

    /** update recent transactions list */
    updateTransactionsList() {
        const dashboardTransactions = document.getElementById('dashboard-transactions');

        if (this.transactions.length > 0) {
            dashboardTransactions.innerHTML = '';

            // show latest 5 transactions
            const latestTransactions = [...this.transactions]
                .sort((a, b) => new Date(b.created_at) - new Date(a.created_at))
                .slice(0, 5);

            latestTransactions.forEach(transaction => {
                dashboardTransactions.appendChild(this.createTransactionElement(transaction));
            });
        } else {
            dashboardTransactions.innerHTML = '<div class="empty-state">no recent transactions</div>';
        }
    }

    updateAccountsList() {
        const dashboardAccounts = document.getElementById('dashboard-accounts');

        if (this.accounts.length > 0) {
            dashboardAccounts.innerHTML = '';

            this.accounts.forEach(account => {
                const accountEl = document.createElement('div');
                accountEl.className = 'account-item';
                accountEl.innerHTML = `
                    <div class="account-info">
                        <strong>${account.account_type}</strong> - ${account.account_number}
                    </div>
                    <div class="account-balance">
                        ${this.formatCurrency(account.balance)}
                    </div>
                `;
                dashboardAccounts.appendChild(accountEl);
            });
        } else {
            dashboardAccounts.innerHTML = '<div class="empty-state">no accounts found</div>';
        }
    }

    /**
     * create transaction element
     * @param {object} transaction - transaction data
     * @returns {htmlelement} - transaction element
     */
    createTransactionElement(transaction) {
        const transactionEl = document.createElement('div');
        transactionEl.className = 'transaction-item';

        // format transaction amount and determine css class
        let amountClass = '';
        let amountPrefix = '';

        switch (transaction.transaction_type) {
            case 'deposit':
                amountClass = 'deposit';
                amountPrefix = '+';
                break;
            case 'withdrawal':
                amountClass = 'withdrawal';
                amountPrefix = '-';
                break;
            case 'transfer':
                if (transaction.destination_account_id) {
                    // outgoing transfer
                    amountClass = 'withdrawal';
                    amountPrefix = '-';
                } else {
                    // incoming transfer
                    amountClass = 'deposit';
                    amountPrefix = '+';
                }
                break;
        }

        transactionEl.innerHTML = `
            <div class="transaction-info">
                <div class="transaction-date">${this.formatDate(transaction.created_at)}</div>
                <div class="transaction-desc">${transaction.description || transaction.transaction_type}</div>
            </div>
            <div class="transaction-amount ${amountClass}">
                ${amountPrefix}${this.formatCurrency(transaction.amount)}
            </div>
        `;

        return transactionEl;
    }

    /**
     * format currency amount
     * @param {number} amount - amount to format
     * @returns {string} - formatted currency string
     */
    formatCurrency(amount) {
        return new Intl.NumberFormat('en-US', {
            style: 'currency',
            currency: 'USD'
        }).format(amount);
    }

    /**
     * format date
     * @param {string} datestring - iso date string
     * @returns {string} - formatted date string
     */
    formatDate(dateString) {
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