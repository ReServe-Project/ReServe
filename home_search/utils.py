# home_search/utils.py
def _is_role_string(x) -> bool:
    return isinstance(x, str) and x.strip().lower() in {"instructor", "instr", "teacher"}

# home_search/utils.py
def is_instructor(user):
    if not getattr(user, "is_authenticated", False):
        return False

    # 1) user.role (string field on your accounts.User)
    role = getattr(user, "role", None)
    if role and str(role).lower() == "instructor":
        return True

    # 2) related profile-like objects (if any exist in your project)
    for attr in ("profile", "userprofile", "account", "accounts_profile"):
        prof = getattr(user, attr, None)
        if prof:
            r = getattr(prof, "role", None)
            if r and str(r).lower() == "instructor":
                return True

    # 3) Django group fallback
    try:
        if user.groups.filter(name__iexact="instructor").exists():
            return True
    except Exception:
        pass

    return False






