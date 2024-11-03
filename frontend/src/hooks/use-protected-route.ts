import { useEffect } from 'react';
import { AuthStore } from '@/stores/auth.store';

export const useProtectedRoute = () => {
    const { isAuthenticated, isTokenValid, handleUnauthorized } = AuthStore();
    
    useEffect(() => {
        if (!isAuthenticated || !isTokenValid()) {
            handleUnauthorized();
        }
    }, [isAuthenticated]);

    return { isAuthenticated };
};