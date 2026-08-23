export {
  type ProfileSession,
  getSession,
  setSession,
  clearSession,
  isSessionValid,
} from "../profile/session";

/** Back-compat alias while migrating imports. */
export type CharacterSession = ProfileSession;
