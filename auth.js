// Shared Local Storage Auth Utilities
(function () {
    'use strict';

    function safeParse(str) {
        try { return JSON.parse(str); } catch (e) { return null; }
    }

    function saveUserData(user) {
        if (!user || typeof user !== 'object') return false;
        // ensure base fields exist
        user.fullName = user.fullName || ((user.firstName || '') + ' ' + (user.lastName || '')).trim();
        user.registeredAt = user.registeredAt || new Date().toISOString();
        localStorage.setItem('user', JSON.stringify(user));
        return true;
    }

    function getUserData() {
        // Migrate legacy keys if present
        const raw = localStorage.getItem('user');
        if (raw) {
            const parsed = safeParse(raw);
            if (parsed) return parsed;
            // corrupted -> remove and continue
            localStorage.removeItem('user');
        }

        // Legacy migration: detect old keys used by earlier pages
        const legacyEmail = localStorage.getItem('userEmail');
        if (legacyEmail) {
            const user = {
                fullName: localStorage.getItem('userName') || '',
                firstName: localStorage.getItem('userFirstName') || '',
                lastName: localStorage.getItem('userLastName') || '',
                username: localStorage.getItem('userName') ? slugify(localStorage.getItem('userName')) : (localStorage.getItem('userName') || ''),
                email: localStorage.getItem('userEmail') || '',
                phone: localStorage.getItem('userPhone') || '',
                address: localStorage.getItem('userAddress') || '',
                city: localStorage.getItem('userCity') || '',
                country: localStorage.getItem('userCountry') || '',
                bio: localStorage.getItem('userBio') || '',
                password: localStorage.getItem('userPassword') || '',
                registeredAt: localStorage.getItem('userRegisteredAt') || new Date().toISOString(),
                role: localStorage.getItem('userRole') || 'user'
            };
            saveUserData(user);
            return user;
        }

        return null;
    }

    function slugify(str) {
        if (!str) return '';
        return String(str).toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '');
    }

    function validateEmail(email) {
        return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email || '');
    }

    function passwordStrongEnough(pw) {
        if (!pw || pw.length < 8) return false;
        // basic checks
        const checks = [/[A-Z]/.test(pw), /[0-9]/.test(pw), /[^A-Za-z0-9]/.test(pw)];
        return checks.filter(Boolean).length >= 1; // at least one of these plus length
    }

    function loginUser(identifier, password, remember) {
        const user = getUserData();
        if (!user) return { ok: false, msg: 'No account found. Please register.' };
        const id = (identifier || '').trim();
        if (!id || !password) return { ok: false, msg: 'Missing credentials.' };
        const matches = (id === user.email) || (id === user.username);
        if (matches && password === user.password) {
            localStorage.setItem('isLoggedIn', 'true');
            localStorage.setItem('lastLoginAt', new Date().toISOString());
            if (remember) localStorage.setItem('rememberedEmail', id);
            return { ok: true };
        }
        return { ok: false, msg: 'Invalid email/username or password.' };
    }

    function logoutUser() {
        localStorage.setItem('isLoggedIn', 'false');
        localStorage.removeItem('lastLoginAt');
        return true;
    }

    function updateProfile(updates) {
        const user = getUserData();
        if (!user) return { ok: false, msg: 'No user to update.' };
        const merged = Object.assign({}, user, updates || {});
        // keep password if not provided
        if (!updates || !updates.password) merged.password = user.password;
        // recompute fullName
        merged.firstName = merged.firstName || '';
        merged.lastName = merged.lastName || '';
        merged.fullName = (merged.firstName + ' ' + merged.lastName).trim() || merged.fullName;
        saveUserData(merged);
        return { ok: true, user: merged };
    }

    function changePassword(current, next) {
        const user = getUserData();
        if (!user) return { ok: false, msg: 'No user found.' };
        if (user.password !== current) return { ok: false, msg: 'Current password is incorrect.' };
        if (!passwordStrongEnough(next)) return { ok: false, msg: 'New password does not meet strength requirements.' };
        user.password = next;
        saveUserData(user);
        return { ok: true };
    }

    // Expose functions
    window.auth = {
        saveUserData,
        getUserData,
        loginUser,
        logoutUser,
        updateProfile,
        changePassword,
        validateEmail,
        passwordStrongEnough
    };

})();
