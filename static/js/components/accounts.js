class AccountsComponent {
    constructor() {
        this.accounts = [];
        this.selectedAccount = null;
        this.initEventListeners();
    }

    initEventListeners() {
        // new account button
        document.getElementById('accounts-new-account-btn').addEventListener('click',this.showNewAccountModal.bind(this));

        // new account form
        document.getElementById('new-account-form').addEventListener('submit',this.handleCreateAccount.bind(this));

        // account actions
        document.getElementById('deposit-btn').addEventListener('click',this.showDepositModal.bind(this));
        document.getElementById('withdraw-btn').addEventListener('click',this.showWithdrawModal.bind(this));
        document.getElementById('close-account-btn').addEventListener('click',this.handleCloseAccount.bind(this));

        // transaction forms
        document.getElementById('deposit-form').addEventListener('submit',this.handleDeposit.bind(this));
        document.getElementById('withdraw-form').addEventListener('submit',this.handleWithdraw.bind(this));

        // modal close buttons
        document.querySelectorAll('#account-modal .close, #new-account-modal .close, #deposit-modal .close, #withdraw-modal .close')
            .forEach(btn => { btn.addEventListener('click', () => { this.closeAllModals();});});
    }

    setAccounts(accounts){ this.accounts = accounts || []; this.updateAccountsUI();}

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
        } else { accountsList.innerHTML = '<div class="empty-state">no accounts found</div>';}
    }

    async viewAccountDetails(accountId) {
        try {
            // get account details
            const acc = await api.getAccount(accountId);
            this.selectedAccount = acc;

            // get account transactions
            const transactionsData = await api.getAccountTransactions(accountId);
            const transactions = transactionsData.transactions || [];

            // update modal ui
            document.getElementById('modal-account-number').textContent = acc.account_number;
            document.getElementById('modal-account-type').textContent = acc.account_type;
            document.getElementById('modal-account-balance').textContent = this.formatCurrency(acc.balance);
            document.getElementById('modal-account-created').textContent = this.formatDate(acc.created_at);

            // show transactions
            const transactionsContainer = document.getElementById('modal-account-transactions');

            if (transactions.length > 0) {
                transactionsContainer.innerHTML = '';

                transactions.forEach(transaction => {
                    transactionsContainer.appendChild(this.createTransactionElement(transaction));
                });
            } else { transactionsContainer.innerHTML = '<div class="empty-state">no transactions found</div>';}

            // show modal
            document.getElementById('account-modal').style.display = 'block';

            // hide close account button if balance is not zero
            const closeAccountBtn = document.getElementById('close-account-btn');
            closeAccountBtn.style.display = acc.balance === 0 ? 'inline-block' : 'none';
        } catch(error){ console.error('error viewing account details:', error); alert('failed to load account details');}
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

    async handleCreateAccount(e) {
        e.preventDefault();

        const accData = {
            account_type: document.getElementById('account-type').value,
            balance: parseFloat(document.getElementById('initial-deposit').value) || 0
        };

        try {
            await api.createAccount(accData);
            this.closeAllModals();

            const accsData = await api.getAccounts();
            this.setAccounts(accsData.accounts);
            alert('account created successfully');
        } catch (error) {
            const errorElem = document.getElementById('new-account-error');
            errorElem.textContent = error.message || 'failed to create account';
            errorElem.style.display = 'block';
        }
    }

    async handleDeposit(e) {
        e.preventDefault();

        const accId = document.getElementById('deposit-account-id').value;
        const amount = parseFloat(document.getElementById('deposit-amount').value);
        const descr = document.getElementById('deposit-description').value;

        try {
            await api.deposit(accId, amount, descr);

            // close modal
            this.closeAllModals();

            // refresh acc details
            await this.viewAccountDetails(accId);

            // reload accs
            const accsData = await api.getAccounts();
            this.setAccounts(accsData.accounts);
        } catch (error) {
            const errorElem = document.getElementById('deposit-error');
            errorElem.textContent = error.message || 'failed to process deposit';
            errorElem.style.display = 'block';
        }
    }

    async handleWithdraw(e) {
        e.preventDefault();
        const accId = document.getElementById('withdraw-account-id').value;
        const amount = parseFloat(document.getElementById('withdraw-amount').value);
        const descr = document.getElementById('withdraw-description').value;
        try {
            await api.withdraw(accId, amount, descr);
            this.closeAllModals();
            await this.viewAccountDetails(accId);
            const accsData = await api.getAccounts();
            this.setAccounts(accsData.accounts);
        } catch (error) {
            const errorElem = document.getElementById('withdraw-error');
            errorElem.textContent = error.message || 'failed to process withdrawal';
            errorElem.style.display = 'block';
        }
    }

    async handleCloseAccount() {
        if (!this.selectedAccount) return;
        if(!confirm('are you sure you want to close this account? this action cannot be undone.')){ return;}
        try {
            await api.closeAccount(this.selectedAccount.account_id);

            // close modal
            this.closeAllModals();

            // reload accs
            const accData = await api.getAccounts();
            this.setAccounts(accData.accounts);

            alert('account closed successfully');
        } catch (error){ alert(error.message || 'failed to close account');}
    }

    createTransactionElement(transaction) {
        const trnscEl = document.createElement('div');
        trnscEl.className = 'transaction-item';

        let mntClass = '';
        let mntPref = '';

        switch (transaction.transaction_type) {
            case 'deposit': mntClass = 'deposit'; mntPref = '+'; break;
            case 'withdrawal': mntClass = 'withdrawal'; mntPref = '-'; break;
            case 'transfer':
                if(transaction.destination_account_id){ mntClass = 'withdrawal'; mntPref = '-';} // outgoing transfer
                else{ mntClass = 'deposit'; mntPref = '+';} // incoming transfer
                break;
        }

        trnscEl.innerHTML = `
            <div class="transaction-info">
                <div class="transaction-date">${this.formatDate(transaction.created_at)}</div>
                <div class="transaction-desc">${transaction.description || transaction.transaction_type}</div>
            </div>
            <div class="transaction-amount ${amountClass}">
                ${amountPrefix}${this.formatCurrency(transaction.amount)}
            </div>
        `;

        return trnscEl;
    }

    closeAllModals(){ document.querySelectorAll('.modal').forEach(modal => { modal.style.display = 'none';});}

    formatCurrency(amount) { return new Intl.NumberFormat('en-US', { style:'currency',currency: 'USD'}).format(amount);}

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