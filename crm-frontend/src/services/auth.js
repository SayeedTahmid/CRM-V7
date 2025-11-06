import { getAuth } from 'firebase/auth';

/**
 * Small client-side helper to read Firebase ID token claims.
 * We use this to detect the current user's role/tenant for UI decisions.
 */

export async function getIdTokenResult() {
  const auth = getAuth();
  const user = auth.currentUser;
  if (!user) return null;
  try {
    return await user.getIdTokenResult(true);
  } catch (err) {
    console.warn('Failed to get ID token result', err);
    return null;
  }
}

export async function getCurrentUserClaims() {
  const tokenResult = await getIdTokenResult();
  return tokenResult ? tokenResult.claims || {} : {};
}

export async function getCurrentUserRole() {
  const claims = await getCurrentUserClaims();
  return claims.role || null;
}

export async function getCurrentUserTenant() {
  const claims = await getCurrentUserClaims();
  return claims.tenant || null;
}
