class ProfileComponent {
    constructor() {
        this.userData = null;
        this.initEventListeners();
    }

    initEventListeners() {
        // profile form
        document.getElementById('profile-form').addEventListener('submit',
            this.handleUpdateProfile.bind(this));
    }

    /**
     * set user data
     * @param {Object} userData - cur user data
     */
    setUserData(userData) {
        this.userData = userData;
        this.updateProfileUI();
    }

    /**
     * upd profile ui
     */
    updateProfileUI() {
        if (!this.userData) return;

        // populate profile form
        document.getElementById('profile-username').value = this.userData.username;
        document.getElementById('profile-fullname').value = this.userData.full_name;
        document.getElementById('profile-email').value = this.userData.email;
        document.getElementById('profile-password').value = '';

        // clear error msg
        document.getElementById('profile-error').style.display = 'none';
    }

    /**
     * handle upd profile form submit
     * @param {Event} e - form submit event
     */
    async handleUpdateProfile(e) {
        e.preventDefault();

        const profileData = {
            full_name: document.getElementById('profile-fullname').value,
            email: document.getElementById('profile-email').value
        };

        const password = document.getElementById('profile-password').value;
        if (password) {
            profileData.password = password;
        }

        try {
            await api.updateProfile(profileData);

            // upd user state
            const userData = await api.getProfile();
            this.userData = userData;

            // upd ui
            this.updateProfileUI();

            // upd user name in header
            document.getElementById('user-fullname').textContent = this.userData.full_name;

            // show success msg
            alert('profile upd successfully');
        } catch (error) {
            const errorElem = document.getElementById('profile-error');
            errorElem.textContent = error.message || 'failed to upd profile';
            errorElem.style.display = 'block';
        }
    }
}

const profileComponent = new ProfileComponent();