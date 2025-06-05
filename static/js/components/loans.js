class LoansComponent {
    constructor() {
        this.loans = [];
        this.accounts = [];
        this.selectedLoan = null;
        this.initEventListeners();
    }

    initEventListeners() {
        document.getElementById('new-loan-btn').addEventListener('click',this.showNewLoanModal.bind(this));
        document.getElementById('new-loan-form').addEventListener('submit',this.handleLoanApplication.bind(this));
        document.getElementById('payment-form').addEventListener('submit',this.handleLoanPayment.bind(this));
        document.querySelectorAll('#loan-modal .close, #new-loan-modal .close, #payment-modal .close').forEach(btn => { btn.addEventListener('click', () => { this.closeAllModals();});});
    }

    setLoans(loans){ this.loans = loans || []; this.updateLoansUI();}

    setAccounts(accounts){ this.accounts = accounts || [];}

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
                loanItem.querySelector('.view-loan-btn').addEventListener('click', () => { this.viewLoanDetails(loan.loan_id);});
            });
        } else{ loansList.innerHTML = '<div class="empty-state">no loans found</div>';}
    }

    async viewLoanDetails(loanId) {
        try {
            const loan = await api.getLoan(loanId);
            this.selectedLoan = loan;

            let paymentInfo = { payment_amount: 0 };
            try{ paymentInfo = await api.calculateLoanPayment(loanId);}
            catch(error){ console.error('error calculating payment:', error);}

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

            if(loan.status === 'active'){
                const payBtn = document.createElement('button');
                payBtn.className = 'btn btn-success';
                payBtn.innerHTML = '<i class="fas fa-money-bill-wave"></i> make payment';
                payBtn.addEventListener('click', this.showPaymentModal.bind(this));
                actionsContainer.appendChild(payBtn);
            }
            document.getElementById('loan-modal').style.display = 'block';
        } catch(error){ console.error('error viewing loan details:', error); alert('failed to load loan details');}
    }

    showNewLoanModal() {
        document.getElementById('new-loan-form').reset();
        document.getElementById('new-loan-error').style.display = 'none';
        document.getElementById('new-loan-modal').style.display = 'block';
    }

    showPaymentModal() {
        if (!this.selectedLoan) return;

        document.getElementById('payment-form').reset();
        document.getElementById('payment-error').style.display = 'none';
        document.getElementById('payment-loan-id').value = this.selectedLoan.loan_id;

        const accSelect = document.getElementById('payment-account');
        accSelect.innerHTML = '<option value="">Select account</option>';

        if (this.accounts.length > 0) {
            const ctvAccs = this.accounts.filter(account => account.active && account.balance > 0);

            if (ctvAccs.length > 0) {
                ctvAccs.forEach(account => {
                    const opt = document.createElement('opt');
                    opt.value = account.account_id;
                    opt.textContent = `${account.account_type} - ${account.account_number} (${this.formatCurrency(account.balance)})`;
                    accSelect.appendChild(opt);
                });
            } else {
                const opt = document.createElement('opt');
                opt.value = "";
                opt.textContent = "No accounts with available balance";
                opt.disabled = true;
                accSelect.appendChild(opt);
            }
        }

        try{ api.calculateLoanPayment(this.selectedLoan.loan_id).then(info => { document.getElementById('payment-amount').value = info.payment_amount || '';});}
        catch(error){ console.error('error calculating payment:', error);}
        document.getElementById('payment-modal').style.display = 'block';
    }

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
        } catch(error){
            const errorElem = document.getElementById('new-loan-error');
            errorElem.textContent = error.message || 'failed to submit loan app';
            errorElem.style.display = 'block';
        }
    }

    async handleLoanPayment(e) {
        e.preventDefault();

        if (!this.selectedLoan) return;

        const loanId = document.getElementById('payment-loan-id').value;
        const accId = document.getElementById('payment-account').value;
        const amount = parseFloat(document.getElementById('payment-amount').value);

        if (!accId) {
            const errorElem = document.getElementById('payment-error');
            errorElem.textContent = 'Please select an account to pay from';
            errorElem.style.display = 'block';
            return;
        }

        try {
            await api.makeLoanPayment(loanId, amount, accId);
            this.closeAllModals();
            const accountsData = await api.getAccounts();
            this.setAccounts(accountsData.accounts);
            await this.viewLoanDetails(loanId);
            const loansData = await api.getLoans();
            this.setLoans(loansData.loans);
            alert('payment processed successfully');
        } catch(error){
            const errorElem = document.getElementById('payment-error');
            errorElem.textContent = error.message || 'failed to process payment';
            errorElem.style.display = 'block';
        }
    }

    closeAllModals(){ document.querySelectorAll('.modal').forEach(modal => { modal.style.display = 'none';});}
    formatCurrency(amount){ return new Intl.NumberFormat('en-US', { style: 'currency',currency: 'USD'}).format(amount);}
    formatLoanStatus(status){ return status.replace('_', ' ').split(' ').map(word => word.charAt(0).toUpperCase() + word.slice(1)).join(' ');}
}

const loansComponent = new LoansComponent();