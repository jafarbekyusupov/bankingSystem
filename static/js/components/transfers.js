/** transfers component -- handles transfers ui & funcs */

class TransfersComponent {
    constructor() {
        this.accounts = [];
        this.initEventListeners();
    }

    /** initialize event listeners */
    initEventListeners() {
        // transfer form
        document.getElementById('transfer-form').addEventListener('submit',
            this.handleTransfer.bind(this));

        // acc select handlers
        document.getElementById('from-account').addEventListener('change',
            this.updateFromAccountDetails.bind(this));
        document.getElementById('to-account').addEventListener('change',
            this.updateToAccountDetails.bind(this));
    }

    /**
     * set accounts data
     * @param {Array} accounts - user accounts
     */
    setAccounts(accounts) {
        this.accounts = accounts || [];
        this.updateTransfersUI();
    }

    /**
     * update transfers ui
     */
    updateTransfersUI() {
        const fromAccountSelect = document.getElementById('from-account');
        const toAccountSelect = document.getElementById('to-account');

        // clear existing options
        fromAccountSelect.innerHTML = '<option value="">Select account</option>';
        toAccountSelect.innerHTML = '<option value="">Select account</option>';

        if (this.accounts.length > 0) {
            // add account options
            this.accounts.forEach(account => {
                const option = document.createElement('option');
                option.value = account.account_id;
                option.textContent = `${account.account_type} - ${account.account_number} (${this.formatCurrency(account.balance)})`;

                fromAccountSelect.appendChild(option.cloneNode(true));
                toAccountSelect.appendChild(option);
            });
        }

        // reset form
        document.getElementById('transfer-form').reset();
        document.getElementById('transfer-error').style.display = 'none';

        // clear account previews
        document.getElementById('from-account-info').innerHTML = '<div class="empty-state">Select an account</div>';
        document.getElementById('to-account-info').innerHTML = '<div class="empty-state">Select an account</div>';
    }

    /**
     * update "from" acc details
     */
    updateFromAccountDetails() {
        const accountId = document.getElementById('from-account').value;
        const infoContainer = document.getElementById('from-account-info');

        if (!accountId) {
            infoContainer.innerHTML = '<div class="empty-state">Select an account</div>';
            return;
        }

        const account = this.accounts.find(a => a.account_id === accountId);

        if(account){
            infoContainer.innerHTML = `
                <p><strong>Account Number:</strong> ${account.account_number}</p>
                <p><strong>Type:</strong> ${account.account_type}</p>
                <p><strong>Balance:</strong> ${this.formatCurrency(account.balance)}</p>
            `;
        }
    }

    /** update to acc details */
    updateToAccountDetails() {
        const accountId = document.getElementById('to-account').value;
        const infoContainer = document.getElementById('to-account-info');

        if (!accountId) {
            infoContainer.innerHTML = '<div class="empty-state">Select an account</div>';
            return;
        }

        const account = this.accounts.find(a => a.account_id === accountId);

        if (account) {
            infoContainer.innerHTML = `
                <p><strong>Account Number:</strong> ${account.account_number}</p>
                <p><strong>Type:</strong> ${account.account_type}</p>
                <p><strong>Balance:</strong> ${this.formatCurrency(account.balance)}</p>
            `;
        }
    }

    /**
     * handle transfer form submission
     * @param {Event} e - form submit event
     */
    async handleTransfer(e) {
        e.preventDefault();

        const fromAccountId = document.getElementById('from-account').value;
        const toAccountId = document.getElementById('to-account').value;
        const amount = parseFloat(document.getElementById('transfer-amount').value);
        const description = document.getElementById('transfer-description').value;

        // validation
        if (!fromAccountId || !toAccountId) {
            const errorElem = document.getElementById('transfer-error');
            errorElem.textContent = 'please select both source and destination accounts';
            errorElem.style.display = 'block';
            return;
        }

        if (fromAccountId === toAccountId) {
            const errorElem = document.getElementById('transfer-error');
            errorElem.textContent = 'cannot transfer to the same account';
            errorElem.style.display = 'block';
            return;
        }

        if (!amount || isNaN(amount) || amount <= 0) {
            const errorElem = document.getElementById('transfer-error');
            errorElem.textContent = 'please enter a valid amount greater than zero';
            errorElem.style.display = 'block';
            return;
        }

        try {
            await api.transfer(fromAccountId, toAccountId, amount, description);

            // reset form
            document.getElementById('transfer-form').reset();

            // clear acc previews
            document.getElementById('from-account-info').innerHTML = '<div class="empty-state">Select an account</div>';
            document.getElementById('to-account-info').innerHTML = '<div class="empty-state">Select an account</div>';

            // clear error message
            document.getElementById('transfer-error').style.display = 'none';

            // show success message
            alert('transfer completed successfully');

            // reload accs
            const accountsData = await api.getAccounts();
            this.setAccounts(accountsData.accounts);
        } catch (error) {
            const errorElem = document.getElementById('transfer-error');
            errorElem.textContent = error.message || 'failed to process transfer';
            errorElem.style.display = 'block';
        }
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
}

const transfersComponent = new TransfersComponent();
