class AdminComponent {
    constructor() {
        this.users = [];
        this.pendingLoans = [];
        this.approvedLoans = [];
        this.initEventListeners();
    }

    initEventListeners(){}

    isAdmin(user){ return user && user.role === 'admin';}

    async initAdminDashboard(user){
        if(!this.isAdmin(user)){ return;}
        this.addAdminNavItem();
        await this.createAdminPage();
    }

    addAdminNavItem() {
        const navList = document.querySelector('.nav-list');
        if(document.querySelector('.nav-link[data-page="admin"]')){ return;}

        // create admin nav item
        const adminNavItem = document.createElement('li');
        adminNavItem.innerHTML = `<a href="#" class="nav-link" data-page="admin"><i class="fas fa-shield-alt"></i> Admin</a>`;

        // insert before profile link
        const profileNavItem = document.querySelector('.nav-link[data-page="profile"]').parentNode;
        navList.insertBefore(adminNavItem, profileNavItem);

        // add event listener
        adminNavItem.querySelector('.nav-link').addEventListener('click', (e) => {
            e.preventDefault();
            this.showAdminDashboard();
        });
    }

    async createAdminPage() {
        if(document.getElementById('admin-page')){ return;}
        const adminPage = document.createElement('div');
        adminPage.id = 'admin-page';
        adminPage.className = 'page';
        adminPage.innerHTML = `
            <h2>Admin Dashboard</h2>
            <div class="admin-tabs">
                <div class="tab-links">
                    <a href="#" class="tab-link active" data-tab="users">User Management</a>
                    <a href="#" class="tab-link" data-tab="loan-approvals">Loan Approvals</a>
                    <a href="#" class="tab-link" data-tab="system">System Management</a>
                </div>
                
                <div class="tab-content">
                    <!-- users tab -->
                    <div id="users-tab" class="tab-pane active">
                        <h3>User Management</h3>
                        <div id="users-list"></div>
                    </div>
                    
                    <!-- loan approvals tab -->
                    <div id="loan-approvals-tab" class="tab-pane">
                        <h3>Loan Approvals</h3>
                        <div id="pending-loans"></div>
                        <h3>Approved Loans (Pending Activation)</h3>
                        <div id="approved-loans"></div>
                    </div>
                    
                    <!-- system management tab -->
                    <div id="system-tab" class="tab-pane">
                        <h3>System Management</h3>
                        <div class="stats-cards">
                            <div class="stats-card">
                                <h4>Total Users</h4>
                                <p id="stats-users">0</p>
                            </div>
                            <div class="stats-card">
                                <h4>Total Accounts</h4>
                                <p id="stats-accounts">0</p>
                            </div>
                            <div class="stats-card">
                                <h4>Total Transactions</h4>
                                <p id="stats-transactions">0</p>
                            </div>
                            <div class="stats-card">
                                <h4>Total Loans</h4>
                                <p id="stats-loans">0</p>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            
            <!-- user details modal -->
            <div id="user-details-modal" class="modal">
                <div class="modal-content">
                    <span class="close">&times;</span>
                    <h3>User Details</h3>
                    <div id="user-details"></div>
                    <div id="user-accounts"></div>
                </div>
            </div>
            
            <!-- loan details modal -->
            <div id="admin-loan-modal" class="modal">
                <div class="modal-content">
                    <span class="close">&times;</span>
                    <h3>Loan Details</h3>
                    <div id="admin-loan-details"></div>
                    <div id="admin-loan-actions"></div>
                </div>
            </div>
        `;

        document.getElementById('main-pages').appendChild(adminPage);
        this.addAdminStyles();

        adminPage.querySelectorAll('.tab-link').forEach(link => {
            link.addEventListener('click', (e) => { e.preventDefault(); const tabId = e.target.getAttribute('data-tab');this.showTab(tabId);});
        });

        adminPage.querySelectorAll('.modal .close').forEach(btn => {
            btn.addEventListener('click', () => {
                adminPage.querySelectorAll('.modal').forEach(modal => { modal.style.display = 'none';});
            });
        });

        await this.loadAdminData();
    }

    addAdminStyles() {
        if(document.getElementById('admin-styles')){ return;}
        const style = document.createElement('style');
        style.id = 'admin-styles';
        style.textContent = `
            .admin-tabs {
                margin-top: 2rem;
            }
            
            .tab-links {
                display: flex;
                border-bottom: 1px solid var(--border-color);
                margin-bottom: 1.5rem;
            }
            
            .tab-link {
                padding: 0.75rem 1.5rem;
                margin-right: 0.5rem;
                border-bottom: 3px solid transparent;
                color: var(--gray-dark);
                cursor: pointer;
            }
            
            .tab-link.active {
                border-bottom-color: var(--primary-color);
                color: var(--primary-color);
                font-weight: 600;
            }
            
            .tab-pane {
                display: none;
            }
            
            .tab-pane.active {
                display: block;
            }
            
            .user-item, .admin-loan-item {
                background-color: white;
                border-radius: 8px;
                padding: 1rem;
                margin-bottom: 1rem;
                box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
                display: flex;
                justify-content: space-between;
                align-items: center;
            }
            
            .stats-cards {
                display: grid;
                grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
                gap: 1.5rem;
                margin-top: 1.5rem;
            }
            
            .stats-card {
                background-color: white;
                border-radius: 8px;
                padding: 1.5rem;
                box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
                text-align: center;
            }
            
            .stats-card h4 {
                margin-bottom: 0.5rem;
                color: var(--gray-dark);
            }
            
            .stats-card p {
                font-size: 2rem;
                font-weight: 700;
                color: var(--primary-color);
            }
            
            #user-details table, #admin-loan-details table {
                width: 100%;
                border-collapse: collapse;
                margin-bottom: 1.5rem;
            }
            
            #user-details table th, #admin-loan-details table th {
                text-align: left;
                padding: 0.75rem;
                background-color: var(--gray-light);
            }
            
            #user-details table td, #admin-loan-details table td {
                padding: 0.75rem;
                border-bottom: 1px solid var(--gray-light);
            }
        `;
        document.head.appendChild(style);
    }

    async loadAdminData(){
        try{
            await this.loadUsers();
            await this.loadPendingLoans();
            await this.loadSystemStats();
        } catch(error){ console.error('Error loading admin data:', error);}
    }

    async loadUsers(){
        try{
            const getAllUsers = await fetch('/api/v1/users', { headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}`}});
            if(!getAllUsers.ok){ throw new Error('Failed to load users');}

            const data = await getAllUsers.json();
            this.users = data.users || [];
            this.updateUsersList();
        } catch(error){ console.error('Error loading users:', error);}
    }

    updateUsersList() {
        const usersList = document.getElementById('users-list');

        if (this.users.length > 0) {
            usersList.innerHTML = '';

            this.users.forEach(user => {
                const userItem = document.createElement('div');
                userItem.className = 'user-item';
                userItem.innerHTML = `
                    <div class="user-info">
                        <h4>${user.full_name}</h4>
                        <div><strong>Username:</strong> ${user.username}</div>
                        <div><strong>Email:</strong> ${user.email}</div>
                        <div><strong>Role:</strong> ${user.role}</div>
                    </div>
                    <div class="user-actions">
                        <button class="btn btn-primary view-user-btn" data-id="${user.user_id}">View Details</button>
                    </div>
                `;

                usersList.appendChild(userItem);
            });

            usersList.querySelectorAll('.view-user-btn').forEach(btn => {
                btn.addEventListener('click', (e) => {
                    const userId = e.target.getAttribute('data-id');
                    this.viewUserDetails(userId);
                });
            });
        } else{ usersList.innerHTML = '<div class="empty-state">No users found</div>';}
    }

    async viewUserDetails(userId){
        try{
            const response = await fetch(`/api/v1/users/${userId}`, { headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}`}});
            if(!response.ok){ throw new Error('Failed to load user details');}

            const user = await response.json();

            // get user accs
            const accountsResponse = await fetch(`/api/v1/accounts?user_id=${userId}`, { headers:{ 'Authorization': `Bearer ${localStorage.getItem('token')}`}});

            let accounts = [];
            if(accountsResponse.ok){ const accountsData = await accountsResponse.json(); accounts = accountsData.accounts || [];}

            // upd user details ui
            const userDetails = document.getElementById('user-details');
            userDetails.innerHTML = `
                <table>
                    <tr>
                        <th>Full Name</th>
                        <td>${user.full_name}</td>
                    </tr>
                    <tr>
                        <th>Username</th>
                        <td>${user.username}</td>
                    </tr>
                    <tr>
                        <th>Email</th>
                        <td>${user.email}</td>
                    </tr>
                    <tr>
                        <th>Role</th>
                        <td>${user.role}</td>
                    </tr>
                    <tr>
                        <th>Created</th>
                        <td>${this.formatDate(user.created_at)}</td>
                    </tr>
                </table>
                
                <div class="user-admin-actions">
                    <button class="btn btn-warning edit-user-btn" data-id="${user.user_id}">Edit User</button>
                    <button class="btn btn-danger delete-user-btn" data-id="${user.user_id}">Delete User</button>
                </div>
            `;

            const userAccounts = document.getElementById('user-accounts');

            if (accounts.length > 0) {
                userAccounts.innerHTML = `
                    <h4>User Accounts</h4>
                    <div class="accounts-list">
                        ${accounts.map(account => `
                            <div class="account-item">
                                <div class="account-info">
                                    <strong>${account.account_type}</strong> - ${account.account_number}
                                </div>
                                <div class="account-balance">
                                    ${this.formatCurrency(account.balance)}
                                </div>
                            </div>
                        `).join('')}
                    </div>
                `;
            } else {
                userAccounts.innerHTML = `
                    <h4>User Accounts</h4>
                    <div class="empty-state">No accounts found</div>
                `;
            }

            const editBtn = userDetails.querySelector('.edit-user-btn');
            if(editBtn){ editBtn.addEventListener('click', () => { alert('Edit user functionality would be implemented here');});}

            const deleteBtn = userDetails.querySelector('.delete-user-btn');
            if(deleteBtn){ deleteBtn.addEventListener('click', () => {
                if(confirm('Are you sure you want to delete this user? This action cannot be undone.')){ this.deleteUser(userId);}});
            }
            document.getElementById('user-details-modal').style.display = 'block';
        } catch(error){ console.error('Error viewing user details:', error); alert('Failed to load user details');}
    }

    async deleteUser(userId) {
        try {
            const response = await fetch(`/api/v1/users/${userId}`, {
                method: 'DELETE',
                headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}`}
            });

            if(!response.ok){ throw new Error('Failed to delete user');}
            document.getElementById('user-details-modal').style.display = 'none';
            await this.loadUsers();
            alert('User deleted successfully');
        } catch(error){ console.error('Error deleting user:', error); alert(error.message || 'Failed to delete user');}
    }

    async loadPendingLoans() {
        try {
            const getLoans = await fetch('/api/v1/loans?all=true', { headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}`}});
            if(!getLoans.ok){ throw new Error('Failed to load loans');}

            const data = await getLoans.json();
            const loans = data.loans || [];

            this.pendingLoans = loans.filter(loan => loan.status === 'pending');
            this.approvedLoans = loans.filter(loan => loan.status === 'approved');
            this.updateLoansUI();
        } catch(error){ console.error('Error loading loans:', error);}
    }

    updateLoansUI() {
        const pendingLoansList = document.getElementById('pending-loans');

        if(this.pendingLoans.length>0){
            pendingLoansList.innerHTML = '';
            this.pendingLoans.forEach(loan => {
                const loanItem = document.createElement('div');
                loanItem.className = 'admin-loan-item';

                // find user
                const user = this.users.find(u => u.user_id === loan.user_id) || { full_name: 'Unknown User' };

                loanItem.innerHTML = `
                    <div class="loan-info">
                        <h4>${loan.loan_type} Loan</h4>
                        <div><strong>Amount:</strong> ${this.formatCurrency(loan.amount)}</div>
                        <div><strong>Applicant:</strong> ${user.full_name}</div>
                        <div><strong>Applied:</strong> ${this.formatDate(loan.created_at)}</div>
                    </div>
                    <div class="loan-actions">
                        <button class="btn btn-primary view-loan-btn" data-id="${loan.loan_id}">View Details</button>
                    </div>
                `;
                pendingLoansList.appendChild(loanItem);
            });

            pendingLoansList.querySelectorAll('.view-loan-btn').forEach(btn => {
                btn.addEventListener('click', (e) => {
                    const loanId = e.target.getAttribute('data-id');
                    this.viewLoanDetails(loanId);
                });
            });
        } else{ pendingLoansList.innerHTML = '<div class="empty-state">No pending loan applications</div>';}

        const approvedLoansList = document.getElementById('approved-loans');

        if(this.approvedLoans.length > 0){
            approvedLoansList.innerHTML = '';

            this.approvedLoans.forEach(loan => {
                const loanItem = document.createElement('div');
                loanItem.className = 'admin-loan-item';

                const user = this.users.find(u => u.user_id === loan.user_id) || { full_name: 'Unknown User' };

                loanItem.innerHTML = `
                    <div class="loan-info">
                        <h4>${loan.loan_type} Loan</h4>
                        <div><strong>Amount:</strong> ${this.formatCurrency(loan.amount)}</div>
                        <div><strong>Applicant:</strong> ${user.full_name}</div>
                        <div><strong>Approved:</strong> ${this.formatDate(loan.approved_at)}</div>
                    </div>
                    <div class="loan-actions">
                        <button class="btn btn-primary view-loan-btn" data-id="${loan.loan_id}">View Details</button>
                    </div>
                `;

                approvedLoansList.appendChild(loanItem);
            });

            approvedLoansList.querySelectorAll('.view-loan-btn').forEach(btn => {
                btn.addEventListener('click', (e) => {
                    const loanId = e.target.getAttribute('data-id');
                    this.viewLoanDetails(loanId);
                });
            });
        } else{ approvedLoansList.innerHTML = '<div class="empty-state">No approved loans pending activation</div>';}
    }

    async viewLoanDetails(loanId){
        try {
            const loanDtls = await fetch(`/api/v1/loans/${loanId}`, { headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}`}});
            if(!loanDtls.ok){ throw new Error('Failed to load loan details');}
            const loan = await loanDtls.json();

            const user = this.users.find(u => u.user_id === loan.user_id) || { full_name: 'Unknown User', email: 'Unknown' };

            let monthlyPayment = 'Not calculated';
            try{
                const paymentResponse = await fetch(`/api/v1/loans/${loanId}/payment-amount`, { headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}`}});

                if(paymentResponse.ok){
                    const paymentData = await paymentResponse.json();
                    monthlyPayment = this.formatCurrency(paymentData.payment_amount);
                }
            } catch(error){ console.error('Error calculating payment:', error);}

            const loanDetails = document.getElementById('admin-loan-details');
            loanDetails.innerHTML = `
                <table>
                    <tr>
                        <th>Loan Type</th>
                        <td>${loan.loan_type}</td>
                    </tr>
                    <tr>
                        <th>Amount</th>
                        <td>${this.formatCurrency(loan.amount)}</td>
                    </tr>
                    <tr>
                        <th>Interest Rate</th>
                        <td>${loan.interest_rate}%</td>
                    </tr>
                    <tr>
                        <th>Term</th>
                        <td>${loan.term_months} months</td>
                    </tr>
                    <tr>
                        <th>Monthly Payment</th>
                        <td>${monthlyPayment}</td>
                    </tr>
                    <tr>
                        <th>Status</th>
                        <td>${this.formatLoanStatus(loan.status)}</td>
                    </tr>
                    <tr>
                        <th>Applicant</th>
                        <td>${user.full_name} (${user.email})</td>
                    </tr>
                    <tr>
                        <th>Purpose</th>
                        <td>${loan.purpose || 'Not specified'}</td>
                    </tr>
                    <tr>
                        <th>Applied</th>
                        <td>${this.formatDate(loan.created_at)}</td>
                    </tr>
                    ${loan.approved_at ? `
                    <tr>
                        <th>Approved</th>
                        <td>${this.formatDate(loan.approved_at)}</td>
                    </tr>
                    ` : ''}
                </table>
            `;

            const actionsContainer = document.getElementById('admin-loan-actions');
            actionsContainer.innerHTML = '';

            if(loan.status === 'pending'){
                const approveBtn = document.createElement('button');
                approveBtn.className = 'btn btn-success';
                approveBtn.innerHTML = '<i class="fas fa-check"></i> Approve Loan';
                approveBtn.addEventListener('click', () => { this.approveLoan(loanId);});

                const rejectBtn = document.createElement('button');
                rejectBtn.className = 'btn btn-danger';
                rejectBtn.innerHTML = '<i class="fas fa-times"></i> Reject Loan';
                rejectBtn.addEventListener('click', () => { this.rejectLoan(loanId);});

                actionsContainer.appendChild(approveBtn);
                actionsContainer.appendChild(rejectBtn);
            } else if (loan.status === 'approved') {
                const activateBtn = document.createElement('button');
                activateBtn.className = 'btn btn-success';
                activateBtn.innerHTML = '<i class="fas fa-play"></i> Activate Loan';
                activateBtn.addEventListener('click', () => { this.activateLoan(loanId);});

                actionsContainer.appendChild(activateBtn);
            }

            document.getElementById('admin-loan-modal').style.display = 'block';
        } catch(error){ console.error('Error viewing loan details:', error); alert('Failed to load loan details');}
    }

    async approveLoan(loanId) {
        try {
            const apprvLoan = await fetch(`/api/v1/loans/${loanId}/approve`, {
                method: 'POST',
                headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}`}
            });

            if(!apprvLoan.ok){ throw new Error('Failed to approve loan');}
            document.getElementById('admin-loan-modal').style.display = 'none';
            await this.loadPendingLoans();
            alert('Loan approved successfully');
        } catch(error){ console.error('Error approving loan:', error); alert(error.message || 'Failed to approve loan');}
    }

    async rejectLoan(loanId) {
        try {
            const rjctLoan = await fetch(`/api/v1/loans/${loanId}/reject`, {
                method: 'POST',
                headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}`}
            });

            if(!rjctLoan.ok){ throw new Error('Failed to reject loan');}
            document.getElementById('admin-loan-modal').style.display = 'none';
            await this.loadPendingLoans();
            alert('Loan rejected successfully');
        } catch(error){ console.error('Error rejecting loan:', error); alert(error.message || 'Failed to reject loan');}
    }

    async activateLoan(loanId) {
        try {
            const activateLoan = await fetch(`/api/v1/loans/${loanId}/activate`, {
                method: 'POST', headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}`}});

            if(!activateLoan.ok){ throw new Error('Failed to activate loan');}
            document.getElementById('admin-loan-modal').style.display = 'none';
            await this.loadPendingLoans();
            alert('Loan activated successfully');
        } catch(error){ console.error('Error activating loan:', error); alert(error.message || 'Failed to activate loan');}
    }

    async loadSystemStats() {
        try {
            document.getElementById('stats-users').textContent = this.users.length;
            const accsRsp = await fetch('/api/v1/accounts?all=true', {
                headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}`}});

            let accCnt = 0;
            if(accsRsp.ok){ const accountsData = await accsRsp.json(); accCnt = (accountsData.accounts || []).length;}

            document.getElementById('stats-accounts').textContent = accCnt;

            const transacRsp = await fetch('/api/v1/accounts/user/transactions', { headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}`}});

            let transacCnt = 0;
            if (transacRsp.ok){ const transactionsData = await transacRsp.json(); transacCnt = (transactionsData.transactions || []).length;}

            document.getElementById('stats-transactions').textContent = transacCnt;

            const loanRsp = await fetch('/api/v1/loans?all=true', { headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}`}});

            let loanCnt = 0;
            if(loanRsp.ok){ const loansData = await loanRsp.json(); loanCnt = (loansData.loans || []).length;}
            document.getElementById('stats-loans').textContent = loanCnt;
        } catch(error){ console.error('Error loading system stats:', error);}
    }

    showAdminDashboard(){
        document.querySelectorAll('#main-pages .page').forEach(p => { p.classList.remove('active');});
        document.getElementById('admin-page').classList.add('active');
        document.querySelectorAll('.nav-link').forEach(link => { link.classList.remove('active');});
        document.querySelector('.nav-link[data-page="admin"]').classList.add('active');
        this.loadAdminData();
    }

    showTab(tabId) {
        document.querySelectorAll('.tab-pane').forEach(pane => { pane.classList.remove('active');});
        document.getElementById(`${tabId}-tab`).classList.add('active');
        document.querySelectorAll('.tab-link').forEach(link => { link.classList.remove('active');});
        document.querySelector(`.tab-link[data-tab="${tabId}"]`).classList.add('active');
    }

    formatCurrency(amount){ return new Intl.NumberFormat('en-US', { style: 'currency',currency: 'USD'}).format(amount);}

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

    formatLoanStatus(status){ return status.replace('_', ' ').split(' ').map(word => word.charAt(0).toUpperCase() + word.slice(1)).join(' ');}
}

const adminComponent = new AdminComponent();