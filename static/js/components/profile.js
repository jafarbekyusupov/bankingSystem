class ProfileComponent {
    constructor(){ this.userData = null; this.initEventListeners();}

    initEventListeners(){ document.getElementById('profile-form').addEventListener('submit', this.handleUpdateProfile.bind(this));}
    setUserData(userData){ this.userData = userData; this.updateProfileUI();}

    updateProfileUI(){
        if(!this.userData){ return;}
        document.getElementById('profile-username').value = this.userData.username;
        document.getElementById('profile-fullname').value = this.userData.full_name;
        document.getElementById('profile-email').value = this.userData.email;
        document.getElementById('profile-password').value = '';
        document.getElementById('profile-error').style.display = 'none';
    }

    async handleUpdateProfile(e) {
        e.preventDefault();
        const profileData ={ full_name: document.getElementById('profile-fullname').value,  email: document.getElementById('profile-email').value};
        const pwd = document.getElementById('profile-password').value;
        if(pwd){ profileData.password = pwd;}
        try {
            await api.updateProfile(profileData);
            const userData = await api.getProfile();
            this.userData = userData; // upd user state

            this.updateProfileUI();
            document.getElementById('user-fullname').textContent = this.userData.full_name;
            alert('profile upd successfully');
        } catch(error){
            const errorElem = document.getElementById('profile-error');
            errorElem.textContent = error.message || 'failed to upd profile';
            errorElem.style.display = 'block';
        }
    }
}

const profileComponent = new ProfileComponent();