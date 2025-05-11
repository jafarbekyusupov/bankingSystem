/** api client for banking system */

class BankAPI {
    constructor() {
        this.baseUrl = '/api/v1';
        this.token = localStorage.getItem('token');
    }

    /**
     * set the authentication token
     * @param {string} token - jwt token
     */
    setToken(token) {
        this.token = token;
        localStorage.setItem('token', token);
    }

    /**
     * clear the authentication token
     */
    clearToken() {
        this.token = null;
        localStorage.removeItem('token');
    }

    /**
     * check if user is authenticated
     * @returns {boolean} - true if authenticated
     */
    isAuthenticated() {
        return !!this.token;
    }

    /**
     * get headers for api requests
     * @returns {object} - headers object
     */
    getHeaders() {
        const headers = {
            'Content-Type': 'application/json'
        };

        if (this.token) {
            headers['Authorization'] = `Bearer ${this.token}`;
        }

        return headers;
    }

    /**
     * make api request
     * @param {string} method - http method
     * @param {string} endpoint - api endpoint
     * @param {object} data - request data
     * @returns {promise} - request promise
     */
    async request(method, endpoint, data = null) {
        const url = `${this.baseUrl}${endpoint}`;
        const options = {
            method,
            headers: this.getHeaders()
        };

        if (data && (method === 'POST' || method === 'PUT')) {
            options.body = JSON.stringify(data);
        }

        try {
            const response = await fetch(url, options);
            const result = await response.json();

            if (!response.ok) {
                throw new Error(result.error || 'api request failed');
            }

            return result;
        } catch (error) {
            console.error('api error:', error);
            throw error;
        }
    }

    /**
     * register a new user
     * @param {object} userData - user registration data
     * @returns {promise} - registration result
     */
    async register(userData) {
        return this.request('POST', '/users/register', userData);
    }

    /**
     * login user
     * @param {string} username - username
     * @param {string} password - password
     * @returns {promise} - login result with token
     */
    async login(username, password) {
        const result = await this.request('POST', '/users/login', { username, password });
        if (result.token) {
            this.setToken(result.token);
        }
        return result;
    }

    logout() {
        this.clearToken();
    }

    /**
     * get current user profile
     * @returns {promise} - user profile
     */
    async getProfile() {
        return this.request('GET', '/users/profile');
    }

    /**
     * update user profile
     * @param {object} profileData - updated profile data
     * @returns {promise} - update result
     */
    async updateProfile(profileData) {
        return this.request('PUT', '/users/profile', profileData);
    }

    /**
     * get all accounts for current user
     * @returns {promise} - list of accounts
     */
    async getAccounts() {
        return this.request('GET', '/accounts');
    }

    /**
     * get account details
     * @param {string} accountId - account id
     * @returns {promise} - account details
     */
    async getAccount(accountId) {
        return this.request('GET', `/accounts/${accountId}`);
    }

    /**
     * create a new account
     * @param {object} accountData - account data
     * @returns {promise} - creation result
     */
    async createAccount(accountData) {
        return this.request('POST', '/accounts', accountData);
    }

    /**
     * close an account
     * @param {string} accountId - account id
     * @returns {promise} - closure result
     */
    async closeAccount(accountId) {
        return this.request('POST', `/accounts/${accountId}/close`);
    }

    /**
     * deposit money to an account
     * @param {string} accountId - account id
     * @param {number} amount - deposit amount
     * @param {string} description - optional description
     * @returns {promise} - deposit result
     */
    async deposit(accountId, amount, description = '') {
        return this.request('POST', `/accounts/${accountId}/deposit`, {
            amount,
            description
        });
    }

    /**
     * withdraw money from an account
     * @param {string} accountId - account id
     * @param {number} amount - withdrawal amount
     * @param {string} description - optional description
     * @returns {promise} - withdrawal result
     */
    async withdraw(accountId, amount, description = '') {
        return this.request('POST', `/accounts/${accountId}/withdraw`, {
            amount,
            description
        });
    }

    /**
     * transfer money between accounts
     * @param {string} fromAccountId - source account id
     * @param {string} toAccountId - destination account id
     * @param {number} amount - transfer amount
     * @param {string} description - optional description
     * @returns {promise} - transfer result
     */
    async transfer(fromAccountId, toAccountId, amount, description = '') {
        return this.request('POST', '/accounts/transfer', {
            from_account_id: fromAccountId,
            to_account_id: toAccountId,
            amount,
            description
        });
    }

    /**
     * get transactions for an account
     * @param {string} accountId - account id
     * @returns {promise} - list of transactions
     */
    async getAccountTransactions(accountId) {
        return this.request('GET', `/accounts/${accountId}/transactions`);
    }

    /**
     * get all transactions for current user
     * @returns {promise} - list of transactions
     */
    async getUserTransactions() {
        return this.request('GET', '/accounts/user/transactions');
    }

    /**
     * get all loans for current user
     * @returns {promise} - list of loans
     */
    async getLoans() {
        return this.request('GET', '/loans');
    }

    /**
     * get loan details
     * @param {string} loanId - loan id
     * @returns {promise} - loan details
     */
    async getLoan(loanId) {
        return this.request('GET', `/loans/${loanId}`);
    }

    /**
     * apply for a new loan
     * @param {object} loanData - loan application data
     * @returns {promise} - application result
     */
    async applyForLoan(loanData) {
        return this.request('POST', '/loans', loanData);
    }

    /**
     * make a payment on a loan
     * @param {string} loanId - loan id
     * @param {number} amount - payment amount
     * @param {string} accountId - account to pay from
     * @returns {promise} - payment result
    */
    async makeLoanPayment(loanId, amount, accountId) {
        return this.request('POST', `/loans/${loanId}/payment`, {
            amount,
            account_id: accountId
        });
    }

    /**
     * calculate monthly payment for a loan
     * @param {string} loanId - loan id
     * @returns {promise} - payment calculation
     */
    async calculateLoanPayment(loanId) {
        return this.request('GET', `/loans/${loanId}/payment-amount`);
    }

    /**
     * approve a loan (admin only)
     * @param {string} loanId - loan id
     * @returns {promise} - approval result
     */
    async approveLoan(loanId) {
        return this.request('POST', `/loans/${loanId}/approve`);
    }

    /**
     * reject a loan (admin only)
     * @param {string} loanId - loan id
     * @returns {promise} - rejection result
     */
    async rejectLoan(loanId) {
        return this.request('POST', `/loans/${loanId}/reject`);
    }

    /**
     * activate a loan (admin only)
     * @param {string} loanId - loan id
     * @returns {promise} - activation result
     */
    async activateLoan(loanId) {
        return this.request('POST', `/loans/${loanId}/activate`);
    }
}

const api = new BankAPI();
