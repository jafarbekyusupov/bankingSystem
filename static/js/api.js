class BankAPI {
    constructor(){ this.baseUrl = '/api/v1'; this.token = localStorage.getItem('token');}

    setToken(token){ this.token = token; localStorage.setItem('token', token);}
    clearToken(){ this.token = null; localStorage.removeItem('token');}
    isAuthenticated(){ return !!this.token;}

    getHeaders() {
        const headers = {'Content-Type': 'application/json'};
        if(this.token){ headers['Authorization'] = `Bearer ${this.token}`;}
        return headers;
    }

    async request(method, endpoint, data = null) {
        const url = `${this.baseUrl}${endpoint}`;
        const options = { method,headers: this.getHeaders()};
        if(data && (method === 'POST' || method === 'PUT')){ options.body = JSON.stringify(data);}
        try {
            const resp = await fetch(url, options);
            const res = await resp.json();
            if(!resp.ok){ throw new Error(res.error || 'api request failed');}
            return res;
        } catch(error){ console.error('api error:', error); throw error;}
    }

    async register(userData){ return this.request('POST', '/users/register', userData);}

    async login(username, password) {
        const result = await this.request('POST', '/users/login', { username, password });
        if(result.token){ this.setToken(result.token);}
        return result;
    }

    logout(){ this.clearToken();}

    async getProfile(){ return this.request('GET', '/users/profile');}
    async updateProfile(profileData){ return this.request('PUT', '/users/profile', profileData);}

    async getAccounts(){ return this.request('GET', '/accounts');}
    async getAccount(accountId){ return this.request('GET', `/accounts/${accountId}`);}

    async createAccount(accountData){ return this.request('POST', '/accounts', accountData);}
    async closeAccount(accountId){ return this.request('POST', `/accounts/${accountId}/close`);}

    async deposit(accountId, amount, description = '') { return this.request('POST', `/accounts/${accountId}/deposit`, { amount,  description});}
    async withdraw(accountId, amount, description = ''){ return this.request('POST', `/accounts/${accountId}/withdraw`, { amount,description});}
    async transfer(fromAccountId, toAccountId, amount, description = '') { return this.request('POST', '/accounts/transfer', { from_account_id: fromAccountId,to_account_id: toAccountId,amount,description});}

    async getAccountTransactions(accountId){ return this.request('GET', `/accounts/${accountId}/transactions`);}
    async getUserTransactions(){ return this.request('GET', '/accounts/user/transactions');}

    async getLoans(){ return this.request('GET', '/loans');}
    async getLoan(loanId){ return this.request('GET', `/loans/${loanId}`);}

    async applyForLoan(loanData){ return this.request('POST', '/loans', loanData);}
    async makeLoanPayment(loanId, amount, accountId){ return this.request('POST', `/loans/${loanId}/payment`,{ amount,account_id:accountId});}
    async calculateLoanPayment(loanId){ return this.request('GET', `/loans/${loanId}/payment-amount`);}


    /*****================ ADMIN SPECIFIC STUFF ================*****/
    // return types -- {promise} -- func result [approval/rejection/activation]
    async approveLoan(loanId){ return this.request('POST', `/loans/${loanId}/approve`);}
    async rejectLoan(loanId){ return this.request('POST', `/loans/${loanId}/reject`);}
    async activateLoan(loanId){ return this.request('POST', `/loans/${loanId}/activate`);}
}

const api = new BankAPI();