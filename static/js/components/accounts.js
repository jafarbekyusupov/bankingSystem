class AccountsComponent {
    constructor() {
        this.accounts = [];
        this.selectedAccount = null;
        this.initEventListeners();
    }

    initEventListeners() {
        // new account button
        document.getElementById('accounts-new-account-btn').addEventListener('click',
            this.showNewAccountModal.bind(this));

        // new account form
        document.getElementById('new-account-form').addEventListener('submit',
            this.handleCreateAccount.bind(this));

        // account actions
        document.getElementById('deposit-btn').addEventListener('click',
            this.showDepositModal.bind(this));
        document.getElementById('withdraw-btn').addEventListener('click',
            this.showWithdrawModal.bind(this));
        document.getElementById('close-account-btn').addEventListener('click',
            this.handleCloseAccount.bind(this));

        // transaction forms
        document.getElementById('deposit-form').addEventListener('submit',
            this.handleDeposit.bind(this));
        document.getElementById('withdraw-form').addEventListener('submit',
            this.handleWithdraw.bind(this));

        // modal close buttons
        document.querySelectorAll('#account-modal .close, #new-account-modal .close, #deposit-modal .close, #withdraw-modal .close')
            .forEach(btn => {
                btn.addEventListener('click', () => {
                    this.closeAllModals();
                });
            });
    }

    /**
     * set accounts data
     * @param {array} accounts - user accounts
     */
    setAccounts(accounts) {
        this.accounts = accounts || [];
        this.updateAccountsUI();
    }

    updateAccountsUI() {
        const accountsList = document.getElementById('accounts-list');

        if (this.accounts.length > 0) {
            accountsList.innerHTML = '';

            this.accounts.forEach(account => {
                const accountCard = document.createElement('div');
                accountCard.className = 'account-card';
                accountCard.dataset.id = account.account_id;
                accountCard.innerHTML = `
                    <div class="account-type">${account.account_type} account</div>
                    <div class="account-number">${account.account_number}</div>
                    <div class="account-balance">${this.formatCurrency(account.balance)}</div>
                    <div class="account-actions">
                        <button class="btn btn-primary view-account-btn">view details</button>
                    </div>
                `;

                accountsList.appendChild(accountCard);

                // add event listener to view button
                accountCard.querySelector('.view-account-btn').addEventListener('click', () => {
                    this.viewAccountDetails(account.account_id);
                });
            });
        } else {
            accountsList.innerHTML = '<div class="empty-state">no accounts found</div>';
        }
    }

    /**
     * view account details
     * @param {string} accountid - account id
     */
    async viewAccountDetails(accountId) {
        try {
            // get account details
            const account = await api.getAccount(accountId);
            this.selectedAccount = account;

            // get account transactions
            const transactionsData = await api.getAccountTransactions(accountId);
            const transactions = transactionsData.transactions || [];

            // update modal ui
            document.getElementById('modal-account-number').textContent = account.account_number;
            document.getElementById('modal-account-type').textContent = account.account_type;
            document.getElementById('modal-account-balance').textContent = this.formatCurrency(account.balance);
            document.getElementById('modal-account-created').textContent = this.formatDate(account.created_at);

            // show transactions
            const transactionsContainer = document.getElementById('modal-account-transactions');

            if (transactions.length > 0) {
                transactionsContainer.innerHTML = '';

                transactions.forEach(transaction => {
                    transactionsContainer.appendChild(this.createTransactionElement(transaction));
                });
            } else {
                transactionsContainer.innerHTML = '<div class="empty-state">no transactions found</div>';
            }

            // show modal
            document.getElementById('account-modal').style.display = 'block';

            // hide close account button if balance is not zero
            const closeAccountBtn = document.getElementById('close-account-btn');
            closeAccountBtn.style.display = account.balance === 0 ? 'inline-block' : 'none';
        } catch (error) {
            console.error('error viewing account details:', error);
            alert('failed to load account details');
        }
    }

    showNewAccountModal() {
        // reset form
        document.getElementById('new-account-form').reset();
        document.getElementById('new-account-error').style.display = 'none';

        // show modal
        document.getElementById('new-account-modal').style.display = 'block';
    }


    showDepositModal() {
        if (!this.selectedAccount) return;

        // reset form
        document.getElementById('deposit-form').reset();
        document.getElementById('deposit-error').style.display = 'none';

        // set account id
        document.getElementById('deposit-account-id').value = this.selectedAccount.account_id;

        // show modal
        document.getElementById('deposit-modal').style.display = 'block';
    }

    showWithdrawModal() {
        if (!this.selectedAccount) return;

        // reset form
        document.getElementById('withdraw-form').reset();
        document.getElementById('withdraw-error').style.display = 'none';

        // set account id
        document.getElementById('withdraw-account-id').value = this.selectedAccount.account_id;

        // show modal
        document.getElementById('withdraw-modal').style.display = 'block';
    }

    /**
     * handle create account form submission
     * @param {event} e - form submit event
     */
    async handleCreateAccount(e) {
        e.preventDefault();

        const accountData = {
            account_type: document.getElementById('account-type').value,
            balance: parseFloat(document.getElementById('initial-deposit').value) || 0
        };

        try {
            await api.createAccount(accountData);

            // close modal
            this.closeAllModals();

            // reload accounts
            const accountsData = await api.getAccounts();
            this.setAccounts(accountsData.accounts);

            // show success message
            alert('account created successfully');
        } catch (error) {
            const errorElem = document.getElementById('new-account-error');
            errorElem.textContent = error.message || 'failed to create account';
            errorElem.style.display = 'block';
        }
    }

    /**
     * handle deposit form submission
     * @param {event} e - form submit event
     */
    async handleDeposit(e) {
        e.preventDefault();

        const accountId = document.getElementById('deposit-account-id').value;
        const amount = parseFloat(document.getElementById('deposit-amount').value);
        const description = document.getElementById('deposit-description').value;

        try {
            await api.deposit(accountId, amount, description);

            // close modal
            this.closeAllModals();

            // refresh acc details
            await this.viewAccountDetails(accountId);

            // reload accs
            const accountsData = await api.getAccounts();
            this.setAccounts(accountsData.accounts);
        } catch (error) {
            const errorElem = document.getElementById('deposit-error');
            errorElem.textContent = error.message || 'failed to process deposit';
            errorElem.style.display = 'block';
        }
    }

    /**
     * handle withdraw form submission
     * @param {event} e - form submit event
     */
    async handleWithdraw(e) {
        e.preventDefault();

        const accountId = document.getElementById('withdraw-account-id').value;
        const amount = parseFloat(document.getElementById('withdraw-amount').value);
        const description = document.getElementById('withdraw-description').value;

        try {
            await api.withdraw(accountId, amount, description);

            // close modal
            this.closeAllModals();

            // refresh acc details
            await this.viewAccountDetails(accountId);

            // reload accs
            const accountsData = await api.getAccounts();
            this.setAccounts(accountsData.accounts);
        } catch (error) {
            const errorElem = document.getElementById('withdraw-error');
            errorElem.textContent = error.message || 'failed to process withdrawal';
            errorElem.style.display = 'block';
        }
    }

    async handleCloseAccount() {
        if (!this.selectedAccount) return;

        if (!confirm('are you sure you want to close this account? this action cannot be undone.')) {
            return;
        }

        try {
            await api.closeAccount(this.selectedAccount.account_id);

            // close modal
            this.closeAllModals();

            // reload accs
            const accountsData = await api.getAccounts();
            this.setAccounts(accountsData.accounts);

            alert('account closed successfully');
        } catch (error) {
            alert(error.message || 'failed to close account');
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

    closeAllModals() {
        document.querySelectorAll('.modal').forEach(modal => {
            modal.style.display = 'none';
        });
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

const accountsComponent = new AccountsComponent();