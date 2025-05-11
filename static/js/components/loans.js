/**
 * loans component
 * handles loans ui and functionality
 */

class LoansComponent {
    constructor() {
        this.loans = [];
        this.accounts = [];
        this.selectedLoan = null;
        this.initEventListeners();
    }

    initEventListeners() {
        // new loan btn
        document.getElementById('new-loan-btn').addEventListener('click',
            this.showNewLoanModal.bind(this));

        // new loan form
        document.getElementById('new-loan-form').addEventListener('submit',
            this.handleLoanApplication.bind(this));

        // payment form
        document.getElementById('payment-form').addEventListener('submit',
            this.handleLoanPayment.bind(this));

        // modal close btns
        document.querySelectorAll('#loan-modal .close, #new-loan-modal .close, #payment-modal .close')
            .forEach(btn => {
                btn.addEventListener('click', () => {
                    this.closeAllModals();
                });
            });
    }

    /**
     * set loans data
     * @param {Array} loans - user loans
     */
    setLoans(loans) {
        this.loans = loans || [];
        this.updateLoansUI();
    }

    /**
     * Set accounts data
     * @param {Array} accounts - user accounts
     */
    setAccounts(accounts) {
        this.accounts = accounts || [];
    }

    /**
     * upd loans ui
     */
    updateLoansUI() {
        const loansList = document.getElementById('loans-list');

        if (this.loans.length > 0) {
            loansList.innerHTML = '';

            this.loans.forEach(loan => {
                const loanItem = document.createElement('div');
                loanItem.className = 'loan-item';
                loanItem.dataset.id = loan.loan_id;

                loanItem.innerHTML = `
                    <div class="loan-info">
                        <h4>${loan.loan_type} Loan</h4>
                        <div><strong>Amount:</strong> ${this.formatCurrency(loan.amount)}</div>
                        <div><strong>Status:</strong> <span class="loan-status ${loan.status}">${this.formatLoanStatus(loan.status)}</span></div>
                    </div>
                    <div class="loan-actions">
                        <button class="btn btn-primary view-loan-btn">view details</button>
                    </div>
                `;

                loansList.appendChild(loanItem);

                // add listener to view btn
                loanItem.querySelector('.view-loan-btn').addEventListener('click', () => {
                    this.viewLoanDetails(loan.loan_id);
                });
            });
        } else {
            loansList.innerHTML = '<div class="empty-state">no loans found</div>';
        }
    }

    /**
     * view loan details
     * @param {string} loanId - loan id
     */
    async viewLoanDetails(loanId) {
        try {
            const loan = await api.getLoan(loanId);
            this.selectedLoan = loan;

            let paymentInfo = { payment_amount: 0 };

            try {
                paymentInfo = await api.calculateLoanPayment(loanId);
            } catch (error) {
                console.error('error calculating payment:', error);
            }

            document.getElementById('modal-loan-type').textContent = loan.loan_type;
            document.getElementById('modal-loan-amount').textContent = this.formatCurrency(loan.amount);
            document.getElementById('modal-loan-rate').textContent = loan.interest_rate;
            document.getElementById('modal-loan-term').textContent = loan.term_months;
            document.getElementById('modal-loan-status').textContent = this.formatLoanStatus(loan.status);
            document.getElementById('modal-loan-payment').textContent = this.formatCurrency(paymentInfo.payment_amount);
            document.getElementById('modal-loan-balance').textContent = this.formatCurrency(loan.balance);
            document.getElementById('modal-loan-purpose').textContent = loan.purpose || 'not specified';

            const actionsContainer = document.getElementById('loan-actions');
            actionsContainer.innerHTML = '';

            if (loan.status === 'active') {
                const payBtn = document.createElement('button');
                payBtn.className = 'btn btn-success';
                payBtn.innerHTML = '<i class="fas fa-money-bill-wave"></i> make payment';
                payBtn.addEventListener('click', this.showPaymentModal.bind(this));
                actionsContainer.appendChild(payBtn);
            }
            document.getElementById('loan-modal').style.display = 'block';
        } catch (error) {
            console.error('error viewing loan details:', error);
            alert('failed to load loan details');
        }
    }

    /**
     * show new loan modal
     */
    showNewLoanModal() {
        document.getElementById('new-loan-form').reset();
        document.getElementById('new-loan-error').style.display = 'none';

        document.getElementById('new-loan-modal').style.display = 'block';
    }

    /**
     * show loan payment modal
     */
    showPaymentModal() {
        if (!this.selectedLoan) return;

        document.getElementById('payment-form').reset();
        document.getElementById('payment-error').style.display = 'none';

        document.getElementById('payment-loan-id').value = this.selectedLoan.loan_id;

        const accountSelect = document.getElementById('payment-account');
        accountSelect.innerHTML = '<option value="">Select account</option>';

        if (this.accounts.length > 0) {
            const activeAccounts = this.accounts.filter(account => account.active && account.balance > 0);

            if (activeAccounts.length > 0) {
                activeAccounts.forEach(account => {
                    const option = document.createElement('option');
                    option.value = account.account_id;
                    option.textContent = `${account.account_type} - ${account.account_number} (${this.formatCurrency(account.balance)})`;
                    accountSelect.appendChild(option);
                });
            } else {
                const option = document.createElement('option');
                option.value = "";
                option.textContent = "No accounts with available balance";
                option.disabled = true;
                accountSelect.appendChild(option);
            }
        }

        // pre-fill payment amount
        try {
            api.calculateLoanPayment(this.selectedLoan.loan_id).then(info => {
                document.getElementById('payment-amount').value = info.payment_amount || '';
            });
        } catch (error) {
            console.error('error calculating payment:', error);
        }

        // show modal
        document.getElementById('payment-modal').style.display = 'block';
    }

    /**
     * handle loan app form submit
     * @param {Event} e - form submit event
     */
    async handleLoanApplication(e) {
        e.preventDefault();

        const loanData = {
            loan_type: document.getElementById('loan-type').value,
            amount: parseFloat(document.getElementById('loan-amount').value),
            term_months: parseInt(document.getElementById('loan-term').value),
            interest_rate: parseFloat(document.getElementById('loan-rate').value),
            purpose: document.getElementById('loan-purpose').value
        };

        try {
            await api.applyForLoan(loanData);

            this.closeAllModals();

            alert('loan app submitted successfully');

            const loansData = await api.getLoans();
            this.setLoans(loansData.loans);
        } catch (error) {
            const errorElem = document.getElementById('new-loan-error');
            errorElem.textContent = error.message || 'failed to submit loan app';
            errorElem.style.display = 'block';
        }
    }

    /**
     * handle loan payment form submit
     * @param {Event} e - form submit event
     */
    async handleLoanPayment(e) {
        e.preventDefault();

        if (!this.selectedLoan) return;

        const loanId = document.getElementById('payment-loan-id').value;
        const accountId = document.getElementById('payment-account').value;
        const amount = parseFloat(document.getElementById('payment-amount').value);

        if (!accountId) {
            const errorElem = document.getElementById('payment-error');
            errorElem.textContent = 'Please select an account to pay from';
            errorElem.style.display = 'block';
            return;
        }

        try {
            await api.makeLoanPayment(loanId, amount, accountId);

            this.closeAllModals();

            const accountsData = await api.getAccounts();
            this.setAccounts(accountsData.accounts);

            await this.viewLoanDetails(loanId);

            const loansData = await api.getLoans();
            this.setLoans(loansData.loans);

            alert('payment processed successfully');
        } catch (error) {
            const errorElem = document.getElementById('payment-error');
            errorElem.textContent = error.message || 'failed to process payment';
            errorElem.style.display = 'block';
        }
    }

    /**
     * close all modals
     */
    closeAllModals() {
        document.querySelectorAll('.modal').forEach(modal => {
            modal.style.display = 'none';
        });
    }

    /**
     * format currency
     * @param {number} amount - amount to format
     * @returns {string}
     */
    formatCurrency(amount) {
        return new Intl.NumberFormat('en-US', {
            style: 'currency',
            currency: 'USD'
        }).format(amount);
    }

    /**
     * format loan status
     * @param {string} status - loan status
     * @returns {string}
     */
    formatLoanStatus(status) {
        return status.replace('_', ' ').split(' ')
            .map(word => word.charAt(0).toUpperCase() + word.slice(1))
            .join(' ');
    }
}

// create and export loans component instance
const loansComponent = new LoansComponent();