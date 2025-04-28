class TransactionsComponent {
    constructor() {
        this.transactions = [];
        this.accounts = [];
        this.initEventListeners();
    }

    initEventListeners() {
        // filter controls
        document.getElementById('transaction-account').addEventListener('change',
            this.filterTransactions.bind(this));
        document.getElementById('transaction-type').addEventListener('change',
            this.filterTransactions.bind(this));
    }

    /**
     * set transactions and accounts data
     * @param {Array} transactions - user transactions
     * @param {Array} accounts - user accounts
     */
    setData(transactions, accounts) {
        this.transactions = transactions || [];
        this.accounts = accounts || [];
        this.updateTransactionsUI();
    }

    /** upd transactions ui */
    updateTransactionsUI() {
        // populate account filter
        const accountSelect = document.getElementById('transaction-account');
        accountSelect.innerHTML = '<option value="all">All Accounts</option>';

        this.accounts.forEach(account => {
            const option = document.createElement('option');
            option.value = account.account_id;
            option.textContent = `${account.account_type} - ${account.account_number}`;
            accountSelect.appendChild(option);
        });

        // disp transactions
        this.filterTransactions();
    }

    /** filter transactions based on selected options */
    filterTransactions() {
        const accountId = document.getElementById('transaction-account').value;
        const transactionType = document.getElementById('transaction-type').value;
        const transactionsList = document.getElementById('transactions-list');

        // filter transacs
        let filteredTransactions = [...this.transactions];

        if (accountId !== 'all') {
            filteredTransactions = filteredTransactions.filter(t =>
                t.account_id === accountId || t.destination_account_id === accountId
            );
        }

        if (transactionType !== 'all') {
            filteredTransactions = filteredTransactions.filter(t =>
                t.transaction_type === transactionType
            );
        }

        // sort transacs by recency date -- newest to oldest
        filteredTransactions.sort((a, b) => new Date(b.created_at) - new Date(a.created_at));

        // disp transacs
        if (filteredTransactions.length > 0) {
            transactionsList.innerHTML = '';

            filteredTransactions.forEach(transaction => {
                transactionsList.appendChild(this.createTransactionElement(transaction));
            });
        } else {
            transactionsList.innerHTML = '<div class="empty-state">No transactions found</div>';
        }
    }

    /**
     * create transaction element
     * @param {Object} transaction - data
     * @returns {HTMLElement} - element
     */
    createTransactionElement(transaction) {
        const transactionEl = document.createElement('div');
        transactionEl.className = 'transaction-item';

        // get acc info
        let accountInfo = 'Unknown Account';
        const account = this.accounts.find(a => a.account_id === transaction.account_id);

        if(account){ accountInfo = `${account.account_type} - ${account.account_number}`;}

        // format transaction amount & determ css class
        let amountClass = '';
        let amountPrefix = '';
        let detailsText = '';

        switch (transaction.transaction_type) {
            case 'deposit':
                amountClass = 'deposit';
                amountPrefix = '+';
                detailsText = `Deposit to ${accountInfo}`;
                break;
            case 'withdrawal':
                amountClass = 'withdrawal';
                amountPrefix = '-';
                detailsText = `Withdrawal from ${accountInfo}`;
                break;
            case 'transfer':
                if (transaction.destination_account_id) {
                    // transfer
                    amountClass = 'withdrawal';
                    amountPrefix = '-';

                    // find destination acc
                    const destAccount = this.accounts.find(a => a.account_id === transaction.destination_account_id);
                    const destAccountInfo = destAccount ?
                        `${destAccount.account_type} - ${destAccount.account_number}` :
                        'Unknown Account';

                    detailsText = `Transfer from ${accountInfo} to ${destAccountInfo}`;
                } else {
                    // incoming transfer -- which wont liekly to happen w our api struct, but still
                    amountClass = 'deposit';
                    amountPrefix = '+';
                    detailsText = `Transfer to ${accountInfo}`;
                }
                break;
        }

        transactionEl.innerHTML = `
            <div class="transaction-info">
                <div class="transaction-date">${this.formatDate(transaction.created_at)}</div>
                <div class="transaction-details">${detailsText}</div>
                <div class="transaction-desc">${transaction.description || 'No description'}</div>
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
     * @returns {string} - formatted currency str
     */
    formatCurrency(amount) {
        return new Intl.NumberFormat('en-US', {
            style: 'currency',
            currency: 'USD'
        }).format(amount);
    }

    /**
     * format date
     * @param {string} dateString - iso date str
     * @returns {string} - formatted date str
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

const transactionsComponent = new TransactionsComponent();
